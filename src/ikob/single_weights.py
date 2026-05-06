import logging
import math

import numpy as np

from ikob.configuration_definition import DecayCurveName
from ikob.constants import work_constants
from ikob.datasource import DataKey, DataSource, DataType

logger = logging.getLogger(__name__)

ALL_PREFERENCES = ["Auto", "Neutraal", "Fiets", "OV"]


def calculate_weights(generalized_travel_time, modality, preference, decay_curve_name: DecayCurveName):
    """
    Applies a decay curve to the generalized travel time to compute a weight or 'resistance' for the movement.
    A weight of 1 means a movement with very little resistance (a short & cheap movement).
    A weight of 0 means a movement with a lot of resistance (a long & expensive movement).
    """
    alpha, omega, scaling = work_constants(modality, preference, decay_curve_name)
    n = len(generalized_travel_time)
    weight_matrix = np.zeros((n, n))

    for r in range(len(generalized_travel_time)):
        for k in range(len(generalized_travel_time)):
            if generalized_travel_time[r][k] < 180:
                travel_time = (1.0 / (1 + math.exp((-omega + generalized_travel_time[r][k]) * alpha))) * scaling
            else:
                travel_time = 0.0

            if travel_time < 0.001:
                travel_time = 0.0

            weight_matrix[r, k] = travel_time
    return weight_matrix


def calculate_single_weights(config, generalized_travel_time: DataSource) -> DataSource:
    """
    From experienced travel time to the computation of weights

    Corresponds to section D2 in the IKOB-algorithm.pdf

    Loops over the computed generalized travel time from the previous step and applies a decay curve to them.
    """

    logger.info("Starting step: Weights (travel time decay curves) for car, PT, bike, and E-bike.")

    project_config = config["project"]
    skims_config = config["skims"]

    # Ophalen van instellingen
    part_of_days = skims_config["dagsoort"]
    motive_name = project_config["motief"]["naam"]
    decay_curve = project_config["motief"]["reistijdvervalscurve"]
    regimes = project_config["beprijzingsregime"]

    # Vaste waarden
    incomes = ["hoog", "middelhoog", "middellaag", "laag"]

    weights = DataSource(config, DataType.WEIGHTS)

    for part_of_day in part_of_days:
        for income in incomes:
            add_bike_weights(
                part_of_day, regimes, motive_name, decay_curve, income, generalized_travel_time, weights, config
            )
            add_car_weights(part_of_day, regimes, motive_name, decay_curve, income, generalized_travel_time, weights)
            add_no_car_weights(part_of_day, regimes, motive_name, decay_curve, income, generalized_travel_time, weights)
            add_free_car_weights(
                part_of_day, regimes, motive_name, decay_curve, income, generalized_travel_time, weights
            )
            add_pt_weights(part_of_day, regimes, motive_name, decay_curve, income, generalized_travel_time, weights)
            add_free_pt_weights(
                part_of_day, regimes, motive_name, decay_curve, income, generalized_travel_time, weights
            )

    return weights


def add_bike_weights(
    part_of_day: str,
    regimes: str,
    motive_name: str,
    decay_curve: DecayCurveName,
    income: str,
    generalized_travel_time: DataSource,
    weights: DataSource,
    config,
):
    """Add bike weights to the weights DataSource. Weights are further split on preference and type of bike."""

    project_config = config["project"]
    modalities_bike = ["E-fiets"] if project_config["fiets of E-fiets"]["E-fiets"] else ["Fiets"]
    for preference in ALL_PREFERENCES:
        for modality in modalities_bike:
            if preference == "Auto" or preference == "Fiets":
                key = DataKey("Fiets", part_of_day=part_of_day, regime=regimes, motive=motive_name, income=income)
                gtr_skim = generalized_travel_time.get(key)
                weight_matrix = calculate_weights(gtr_skim, modality, preference, decay_curve_name=decay_curve)
                num_zones = len(weight_matrix)

                if preference == "Auto":
                    key = DataKey(
                        "Fiets_vk",
                        part_of_day=part_of_day,
                        regime=regimes,
                        motive=motive_name,
                        income=income,
                        header=DataKey.zone_header(num_zones),
                        index=DataKey.zone_index(num_zones),
                    )
                else:
                    key = DataKey(
                        "Fiets_vk",
                        part_of_day=part_of_day,
                        income=income,
                        regime=regimes,
                        motive=motive_name,
                        preference=preference,
                        header=DataKey.zone_header(num_zones),
                        index=DataKey.zone_index(num_zones),
                    )

                weights.set(key, weight_matrix.copy())


