import logging
import math

import numpy as np
from scipy import sparse

from ikob.configuration_definition import DecayCurveName
from ikob.constants import work_constants
from ikob.datasource import DataKey, DataSource, DataType
from ikob.generalized_travel_time import generalized_travel_time
from ikob.utils import FLOAT_DTYPE

logger = logging.getLogger(__name__)

MIN_WEIGHT = 0.001


def decay_curve(travel_time, alpha, omega, scaling):
    return scaling / (1 + np.exp((travel_time - omega) * alpha))


def inverse_decay_curve(weight, alpha, omega, scaling):
    return omega + math.log(scaling / weight - 1) / alpha


def calculate_weights(generalized_travel_time, modality: str, decay_curve_name: DecayCurveName):
    """
    Applies a decay curve to the generalized travel time to compute a weight or 'resistance' for the movement.
    A weight of 1 means a movement with very little resistance (a short & cheap movement).
    A weight of 0 means a movement with a lot of resistance (a long & expensive movement).
    """
    constants = work_constants(modality, decay_curve_name)
    cutoff = inverse_decay_curve(MIN_WEIGHT, *constants)
    rows, cols = np.nonzero(generalized_travel_time <= cutoff)
    if rows.size == 0:
        return sparse.csr_matrix(generalized_travel_time.shape, dtype=FLOAT_DTYPE)

    values = decay_curve(generalized_travel_time[rows, cols], *constants)
    keep = values >= MIN_WEIGHT
    return sparse.csr_matrix(
        (values[keep], (rows[keep], cols[keep])), shape=generalized_travel_time.shape, dtype=FLOAT_DTYPE
    )


def consume_travel_time(config, key: DataKey, travel_time, weights: DataSource, *, selected_income: str | None = None):
    """Convert one GTT matrix to all single-weight matrices that use it."""
    project_config = config["project"]
    decay_curve_name = project_config["motief"]["reistijdvervalscurve"]
    regimes = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]

    def store(income=key.income, modality="Auto", weight_matrix=None):
        weight_key = DataKey(
            key.id,
            part_of_day=key.part_of_day,
            income=income,
            regime=regimes,
            motive=motive_name,
            fuel_kind=key.fuel_kind,
        )

        if weight_matrix is None:
            weight_matrix = calculate_weights(travel_time, modality, decay_curve_name)
        weights.set(weight_key, weight_matrix)

    if key.id in ("Auto", "GeenAuto", "GeenRijbewijs", "GratisAuto"):
        store()

    elif key.id == "Fiets":
        modality = "E-fiets" if project_config["fiets of E-fiets"]["E-fiets"] else "Fiets"
        store(modality=modality)

    elif key.id == "OV":
        store(modality="OV")

    elif key.id == "GratisOV":
        # Here we have to loop over the income classes as well because the travel time computation
        # Only computes the free PT travel time once (as it's not dependent on the income group)
        # The weights are not dependent on the income group either, but for ease of implementation
        # we create a key with income group for each income to point to this weight matrix
        # so this modality behaves the same as the others.

        # Note that the free car travel time _is_ dependent on income class,
        # because there are still costs associated with car free car travel counterintuitively.
        # see generalized_travel_time.py for details
        weight_matrix = calculate_weights(travel_time, "OV", decay_curve_name)
        incomes = [selected_income] if selected_income is not None else ["hoog", "middelhoog", "middellaag", "laag"]
        for income in incomes:
            store(income=income, weight_matrix=weight_matrix)


def calculate_single_weights_on_demand(
    config, write_travel_time: bool = False, *, selected_income: str | None = None
) -> tuple[DataSource, DataSource | None]:
    """Compute GTTs and consume each one immediately as sparse weights."""
    weights = DataSource(config, DataType.WEIGHTS, has_zone_id_header=True)

    def consume(key, travel_time):
        consume_travel_time(config, key, travel_time, weights, selected_income=selected_income)

    travel_time = generalized_travel_time(
        config,
        on_travel_time=consume,
        write_travel_time=write_travel_time,
        selected_income=selected_income,
    )
    return weights, travel_time


def calculate_single_weights(
    config, generalized_travel_time: DataSource, *, selected_income: str | None = None
) -> DataSource:
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
    incomes = [selected_income] if selected_income is not None else ["hoog", "middelhoog", "middellaag", "laag"]

    weights = DataSource(config, DataType.WEIGHTS, has_zone_id_header=True)

    for part_of_day in part_of_days:
        for income in incomes:
            # bike
            key = DataKey("Fiets", part_of_day=part_of_day, regime=regimes, motive=motive_name, income=income)
            travel_time = generalized_travel_time.get(key)
            consume_travel_time(config, key, travel_time, weights)

            # car
            for fuel_kind in ("fossiel", "elektrisch"):
                key = DataKey(
                    "Auto",
                    part_of_day=part_of_day,
                    income=income,
                    regime=regimes,
                    motive=motive_name,
                    fuel_kind=fuel_kind,
                )
                travel_time = generalized_travel_time.get(key)
                consume_travel_time(config, key, travel_time, weights)
            # no car
            for no_car_kind in ("GeenAuto", "GeenRijbewijs"):
                key = DataKey(no_car_kind, part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
                travel_time = generalized_travel_time.get(key)
                consume_travel_time(config, key, travel_time, weights)

            # free car
            key = DataKey("GratisAuto", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
            travel_time = generalized_travel_time.get(key)
            consume_travel_time(config, key, travel_time, weights)

            # public transport
            key = DataKey("OV", part_of_day=part_of_day, income=income, regime=regimes, motive=motive_name)
            travel_time = generalized_travel_time.get(key)

            consume_travel_time(config, key, travel_time, weights)

        # free public transport
        key = DataKey("GratisOV", part_of_day=part_of_day, regime=regimes, motive=motive_name)
        travel_time = generalized_travel_time.get(key)
        consume_travel_time(config, key, travel_time, weights, selected_income=selected_income)

    return weights
