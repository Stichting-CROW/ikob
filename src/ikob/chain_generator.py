import logging

import numpy as np
import numpy.typing as npt

from ikob import utils
from ikob.configuration_definition import TvomType
from ikob.datasource import DataKey, DataSource, SkimsSource, read_csv_from_config, read_parking_times
from ikob.utils import IKOB_INFINITE, costs_public_transport

logger = logging.getLogger(__name__)


class Hubs:
    def __init__(self, hubs: npt.NDArray):
        self.validate(hubs)
        self.zone_indices: npt.NDArray[np.integer] = hubs[:, 0].astype(int) - 1  # Zones in config use 1 based indexing
        self.hub_costs_cents: npt.NDArray[np.floating] = hubs[:, 1]
        self.pt_transfer_times: npt.NDArray[np.floating] = hubs[:, 2]
        self.bike_transfer_times: npt.NDArray[np.floating] = hubs[:, 3]
        self.pay_for_pt: npt.NDArray[np.bool_] = hubs[:, 4].astype(bool)
        self.num_hubs: int = len(hubs)

    @staticmethod
    def validate(hub_content_raw):
        valid = True

        if hub_content_raw.shape[0] == 0:
            logger.warning("Hub data is empty.")
            valid = False

        if not hub_content_raw.shape[1] == 5:
            logger.warning(f"Hub data should have 5 columns but has {hub_content_raw.shape[1]}.")
            valid = False

        if not all([zone.is_integer() for zone in hub_content_raw[:, 0]]):
            logger.warning("The first column of the hub data (the zone numbers) should contain only integers.")
            valid = False

        if not (
            all([pay_for_pt.is_integer() for pay_for_pt in hub_content_raw[:, 4]])
            and np.all(np.logical_or(hub_content_raw[:, 4] == 1, hub_content_raw[:, 4] == 0))
        ):
            logger.warning("The fourth column of the hub data (wether to pay for pt) should contain either 0 or 1.")
            valid = False

        return valid


def compute_chain_travel_time(
    hubs: Hubs,
    car_time: npt.NDArray,
    car_dist: npt.NDArray,
    bike_time: npt.NDArray,
    bike_dist: npt.NDArray,
    pt_time: npt.NDArray,
    pt_cost: npt.NDArray,
    tvom_factor: float,
    var_car_rate: float,
    road_pricing: float,
    bike_cost_euro_per_km: float,
    additional_costs: npt.NDArray,
    parking_times: npt.NDArray,
    destination_list: npt.NDArray[np.integer],
) -> tuple[npt.NDArray, npt.NDArray]:
    """Compute Park+Bike and Park+Ride generalized travel time skims.

    For each hub, vectorized over all origin-destination pairs. Returns the
    element-wise minimum across all hubs.
    """
    num_zones = len(car_time)

    # Only compute chain travel times for zones in the destination_list.
    # This allows a user to investigate hub locations to improve travel times to only a subset of the total zones.
    destination_mask = np.zeros(num_zones, dtype=bool)
    destination_mask[destination_list - 1] = True  # Zones in config use 1 based indexing

    # Initialize with true infinite values to overwrite these with gtt even if those are above IKOB_INFINITE
    result_bike = np.full((num_zones, num_zones), np.inf)
    result_ride = np.full((num_zones, num_zones), np.inf)

    # Hubs have their own transfer time that includes the parking time
    hub_parking_times = parking_times.copy()
    hub_parking_times[:, 1] = 0.0

    if hubs.num_hubs == 0:
        result_bike = np.where(result_bike == np.inf, IKOB_INFINITE, result_bike)
        result_ride = np.where(result_ride == np.inf, IKOB_INFINITE, result_ride)
        return result_bike, result_ride

    hub_zones = hubs.zone_indices
    hub_costs = hubs.hub_costs_cents / 100
    change_time_bike = hubs.bike_transfer_times
    change_time_pt = hubs.pt_transfer_times
    pay_for_pt = hubs.pay_for_pt

    # Travel via a hub consist of going by car to the hub, then continuing either by bike or by pt
    car_part = (
        utils.compute_car_gtt(
            car_time=car_time,
            car_dist=car_dist,
            var_rate=var_car_rate,
            road_pricing=road_pricing,
            tvom_factor=tvom_factor,
            additional_costs_eurocent=additional_costs,
            parking_costs_array_eurocent=np.zeros(num_zones),  # parking costs are in the hub_cost
            parking_times_array=hub_parking_times,
        )[:, hub_zones]
        + hub_costs[np.newaxis, :] * tvom_factor
    )
    bike_part = utils.compute_bike_gtt(bike_time, bike_dist, bike_cost_euro_per_km, tvom_factor)[hub_zones, :]
    pt_part = utils.compute_pt_gtt(
        pt_time[hub_zones, :], pt_cost[hub_zones, :] * pay_for_pt[:, np.newaxis], tvom_factor
    )

    # Car from origin to hub, then some change time at the hub, then bike / pt from hub destination
    p_bike = (
        car_part[:, :, np.newaxis]
        + change_time_bike[np.newaxis, :, np.newaxis]
        + bike_part[np.newaxis, :, destination_mask]
    )
    p_ride = (
        car_part[:, :, np.newaxis]
        + change_time_pt[np.newaxis, :, np.newaxis]
        + pt_part[np.newaxis, :, destination_mask]
    )

    result_bike[:, destination_mask] = np.min(p_bike, axis=1)
    result_ride[:, destination_mask] = np.min(p_ride, axis=1)

    result_bike = np.where(result_bike == np.inf, IKOB_INFINITE, result_bike)
    result_ride = np.where(result_ride == np.inf, IKOB_INFINITE, result_ride)
    return result_bike, result_ride


