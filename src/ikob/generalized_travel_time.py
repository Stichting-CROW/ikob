import logging

import numpy as np

import ikob.utils as utils
from ikob.chain_generator import chain_generator
from ikob.configuration_definition import TvomType
from ikob.datasource import (
    DataKey,
    DataSource,
    DataType,
    SegsSource,
    SkimsSource,
    read_csv_from_config,
    read_parking_times,
)
from ikob.utils import IKOB_INFINITE

logger = logging.getLogger(__name__)


def generalized_travel_time(config) -> DataSource:
    """
    Compute generalized (experienced) travel time from time and costs.

    Corresponds to section D1 in IKOB-algorithm.pdf
    """

    logger.info("Starting step: Compute generalized travel time from time and costs.")

    project_config = config["project"]
    skims_config = config["skims"]
    tvom_config = config["TVOM"]
    advanced_config = config["geavanceerd"]
    ketens_config = config["ketens"]

    regime = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]
    motive_tvom = project_config["motief"]["TVOM"]
    chains = ketens_config["chains"]["gebruiken"]
    ketens_config["bestemmingslijst"]["gebruiken"]
    hub_name = ketens_config["chains"]["naam hub"]
    pt_cost_file = skims_config["OV kostenbestand"]["gebruiken"]
    tvom_dict = tvom_config[TvomType.WORK] if motive_tvom == TvomType.WORK else tvom_config[TvomType.OTHER]
    var_fossil = skims_config["Kosten auto fossiele brandstof"]["variabele kosten"]
    road_pricing_fossil = skims_config["Kosten auto fossiele brandstof"]["kmheffing"]
    var_electric = skims_config["Kosten elektrische auto"]["variabele kosten"]
    road_pricing_electric = skims_config["Kosten elektrische auto"]["kmheffing"]
    costs_no_car = skims_config["varkostenga"]
    time_costs_no_car = skims_config["tijdkostenga"]
    part_of_day = skims_config["dagsoort"]
    kind_no_car = ["GeenAuto", "GeenRijbewijs"]
    pt_km_price = skims_config["OV kosten"]["kmkosten"]
    starting_rate = skims_config["OV kosten"]["starttarief"]
    additional_costs = advanced_config["additionele_kosten"]["gebruiken"]
    parking_costs = advanced_config["parkeerkosten"]["gebruiken"]
    pricecap = skims_config["pricecap"]["gebruiken"]
    pricecap_value = skims_config["pricecap"]["getal"]
    bike_cost_euro_per_km = skims_config["bike_cost_ct_per_km"] / 100
    parking_times = read_parking_times(config)

    if parking_costs:
        parking_cost_array = read_csv_from_config(config, key="geavanceerd", id="parkeerkosten")
    else:
        parking_cost_array = utils.zeros(len(parking_times))

    if additional_costs:
        additional_cost_matrix = read_csv_from_config(config, key="geavanceerd", id="additionele_kosten")
    else:
        additional_cost_matrix = np.zeros((len(parking_times), len(parking_times)))

    income_levels = ["laag", "middellaag", "middelhoog", "hoog"]
    pt_km_price = pt_km_price / 100
    starting_rate = starting_rate / 100
    var_fossil = var_fossil / 100
    var_electric = var_electric / 100
    road_pricing_fossil = road_pricing_fossil / 100
    road_pricing_electric = road_pricing_electric / 100
    fuel_kinds = ["fossiel", "elektrisch"]

    SegsSource(config)

    skims_dir = config["project"]["paden"]["skims_directory"]
    skims_reader = SkimsSource(skims_dir)

    generalized_travel_time = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME)

    if chains:
        chain_generator(generalized_travel_time, config)

    num_zones = None
    for pod in part_of_day:
        car_time_matrix = skims_reader.read("Auto_Tijd", pod)
        car_distance_matrix = skims_reader.read("Auto_Afstand", pod)
        bike_time_matrix = skims_reader.read("Fiets_Tijd", pod)
        # Use a default speed to compute distance from time if distance is not directly available
        default_speed_km_p_minute = 15 / 60
        bike_distance_matrix = skims_reader.read(
            "Fiets_Afstand", pod, default=(bike_time_matrix * default_speed_km_p_minute)
        )
        pt_time_matrix = skims_reader.read("OV_Tijd", pod)

        # Can be any of the matrices, this is checked in validate.py
        num_zones = len(pt_time_matrix)

        if pt_cost_file:
            pt_cost_matrix = skims_reader.read("OV_Kosten", pod)
        else:
            pt_distance_matrix = skims_reader.read("OV_Afstand", pod)
            n = len(pt_time_matrix)
            pt_cost_matrix = np.zeros((n, n))
            pt_cost_matrix = utils.costs_public_transport(
                pt_distance_matrix, pt_km_price, starting_rate, pricecap, pricecap_value
            )

        # Bike generalized travel time:
        for income_level in income_levels:
            tvom_factor = tvom_dict.get(income_level)

            gtr_skim = utils.compute_bike_gtt(
                bike_time_matrix, bike_distance_matrix, bike_cost_euro_per_km, tvom_factor
            )

            key = DataKey(
                id="Fiets",
                part_of_day=pod,
                regime=regime,
                motive=motive_name,
                income=income_level,
                header=DataKey.zone_header(num_zones),
                index=DataKey.zone_index(num_zones),
            )
            generalized_travel_time.set(key, gtr_skim.copy())

        gtr_skim = np.zeros((num_zones, num_zones))
        for income_level in income_levels:
            tvom_factor = tvom_dict.get(income_level)
            # Car generalized travel time:
            for fuel_kind in fuel_kinds:
                if fuel_kind == "fossiel":
                    var_car_rate = var_fossil
                    road_pricing = road_pricing_fossil
                else:
                    var_car_rate = var_electric
                    road_pricing = road_pricing_electric

                gtr_skim = utils.compute_car_gtt(
                    car_time=car_time_matrix,
                    car_dist=car_distance_matrix,
                    var_rate=var_car_rate,
                    road_pricing=road_pricing,
                    tvom_factor=tvom_factor,
                    additional_costs_eurocent=additional_cost_matrix,
                    parking_times_array=np.array(parking_times),
                    parking_costs_array_eurocent=parking_cost_array,
                )
                if chains:
                    key = DataKey(
                        id=f"Pplusfiets_{fuel_kind}",
                        part_of_day=pod,
                        income=income_level,
                        hub_name=hub_name,
                        motive=motive_name,
                        regime=regime,
                    )
                    gtr_park_and_bike_skim = generalized_travel_time.get(key)
                    bestskim = np.minimum(gtr_skim, gtr_park_and_bike_skim)
                    key = DataKey(
                        id=f"PplusR_{fuel_kind}",
                        part_of_day=pod,
                        income=income_level,
                        hub_name=hub_name,
                        motive=motive_name,
                        regime=regime,
                    )
                    gtr_park_and_ride_skim = generalized_travel_time.get(key)
                    gtr_skim = np.minimum(bestskim, gtr_park_and_ride_skim)

                key = DataKey(
                    id=f"Auto_{fuel_kind}",
                    part_of_day=pod,
                    income=income_level,
                    regime=regime,
                    motive=motive_name,
                    header=DataKey.zone_header(num_zones),
                    index=DataKey.zone_index(num_zones),
                )
                generalized_travel_time.set(key, gtr_skim.copy())

            # Then PT, pt costs are (optionally) computed from travel times and skims_config["OV kosten"]
            # This does tot strictly follow the documentation in IKOB-algorithm.pdf
            tvom_factor = tvom_dict.get(income_level)
            gtr_skim = utils.compute_pt_gtt(pt_time_matrix, pt_cost_matrix, tvom_factor)
            key = DataKey(
                id="OV",
                part_of_day=pod,
                income=income_level,
                motive=motive_name,
                regime=regime,
                header=DataKey.zone_header(num_zones),
                index=DataKey.zone_index(num_zones),
            )
            generalized_travel_time.set(key, gtr_skim.copy())

            # Dan geen auto (rijbewijs)
            for kind in kind_no_car:
                gtr_skim.fill(IKOB_INFINITE)
                tvom_factor = tvom_dict.get(income_level)
                for i in range(num_zones):
                    for j in range(num_zones):
                        total_time = car_time_matrix[i][j]
                        total_cost = car_time_matrix[i][j] * time_costs_no_car.get(kind) + car_distance_matrix[i][j] * (
                            costs_no_car.get(kind) + road_pricing_electric
                        )
                        gtr_skim[i][j] = total_time + tvom_factor * total_cost

                key = DataKey(
                    id=f"{kind}",
                    part_of_day=pod,
                    income=income_level,
                    motive=motive_name,
                    regime=regime,
                    header=DataKey.zone_header(num_zones),
                    index=DataKey.zone_index(num_zones),
                )
                generalized_travel_time.set(key, gtr_skim.copy())

            # Free car (no variable costs compared to car) generalized travel time:
            gtr_skim.fill(0)
            tvom_factor = tvom_dict.get(income_level)
            for i in range(num_zones):
                for j in range(num_zones):
                    total_time = car_time_matrix[i][j] + parking_times[i][0] + parking_times[j][1]
                    if additional_costs:
                        gtr_skim[i][j] = total_time + tvom_factor * (
                            car_distance_matrix[i][j] * road_pricing_electric
                            + additional_cost_matrix[i][j] / 100
                            + parking_cost_array[j] / 100
                        )
                    else:
                        gtr_skim[i][j] = total_time + tvom_factor * (
                            car_distance_matrix[i][j] * road_pricing_electric + parking_cost_array[j] / 100
                        )
            key = DataKey(
                id="GratisAuto",
                part_of_day=pod,
                income=income_level,
                motive=motive_name,
                regime=regime,
                header=DataKey.zone_header(num_zones),
                index=DataKey.zone_index(num_zones),
            )
            generalized_travel_time.set(key, gtr_skim.copy())

            # Free PT generalized travel time:
            gtr_skim = np.where(pt_time_matrix > 0.5, pt_time_matrix, IKOB_INFINITE)
            key = DataKey(
                id="GratisOV",
                part_of_day=pod,
                motive=motive_name,
                regime=regime,
                header=DataKey.zone_header(num_zones),
                index=DataKey.zone_index(num_zones),
            )
            generalized_travel_time.set(key, gtr_skim.copy())

    return generalized_travel_time
