import logging
from collections.abc import Callable

import numpy as np

from ikob import utils
from ikob.chain_generator import build_chain_travel_time_calculator
from ikob.configuration_definition import TvomType
from ikob.datasource import (
    DataKey,
    DataSource,
    DataType,
    SkimsSource,
    read_csv_from_config,
)
from ikob.utils import IKOB_INFINITE

logger = logging.getLogger(__name__)


def generalized_travel_time(
    config, on_travel_time: Callable | None = None, write_travel_time: bool = True
) -> DataSource | None:
    """
    Compute generalized (experienced) travel time from time and costs.

    Corresponds to section D1 in IKOB-algorithm.pdf

    If on_travel_time is provided, this method will be called when a travel time matrix is computed
    A caller can use this to immediately transform the travel time results to weight matrices
    without having to store the large travel time matrices
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

    income_levels = ["laag", "middellaag", "middelhoog", "hoog"]
    pt_km_price = pt_km_price / 100
    starting_rate = starting_rate / 100
    var_fossil = var_fossil / 100
    var_electric = var_electric / 100
    road_pricing_fossil = road_pricing_fossil / 100
    road_pricing_electric = road_pricing_electric / 100
    fuel_kinds = ["fossiel", "elektrisch"]

    skims_reader = SkimsSource(config)

    travel_time_output = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME, has_zone_id_header=True)

    def publish(key, matrix):
        if on_travel_time is not None:
            on_travel_time(key, matrix)
        if write_travel_time:
            travel_time_output.set(key, matrix)

    parking_times = skims_reader.read_parking_times()
    parking_times_array = np.asarray(parking_times, dtype=utils.FLOAT_DTYPE)

    if parking_costs:
        parking_cost_array = read_csv_from_config(config, key="geavanceerd", id="parkeerkosten")
    else:
        parking_cost_array = utils.zeros(len(parking_times))

    if additional_costs:
        additional_cost_matrix = read_csv_from_config(config, key="geavanceerd", id="additionele_kosten")
    else:
        additional_cost_matrix = np.zeros((len(parking_times), len(parking_times)), dtype=utils.FLOAT_DTYPE)

    chain_calculator = (
        build_chain_travel_time_calculator(config, parking_times_array, additional_cost_matrix) if chains else None
    )

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
            pt_cost_matrix = np.zeros((n, n), dtype=utils.FLOAT_DTYPE)
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
            )
            publish(key, gtr_skim)

        gtr_skim = np.zeros((num_zones, num_zones), dtype=utils.FLOAT_DTYPE)
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
                    parking_times_array=parking_times_array,
                    parking_costs_array_eurocent=parking_cost_array,
                )
                if chains:
                    if chain_calculator is None:
                        raise RuntimeError("Chain travel-time calculator is unavailable while chains are enabled.")
                    chain_bike, chain_ride = chain_calculator.compute(
                        car_time=car_time_matrix,
                        car_dist=car_distance_matrix,
                        bike_time=bike_time_matrix,
                        bike_dist=bike_distance_matrix,
                        pt_time=pt_time_matrix,
                        pt_cost=pt_cost_matrix,
                        tvom_factor=tvom_factor,
                        var_car_rate=var_car_rate,
                        road_pricing=road_pricing,
                        bike_cost_euro_per_km=bike_cost_euro_per_km,
                    )
                    if write_travel_time:
                        travel_time_output.set(
                            DataKey(
                                id=f"Pplusfiets_{fuel_kind}",
                                part_of_day=pod,
                                income=income_level,
                                hub_name=hub_name,
                                motive=motive_name,
                                regime=regime,
                            ),
                            chain_bike,
                        )
                        travel_time_output.set(
                            DataKey(
                                id=f"PplusR_{fuel_kind}",
                                part_of_day=pod,
                                income=income_level,
                                hub_name=hub_name,
                                motive=motive_name,
                                regime=regime,
                            ),
                            chain_ride,
                        )
                    gtr_skim = np.minimum(gtr_skim, chain_bike)
                    gtr_skim = np.minimum(gtr_skim, chain_ride)

                key = DataKey(
                    id=f"Auto_{fuel_kind}",
                    part_of_day=pod,
                    income=income_level,
                    regime=regime,
                    motive=motive_name,
                )
                publish(key, gtr_skim)

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
            )
            publish(key, gtr_skim)

            # Dan geen auto (rijbewijs)
            tvom_factor = tvom_dict.get(income_level)
            for kind in kind_no_car:
                total_cost = car_time_matrix * time_costs_no_car.get(kind) + car_distance_matrix * (
                    costs_no_car.get(kind) + road_pricing_electric
                )
                gtr_skim = car_time_matrix + tvom_factor * total_cost

                key = DataKey(
                    id=f"{kind}",
                    part_of_day=pod,
                    income=income_level,
                    motive=motive_name,
                    regime=regime,
                )
                publish(key, gtr_skim)

            # Free car (no variable costs compared to car) generalized travel time:
            tvom_factor = tvom_dict.get(income_level)
            gtr_skim = utils.compute_car_gtt(
                car_time=car_time_matrix,
                car_dist=car_distance_matrix,
                var_rate=0.0,
                road_pricing=road_pricing_electric,
                tvom_factor=tvom_factor,
                additional_costs_eurocent=additional_cost_matrix,
                parking_times_array=parking_times_array,
                parking_costs_array_eurocent=parking_cost_array,
            )
            key = DataKey(
                id="GratisAuto",
                part_of_day=pod,
                income=income_level,
                motive=motive_name,
                regime=regime,
            )
            publish(key, gtr_skim)

            # Free PT generalized travel time:
            gtr_skim = np.where(pt_time_matrix > 0.5, pt_time_matrix, IKOB_INFINITE)
            key = DataKey(
                id="GratisOV",
                part_of_day=pod,
                motive=motive_name,
                regime=regime,
            )
            publish(key, gtr_skim)

    return travel_time_output if write_travel_time else None
