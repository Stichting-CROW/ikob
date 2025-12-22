import logging

import numpy as np

import ikob.utils as utils
from ikob.datasource import (
    DataKey,
    DataSource,
    DataType,
    SegsSource,
    SkimsSource,
    read_csv_from_config,
    read_parking_times,
)
from ikob.gui.configuration_definition import (
    IkobConfig,
    IncomeGroup,
    NoCarKind,
)

logger = logging.getLogger(__name__)


def costs_public_transport(distance, pt_km_price, starting_rate, pricecap, pricecap_value):
    distance = np.where(distance < 0, 0, distance)
    distance = starting_rate + distance * pt_km_price

    if pricecap:
        np.clip(distance, None, pricecap_value, out=distance)

    return distance


def generalized_travel_time(config: IkobConfig) -> DataSource:
    """See section D1 of the algorithm documentation"""
    logger.info("Starting step: Compute generalized travel time from time and costs.")

    project_config = config.project
    skims_config = config.skims
    tvom_config = config.tvom
    advanced_config = config.advanced
    ketens_config = config.chains_and_hubs

    regime = project_config.pricing_regime
    motives = project_config.motives
    chains = ketens_config.use
    hub_collection = ketens_config.hub_collection
    pt_cost_file = skims_config.use_pt_costs_file
    tvom_work = tvom_config.work_tvom
    tvom_other = tvom_config.other_tvom
    var_fossil = skims_config.ice_costs.cent_per_km
    road_pricing_fossil = skims_config.ice_costs.km_charge
    var_electric = skims_config.ev_costs.cent_per_km
    road_pricing_electric = skims_config.ev_costs.km_charge
    costs_no_car = skims_config.no_car_costs.no_car_euro_per_km
    time_costs_no_car = skims_config.no_car_costs.no_car_euro_per_min
    costs_no_license = skims_config.no_car_costs.no_license_euro_per_km
    time_costs_no_license = skims_config.no_car_costs.no_license_euro_per_min

    parts_of_day = skims_config.parts_of_day
    kind_no_car = list(NoCarKind)
    pt_km_price = skims_config.pt_costs.cent_per_km
    starting_rate = skims_config.pt_costs.base_fare_cent
    use_additional_costs = advanced_config.additional_costs_cents.use
    use_parking_costs = advanced_config.parking_costs_cents.use
    pricecap = skims_config.pt_costs.use_price_cap
    pricecap_value = skims_config.pt_costs.price_cap
    try:
        parking_times_temporary = read_csv_from_config(config.skims.parking_search_time_file)
    except Exception as e:
        logger.error(f"Unable to read parking search time file from path '{config.skims.parking_search_time_file}'.")
        raise e

    if use_parking_costs:
        parking_cost_array = read_csv_from_config(config.advanced.parking_costs_cents.file)
    else:
        parking_cost_array = utils.zeros(len(parking_times_temporary))

    if use_additional_costs:
        additional_cost_matrix = read_csv_from_config(config.advanced.additional_costs_cents.file)
    else:
        additional_cost_matrix = np.zeros((len(parking_cost_array), len(parking_cost_array)))

    income_levels = list(IncomeGroup)
    pt_km_price = pt_km_price / 100
    starting_rate = starting_rate / 100
    var_fossil = var_fossil / 100
    var_electric = var_electric / 100
    road_pricing_fossil = road_pricing_fossil / 100
    road_pricing_electric = road_pricing_electric / 100
    fuel_kinds = ["fossiel", "elektrisch"]

    SegsSource(config)
    parking_times = read_parking_times(config)

    skims_dir = config.project.paths.skims_directory
    skims_reader = SkimsSource(skims_dir)

    generalized_travel_time = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME)

    num_zones = None
    for motive in motives:
        tvom = tvom_work if motive == "werk" else tvom_other
        for pod in parts_of_day:
            car_time_matrix = skims_reader.read("Auto_Tijd", pod)
            car_distance_matrix = skims_reader.read("Auto_Afstand", pod)
            bike_time_matrix = skims_reader.read("Fiets_Tijd", pod)
            pt_time_matrix = skims_reader.read("OV_Tijd", pod)

            num_zones = _check_size_assumptions(
                car_time_matrix,
                car_distance_matrix,
                bike_time_matrix,
                pt_time_matrix,
                parking_cost_array,
                parking_times,
                old_num_zones=num_zones,
            )

            if pt_cost_file:
                pt_cost_matrix = skims_reader.read("OV_Kosten", pod)
            else:
                pt_distance_matrix = skims_reader.read("OV_Afstand", pod)
                n = len(pt_time_matrix)
                pt_cost_matrix = np.zeros((n, n))
                pt_cost_matrix = costs_public_transport(
                    pt_distance_matrix, pt_km_price, starting_rate, pricecap, pricecap_value
                )

            # Eerst de fiets:
            gtr_skim = np.where(bike_time_matrix < 180, bike_time_matrix, 9999)

            key = DataKey(id="Fiets", part_of_day=pod, regime=regime, motive=motive)
            generalized_travel_time.set(key, gtr_skim.copy())

            gtr_skim = np.zeros((num_zones, num_zones))
            for income_level in income_levels:
                factor = tvom.get_tvom(income_level)

                for fuel_kind in fuel_kinds:
                    if fuel_kind == "fossiel":
                        var_car_rate = var_fossil
                        road_pricing = road_pricing_fossil
                    else:
                        var_car_rate = var_electric
                        road_pricing = road_pricing_electric
                    for i in range(num_zones):
                        for j in range(num_zones):
                            total_time = car_time_matrix[i][j] + parking_times[i][1] + parking_times[j][2]
                            gtr_skim[i][j] = total_time + factor * (
                                car_distance_matrix[i][j] * (var_car_rate + road_pricing)
                                + additional_cost_matrix[i][j] / 100
                                + parking_cost_array[j] / 100
                            )
                    if chains:
                        key = DataKey(
                            id=f"Pplusfiets_{fuel_kind}",
                            part_of_day=pod,
                            income=income_level,
                            hub_name=hub_collection,
                            motive=motive,
                            regime=regime,
                        )
                        gtr_park_and_bike_skim = generalized_travel_time.get(key)
                        bestskim = np.minimum(gtr_skim, gtr_park_and_bike_skim)
                        key = DataKey(
                            id=f"PplusR_{fuel_kind}",
                            part_of_day=pod,
                            income=income_level,
                            hub_name=hub_collection,
                            motive=motive,
                            regime=regime,
                        )
                        gtr_park_and_ride_skim = generalized_travel_time.get(key)
                        gtr_skim = np.minimum(bestskim, gtr_park_and_ride_skim)

                    key = DataKey(
                        id=f"Auto_{fuel_kind}", part_of_day=pod, income=income_level, regime=regime, motive=motive
                    )
                    generalized_travel_time.set(key, gtr_skim.copy())

                # Dan het OV
                factor = tvom.get_tvom(income_level)
                gtr_skim = np.where(pt_time_matrix > 0.5, pt_time_matrix + factor * pt_cost_matrix, 9999)
                key = DataKey(id="OV", part_of_day=pod, income=income_level, motive=motive, regime=regime)
                generalized_travel_time.set(key, gtr_skim.copy())

                # Dan geen auto (rijbewijs)
                for kind in kind_no_car:
                    gtr_skim.fill(99999)
                    factor = tvom.get_tvom(income_level)
                    time_costs_no_car = time_costs_no_car if kind == NoCarKind.NO_CAR else time_costs_no_license
                    costs_no_car = costs_no_car if kind == NoCarKind.NO_CAR else costs_no_license
                    for i in range(num_zones):
                        for j in range(num_zones):
                            total_time = car_time_matrix[i][j]
                            total_cost = car_time_matrix[i][j] * time_costs_no_car + car_distance_matrix[i][j] * (
                                costs_no_car + road_pricing
                            )
                            gtr_skim[i][j] = total_time + factor * total_cost

                    key = DataKey(id=f"{kind}", part_of_day=pod, income=income_level, motive=motive, regime=regime)
                    generalized_travel_time.set(key, gtr_skim.copy())

                # GratisAuto
                for income_level in income_levels:
                    gtr_skim.fill(0)
                    factor = tvom.get_tvom(income_level)
                    for i in range(num_zones):
                        for j in range(num_zones):
                            total_time = car_time_matrix[i][j] + parking_times[i][1] + parking_times[j][2]
                            gtr_skim[i][j] = total_time + factor * (
                                car_distance_matrix[i][j] * road_pricing
                                + additional_cost_matrix[i][j] / 100
                                + parking_cost_array[j] / 100
                            )
                    key = DataKey(id="GratisAuto", part_of_day=pod, income=income_level, motive=motive, regime=regime)
                    generalized_travel_time.set(key, gtr_skim.copy())

                # GratisOV
                gtr_skim = np.where(pt_time_matrix > 0.5, pt_time_matrix, 9999)
                key = DataKey(id="GratisOV", part_of_day=pod, motive=motive, regime=regime)
                generalized_travel_time.set(key, gtr_skim.copy())

    return generalized_travel_time


