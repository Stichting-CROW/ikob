import logging

import numpy as np
from scipy import sparse

from ikob.configuration_definition import DecayCurveName
from ikob.constants import work_constants
from ikob.datasource import DataKey, DataSource, DataType
from ikob.generalized_travel_time import generalized_travel_time
from ikob.utils import FLOAT_DTYPE

logger = logging.getLogger(__name__)

ALL_PREFERENCES = ["Auto", "Neutraal", "Fiets", "OV"]


def calculate_weights(generalized_travel_time, modality, preference, decay_curve_name: DecayCurveName):
    """
    Applies a decay curve to the generalized travel time to compute a weight or 'resistance' for the movement.
    A weight of 1 means a movement with very little resistance (a short & cheap movement).
    A weight of 0 means a movement with a lot of resistance (a long & expensive movement).
    """
    alpha, omega, scaling = work_constants(modality, preference, decay_curve_name)

    # Build a sparse matrix directly from in-range entries.
    rows, cols = np.nonzero(generalized_travel_time < 180)
    if rows.size == 0:
        return sparse.csr_matrix(generalized_travel_time.shape, dtype=FLOAT_DTYPE)

    values = scaling / (1 + np.exp((generalized_travel_time[rows, cols] - omega) * alpha))
    keep = values >= 0.001
    return sparse.csr_matrix(
        (values[keep], (rows[keep], cols[keep])), shape=generalized_travel_time.shape, dtype=FLOAT_DTYPE
    )


def consume_travel_time(config, key: DataKey, travel_time, weights: DataSource):
    """Convert one GTT matrix to all single-weight matrices that use it."""
    project_config = config["project"]
    decay_curve = project_config["motief"]["reistijdvervalscurve"]
    regimes = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]

    def store(weight_id, preference, income=key.income, fuel_kind="", modality="Auto", weight_matrix=None):
        weight_key = DataKey(
            weight_id,
            part_of_day=key.part_of_day,
            income=income,
            regime=regimes,
            motive=motive_name,
            preference=preference,
            fuel_kind=fuel_kind,
        )

        if weight_matrix is None:
            weight_matrix = calculate_weights(travel_time, modality, preference, decay_curve)
        weights.set(weight_key, weight_matrix)

    if key.id == "Fiets":
        modality = "E-fiets" if project_config["fiets of E-fiets"]["E-fiets"] else "Fiets"
        # The empty preference is only used for modality bike, this is to keep behavior identical to old code.
        for preference in ("", "Fiets"):
            store("Fiets_vk", preference, modality=modality)

    elif key.id.startswith("Auto_"):
        fuel_kind = key.id.removeprefix("Auto_")
        for preference in ALL_PREFERENCES:
            store("Auto_vk", preference, fuel_kind=fuel_kind)

    elif key.id in ("GeenAuto", "GeenRijbewijs"):
        for preference in ("Neutraal", "OV", "Fiets"):
            store(f"{key.id}_vk", preference)

    elif key.id == "OV":
        for preference in ALL_PREFERENCES:
            store("OV_vk", preference, modality="OV")

    elif key.id == "GratisAuto":
        # The free car weights always use the car preference, even though the preference stored at the key
        # might be neutral. This is to keep behavior identical to old code.
        weight_matrix = calculate_weights(travel_time, "Auto", "Auto", decay_curve)
        for preference in ("Neutraal", "Auto"):
            store("GratisAuto_vk", preference, weight_matrix=weight_matrix)

    elif key.id == "GratisOV":
        # The free PT weights always use the PT preference, even though the preference stored at the key
        # might be neutral. This is to keep behavior identical to old code.
        weight_matrix = calculate_weights(travel_time, "OV", "OV", decay_curve)
        # Here we have to loop over the income classes as well because the travel time computation
        # Only computes the free PT travel time once (as it's not dependent on the income group)
        # Note that the free car weights are dependent, because there are still costs associated with car free car travel counterintuitively
        # see generalized_travel_time.py for details
        for income in ("hoog", "middelhoog", "middellaag", "laag"):
            for preference in ("Neutraal", "OV"):
                store("GratisOV_vk", preference, income=income, weight_matrix=weight_matrix)


def calculate_single_weights_on_demand(config, write_travel_time: bool = False):
    """Compute GTTs and consume each one immediately as sparse weights."""
    weights = DataSource(config, DataType.WEIGHTS, has_zone_id_header=True)

    def consume(key, travel_time):
        consume_travel_time(config, key, travel_time, weights)

    # The returned travel time will be empty if write_travel_time is false
    travel_time = generalized_travel_time(
        config,
        on_travel_time=consume,
        write_travel_time=write_travel_time,
    )
    return weights, travel_time


def calculate_single_weights(config, generalized_travel_time: DataSource) -> DataSource:
    """
    From experienced travel time to the computation of weights

    Corresponds to section D2 in the IKOB-algorithm.pdf

    Loops over the computed generalized travel time from the previous step and applies a decay curve to them.
    """

    logger.info("Starting step: Weights (travel time decay curves) for car, PT, bike, and E-bike.")

    skims_config = config["skims"]

    # Ophalen van instellingen
    part_of_days = skims_config["dagsoort"]
    motive_name = config["project"]["motief"]["naam"]
    regimes = config["project"]["beprijzingsregime"]

    # Vaste waarden
    incomes = ["hoog", "middelhoog", "middellaag", "laag"]

    weights = DataSource(config, DataType.WEIGHTS, has_zone_id_header=True)

    for part_of_day in part_of_days:
        for income in incomes:
            # bike
            key = DataKey("Fiets", part_of_day=part_of_day, regime=regimes, motive=motive_name, income=income)
            travel_time = generalized_travel_time.get(key)
            consume_travel_time(weights.config, key, travel_time, weights)

            # car
            for fuel_kind in ("fossiel", "elektrisch"):
                key = DataKey(
                    f"Auto_{fuel_kind}", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name
                )
                travel_time = generalized_travel_time.get(key)
                consume_travel_time(weights.config, key, travel_time, weights)
            # no car
            for no_car_kind in ("GeenAuto", "GeenRijbewijs"):
                key = DataKey(no_car_kind, part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
                travel_time = generalized_travel_time.get(key)
                consume_travel_time(weights.config, key, travel_time, weights)

            # free car
            key = DataKey("GratisAuto", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
            travel_time = generalized_travel_time.get(key)
            consume_travel_time(weights.config, key, travel_time, weights)

            # public transport
            key = DataKey("OV", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
            travel_time = generalized_travel_time.get(key)

            consume_travel_time(weights.config, key, travel_time, weights)

        # pree public transport
        key = DataKey("GratisOV", part_of_day=part_of_day, regime=regimes, motive=motive_name)
        travel_time = generalized_travel_time.get(key)
        consume_travel_time(weights.config, key, travel_time, weights)

    return weights