def chain_generator(generalized_travel_time: DataSource, config: dict):
    """Generate generalized travel time skims for chains (P+R and P+Bike).

    For each origin, computes the cost of driving to each hub and then
    continuing by bike or public transport. The result for each OD pair is
    the minimum across all hubs:

        P+Bike(i,j) = min_h( car(i,h) + bike(h,j) + transfer + hub_cost )
        P+R(i,j)    = min_h( car(i,h) + PT(h,j) + transfer + PT_cost + hub_cost )

    Results are stored in ``generalized_travel_time`` so they can be picked
    up by the main generalized travel time computation.
    """
    logger.info("Starting step: Compute chain (P+R / P+Bike) generalized travel times.")

    project_config = config["project"]
    skims_config = config["skims"]
    tvom_config = config["TVOM"]
    ketens_config = config["ketens"]

    regime = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]
    motive_tvom = project_config["motief"]["TVOM"]
    hub_name = ketens_config["chains"]["naam hub"]
    tvom_dict = tvom_config[TvomType.WORK] if motive_tvom == TvomType.WORK else tvom_config[TvomType.OTHER]

    var_fossil = skims_config["Kosten auto fossiele brandstof"]["variabele kosten"] / 100
    road_pricing_fossil = skims_config["Kosten auto fossiele brandstof"]["kmheffing"] / 100
    var_electric = skims_config["Kosten elektrische auto"]["variabele kosten"] / 100
    road_pricing_electric = skims_config["Kosten elektrische auto"]["kmheffing"] / 100
    pt_km_price = skims_config["OV kosten"]["kmkosten"] / 100
    starting_rate = skims_config["OV kosten"]["starttarief"] / 100
    pt_cost_file = skims_config["OV kostenbestand"]["gebruiken"]
    pricecap = skims_config["pricecap"]["gebruiken"]
    pricecap_value = skims_config["pricecap"]["getal"]
    bike_cost_euro_per_km = skims_config["bike_cost_ct_per_km"] / 100
    part_of_day = skims_config["dagsoort"]

    income_levels = ["laag", "middellaag", "middelhoog", "hoog"]
    fuel_kinds = ["fossiel", "elektrisch"]

    skims_dir = config["project"]["paden"]["skims_directory"]
    skims_reader = SkimsSource(skims_dir)

    parking_times = read_parking_times(config)
    num_zones = len(parking_times)
    if config["geavanceerd"]["additionele_kosten"]["gebruiken"]:
        additional_cost_matrix = read_csv_from_config(config, key="geavanceerd", id="additionele_kosten")
    else:
        additional_cost_matrix = np.zeros((num_zones, num_zones))

    hubs = Hubs(read_csv_from_config(config, key="ketens", id="chains", has_index_column=False))
    if hubs.num_hubs == 0:
        logger.warning("Chain generator called but no hubs found in file at config['ketens']['chains'].")
    if config["ketens"]["bestemmingslijst"]["gebruiken"]:
        destination_list = read_csv_from_config(
            config, key="ketens", id="bestemmingslijst", type_caster=int, has_index_column=False
        )
    else:
        destination_list = np.linspace(1, num_zones, num_zones, dtype=int)

    for pod in part_of_day:
        car_time = skims_reader.read("Auto_Tijd", pod)
        car_dist = skims_reader.read("Auto_Afstand", pod)
        bike_time = skims_reader.read("Fiets_Tijd", pod)
        default_speed_km_p_minute = 15 / 60
        bike_dist = skims_reader.read("Fiets_Afstand", pod, default=(bike_time * default_speed_km_p_minute))
        pt_time = skims_reader.read("OV_Tijd", pod)

        if pt_cost_file:
            pt_cost = skims_reader.read("OV_Kosten", pod)
        else:
            pt_dist = skims_reader.read("OV_Afstand", pod)
            pt_cost = costs_public_transport(pt_dist, pt_km_price, starting_rate, pricecap, pricecap_value)

        for income_level in income_levels:
            tvom_factor = tvom_dict.get(income_level)

            for fuel_kind in fuel_kinds:
                if fuel_kind == "fossiel":
                    var_car_rate = var_fossil
                    road_pricing = road_pricing_fossil
                else:
                    var_car_rate = var_electric
                    road_pricing = road_pricing_electric

                result_bike, result_ride = compute_chain_travel_time(
                    hubs=hubs,
                    car_time=car_time,
                    car_dist=car_dist,
                    bike_time=bike_time,
                    bike_dist=bike_dist,
                    pt_time=pt_time,
                    pt_cost=pt_cost,
                    tvom_factor=tvom_factor,
                    var_car_rate=var_car_rate,
                    road_pricing=road_pricing,
                    bike_cost_euro_per_km=bike_cost_euro_per_km,
                    additional_costs=additional_cost_matrix,
                    parking_times=np.array(parking_times),
                    destination_list=destination_list,
                )

                key = DataKey(
                    id=f"Pplusfiets_{fuel_kind}",
                    part_of_day=pod,
                    income=income_level,
                    hub_name=hub_name,
                    motive=motive_name,
                    regime=regime,
                    index=DataKey.zone_index(len(result_bike)),
                    header=DataKey.zone_header(len(result_bike)),
                )
                generalized_travel_time.set(key, result_bike)

                key = DataKey(
                    id=f"PplusR_{fuel_kind}",
                    part_of_day=pod,
                    income=income_level,
                    hub_name=hub_name,
                    motive=motive_name,
                    regime=regime,
                    index=DataKey.zone_index(len(result_ride)),
                    header=DataKey.zone_header(len(result_ride)),
                )
                generalized_travel_time.set(key, result_ride)