def _check_size_assumptions(
    car_time_matrix: np.ndarray,
    car_distance_matrix: np.ndarray,
    bike_time_matrix: np.ndarray,
    pt_time_matrix: np.ndarray,
    parking_cost_array: np.ndarray,
    parking_times: np.ndarray | list[list[int]],
    old_num_zones: int | None,
) -> int:
    """The travel time code expects the shapes of all these matrices to be the same, and equal to the number of zones.

    The arrays are expected to have this length"""
    assert (
        car_time_matrix.shape
        == car_distance_matrix.shape
        == bike_time_matrix.shape
        == bike_time_matrix.shape
        == pt_time_matrix.shape
        and pt_time_matrix.shape[0] == pt_time_matrix.shape[1]
    ), (
        "The travel time code expects the shapes of all these matrices to be the same, and equal to the number of zones in both dimensions"
    )
    num_zones = len(pt_time_matrix)
    assert len(parking_cost_array) == num_zones, (
        "The parking costs is expected to be of length equal to the number of zones"
    )
    assert len(parking_times) == num_zones and len(parking_times[0]) == 3, (
        "The parking times is expected to contain 3 values for each zone. (the zone, the arrival search time, the departure search time)"
    )
    if old_num_zones is not None:
        assert num_zones == old_num_zones, "The number of zones should be constant throughout generalized travel time"
    return num_zones