def add_car_weights(
    part_of_day: str,
    regimes: str,
    motive_name: str,
    decay_curve: DecayCurveName,
    income: str,
    generalized_travel_time: DataSource,
    weights: DataSource,
):
    """Add car weights to the weights DataSource. Weights are further split on preference and type of car."""

    fuel_kinds = ["fossiel", "elektrisch"]
    for preference in ALL_PREFERENCES:
        for fuel_kind in fuel_kinds:
            key = DataKey(
                f"Auto_{fuel_kind}", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name
            )
            gtr_skim = generalized_travel_time.get(key)

            weight_matrix = calculate_weights(gtr_skim, "Auto", preference, decay_curve)
            num_zones = len(weight_matrix)
            key = DataKey(
                "Auto_vk",
                part_of_day=part_of_day,
                income=income,
                regime=regimes,
                motive=motive_name,
                preference=preference,
                fuel_kind=fuel_kind,
                header=DataKey.zone_header(num_zones),
                index=DataKey.zone_index(num_zones),
            )
            weights.set(key, weight_matrix.copy())


def add_no_car_weights(
    part_of_day: str,
    regimes: str,
    motive_name: str,
    decay_curve: DecayCurveName,
    income: str,
    generalized_travel_time: DataSource,
    weights: DataSource,
):
    """Add no car weights to the weights DataSource. Weights are further split on preference and type of car."""

    no_car_kinds = ["GeenAuto", "GeenRijbewijs"]
    # Can't have a preference for car when you don't have a car
    no_car_preferences = ["Neutraal", "OV", "Fiets"]
    for preference in no_car_preferences:
        for no_car_kind in no_car_kinds:
            key = DataKey(f"{no_car_kind}", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
            gtr_skim = generalized_travel_time.get(key)

            weight_matrix = calculate_weights(gtr_skim, "Auto", preference, decay_curve)
            num_zones = len(weight_matrix)
            key = DataKey(
                f"{no_car_kind}_vk",
                part_of_day=part_of_day,
                income=income,
                regime=regimes,
                preference=preference,
                motive=motive_name,
                header=DataKey.zone_header(num_zones),
                index=DataKey.zone_index(num_zones),
            )
            weights.set(key, weight_matrix.copy())


def add_pt_weights(
    part_of_day: str,
    regimes: str,
    motive_name: str,
    decay_curve: DecayCurveName,
    income: str,
    generalized_travel_time: DataSource,
    weights: DataSource,
):
    """Add public transport weights to the weights DataSource. Weights are further split on preference."""

    for preference in ALL_PREFERENCES:
        key = DataKey("OV", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
        gtr_skim = generalized_travel_time.get(key)

        weight_matrix = calculate_weights(gtr_skim, "OV", preference, decay_curve)
        num_zones = len(weight_matrix)
        key = DataKey(
            "OV_vk",
            part_of_day=part_of_day,
            preference=preference,
            income=income,
            regime=regimes,
            motive=motive_name,
            header=DataKey.zone_header(num_zones),
            index=DataKey.zone_index(num_zones),
        )
        weights.set(key, weight_matrix.copy())


def add_free_car_weights(
    part_of_day,
    regimes,
    motive_name: str,
    decay_curve: DecayCurveName,
    income,
    generalized_travel_time: DataSource,
    weights: DataSource,
):
    """Add free car weights to the weights DataSource. Weights are further split on preference.

    The type of car does not matter, as the car is free."""

    key = DataKey("GratisAuto", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
    gtr_skim = generalized_travel_time.get(key)

    weight_matrix = calculate_weights(gtr_skim, "Auto", "Auto", decay_curve)
    num_zones = len(weight_matrix)
    # Can only have preference for the car or neutral if the car is free
    free_car_preferences = ["Neutraal", "Auto"]
    for preference in free_car_preferences:
        key = DataKey(
            "GratisAuto_vk",
            part_of_day=part_of_day,
            preference=preference,
            income=income,
            regime=regimes,
            motive=motive_name,
            header=DataKey.zone_header(num_zones),
            index=DataKey.zone_index(num_zones),
        )
        weights.set(key, weight_matrix.copy())


def add_free_pt_weights(
    part_of_day,
    regimes,
    motive_name: str,
    decay_curve: DecayCurveName,
    income,
    generalized_travel_time: DataSource,
    weights: DataSource,
):
    """Add free public transport weights to the weights DataSource. Weights are further split on preference."""

    key = DataKey("GratisOV", part_of_day=part_of_day, regime=regimes, motive=motive_name)
    gtr_skim = generalized_travel_time.get(key)

    weight_matrix = calculate_weights(gtr_skim, "OV", "OV", decay_curve)
    num_zones = len(weight_matrix)
    # Can only have preference for the public transport or neutral if the public transport is free
    special_pt_kinds = ["Neutraal", "OV"]
    for special_pt_kind in special_pt_kinds:
        key = DataKey(
            "GratisOV_vk",
            part_of_day=part_of_day,
            preference=special_pt_kind,
            income=income,
            regime=regimes,
            motive=motive_name,
            header=DataKey.zone_header(num_zones),
            index=DataKey.zone_index(num_zones),
        )
        weights.set(key, weight_matrix.copy())
