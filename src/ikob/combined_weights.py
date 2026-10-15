import logging

import numpy as np
from scipy import sparse

from ikob.datasource import DataKey, DataSource, DataType

logger = logging.getLogger(__name__)


def component_preference(component, preference):
    if component == "Fiets":
        return "Fiets" if preference == "Fiets" else ""
    return preference


class CombinedWeightsSource(DataSource):
    """Compute combined weights from single weights when they are requested."""

    def __init__(self, config, single_weights: DataSource):
        super().__init__(config, DataType.WEIGHTS, has_zone_id_header=True)
        self.single_weights = single_weights

    def get(self, key: DataKey):
        if key in self.cache:
            return self.cache[key]

        components = key.id.removesuffix("_vk").split("_")
        if (
            key.subtopic != "combinaties"
            or not components
            or any(
                component not in {"Auto", "GeenAuto", "GeenRijbewijs", "GratisAuto", "OV", "GratisOV", "Fiets"}
                for component in components
            )
        ):
            return super().get(key)

        result = None
        for component in components:
            component_key = DataKey(
                f"{component}_vk",
                part_of_day=key.part_of_day,
                regime=key.regime,
                motive=key.motive,
                preference=component_preference(component, key.preference),
                income=key.income,
                fuel_kind=key.fuel_kind if component == "Auto" else "",
            )
            try:
                matrix = self.single_weights.get(component_key)
            except (FileNotFoundError, OSError) as error:
                raise KeyError(f"Missing single weight {component_key} required for combined weight {key}") from error
            result = matrix if result is None else elementwise_max(result, matrix)

        if result is None:
            raise KeyError(f"Cannot compute combined weight key: {key}")
        # Do not cache the results here to save on memory usage at the cost of some performance
        return result


def elementwise_max(left, right):
    """Return the elementwise maximum, preferring the sparse implementation."""
    if sparse.issparse(left) and sparse.issparse(right):
        return left.maximum(right).tocsr()

    logger.warning("Computing combined weights with one or more non-sparse matrices.")
    if sparse.issparse(left) or sparse.issparse(right):
        left_sparse = left if sparse.issparse(left) else sparse.csr_matrix(left)
        right_sparse = right if sparse.issparse(right) else sparse.csr_matrix(right)
        return left_sparse.maximum(right_sparse).tocsr()

    return np.maximum(left, right)


def has_preference(kind_car, kind_pt, preference):
    if kind_car == "GeenAuto" or kind_car == "GeenRijbewijs":
        if preference == "Auto":
            return False
        else:
            if kind_pt == "GratisOV":
                return preference == "OV"
            else:
                return True
    elif kind_car == "GratisAuto":
        if kind_pt == "GratisOV":
            return preference == "Neutraal"
        else:
            return preference == "Auto"
    elif kind_pt == "GratisOV":
        return preference == "OV"
    else:
        return True


def calculate_combined_weights(config, single_weights: DataSource, write_weights: bool = False) -> DataSource:
    combined_weights = CombinedWeightsSource(config, single_weights)
    if write_weights:
        _materialize_combined_weights(config, single_weights, combined_weights)
    return combined_weights


def _materialize_combined_weights(config, single_weights: DataSource, combined_weights: DataSource) -> None:
    """
    From weights for single travel modes to combined weights.

    Corresponds to section D3 in the IKOB-algorithm.pdf

    Travelers are expected to always take the travel mode of least resistance (highest weight) available.
    i.e. the maximum weight over the available travel modes is taken here.
    """
    logger.info("Starting step: Maximum weights by multiple modalities.")

    project_config = config["project"]
    skims_config = config["skims"]

    motive_name = project_config["motief"]["naam"]
    regimes = project_config["beprijzingsregime"]
    part_of_days = skims_config["dagsoort"]

    incomes = ["hoog", "middelhoog", "middellaag", "laag"]
    preferences = ["Auto", "Neutraal", "Fiets", "OV"]
    modalities_bike = ["Fiets"]
    car_kinds = ["Auto", "GeenAuto", "GeenRijbewijs", "GratisAuto"]
    pt_kinds = ["OV", "GratisOV"]
    fuel_kinds = ["fossiel", "elektrisch"]

    for part_of_day in part_of_days:
        for income in incomes:
            for preference in preferences:
                for modality_bike in modalities_bike:
                    for pt_kind in pt_kinds:
                        if not has_preference("Auto", pt_kind, preference):
                            continue

                        preference_bike = "Fiets" if preference == "Fiets" else ""
                        key = DataKey(
                            f"{modality_bike}_vk",
                            part_of_day=part_of_day,
                            preference=preference_bike,
                            income=income,
                            regime=regimes,
                            motive=motive_name,
                        )
                        bike_matrix = single_weights.get(key)

                        key = DataKey(
                            f"{pt_kind}_vk",
                            part_of_day=part_of_day,
                            preference=preference,
                            income=income,
                            regime=regimes,
                            motive=motive_name,
                        )
                        pt_matrix = single_weights.get(key)

                        max_matrix = elementwise_max(bike_matrix, pt_matrix)
                        key = DataKey(
                            f"{pt_kind}_{modality_bike}_vk",
                            part_of_day=part_of_day,
                            income=income,
                            regime=regimes,
                            motive=motive_name,
                            preference=preference,
                            subtopic="combinaties",
                        )
                        # Max weight of taking either pt or the bike
                        combined_weights.set(key, max_matrix)

                    for car_kind in car_kinds:
                        if not has_preference(car_kind, "OV", preference):
                            continue

                        preference_bike = "Fiets" if preference == "Fiets" else ""
                        key = DataKey(
                            f"{modality_bike}_vk",
                            part_of_day=part_of_day,
                            preference=preference_bike,
                            income=income,
                            regime=regimes,
                            motive=motive_name,
                        )
                        bike_matrix = single_weights.get(key)

                        if car_kind == "Auto":
                            for fuel_kind in fuel_kinds:
                                key = DataKey(
                                    f"{car_kind}_vk",
                                    part_of_day=part_of_day,
                                    preference=preference,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                    fuel_kind=fuel_kind,
                                )
                                car_matrix = single_weights.get(key)

                                max_matrix = elementwise_max(bike_matrix, car_matrix)
                                key = DataKey(
                                    f"{car_kind}_{modality_bike}_vk",
                                    part_of_day=part_of_day,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                    preference=preference,
                                    subtopic="combinaties",
                                    fuel_kind=fuel_kind,
                                )
                                # Max weight of taking either the car or the bike
                                combined_weights.set(key, max_matrix)
                        else:
                            key = DataKey(
                                f"{car_kind}_vk",
                                part_of_day=part_of_day,
                                preference=preference,
                                income=income,
                                regime=regimes,
                                motive=motive_name,
                            )
                            car_matrix = single_weights.get(key)

                            max_matrix = elementwise_max(bike_matrix, car_matrix)
                            key = DataKey(
                                f"{car_kind}_{modality_bike}_vk",
                                part_of_day=part_of_day,
                                income=income,
                                regime=regimes,
                                motive=motive_name,
                                preference=preference,
                                subtopic="combinaties",
                            )
                            # Max weight of taking either the car or the bike
                            combined_weights.set(key, max_matrix)

                for pt_kind in pt_kinds:
                    for car_kind in car_kinds:
                        if not has_preference(car_kind, pt_kind, preference):
                            continue

                        key = DataKey(
                            f"{pt_kind}_vk",
                            part_of_day=part_of_day,
                            preference=preference,
                            income=income,
                            regime=regimes,
                            motive=motive_name,
                        )
                        pt_matrix = single_weights.get(key)

                        if car_kind == "Auto":
                            for fuel_kind in fuel_kinds:
                                key = DataKey(
                                    f"{car_kind}_vk",
                                    part_of_day=part_of_day,
                                    preference=preference,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                    fuel_kind=fuel_kind,
                                )
                                car_matrix = single_weights.get(key)
                                max_matrix = elementwise_max(pt_matrix, car_matrix)
                                key = DataKey(
                                    f"{car_kind}_{pt_kind}_vk",
                                    part_of_day=part_of_day,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                    preference=preference,
                                    subtopic="combinaties",
                                    fuel_kind=fuel_kind,
                                )
                                # Max weight of taking either the car or pt
                                combined_weights.set(key, max_matrix)
                        else:
                            key = DataKey(
                                f"{car_kind}_vk",
                                part_of_day=part_of_day,
                                preference=preference,
                                income=income,
                                regime=regimes,
                                motive=motive_name,
                            )
                            car_matrix = single_weights.get(key)

                            max_matrix = elementwise_max(pt_matrix, car_matrix)
                            key = DataKey(
                                f"{car_kind}_{pt_kind}_vk",
                                part_of_day=part_of_day,
                                income=income,
                                regime=regimes,
                                motive=motive_name,
                                preference=preference,
                                subtopic="combinaties",
                            )
                            # Max weight of taking either the car or pt
                            combined_weights.set(key, max_matrix)

                for modality_bike in modalities_bike:
                    for pt_kind in pt_kinds:
                        for car_kind in car_kinds:
                            if not has_preference(car_kind, pt_kind, preference):
                                continue

                            preference_bike = "Fiets" if preference == "Fiets" else ""
                            key = DataKey(
                                f"{modality_bike}_vk",
                                part_of_day=part_of_day,
                                preference=preference_bike,
                                income=income,
                                regime=regimes,
                                motive=motive_name,
                            )
                            bike_matrix = single_weights.get(key)

                            key = DataKey(
                                f"{pt_kind}_vk",
                                part_of_day=part_of_day,
                                preference=preference,
                                income=income,
                                regime=regimes,
                                motive=motive_name,
                            )
                            pt_matrix = single_weights.get(key)

                            if car_kind == "Auto":
                                for fuel_kind in fuel_kinds:
                                    key = DataKey(
                                        f"{car_kind}_vk",
                                        part_of_day=part_of_day,
                                        preference=preference,
                                        income=income,
                                        regime=regimes,
                                        motive=motive_name,
                                        fuel_kind=fuel_kind,
                                    )
                                    car_matrix = single_weights.get(key)

                                    max_matrix = elementwise_max(elementwise_max(car_matrix, bike_matrix), pt_matrix)
                                    key = DataKey(
                                        f"{car_kind}_{pt_kind}_{modality_bike}_vk",
                                        part_of_day=part_of_day,
                                        income=income,
                                        regime=regimes,
                                        motive=motive_name,
                                        preference=preference,
                                        subtopic="combinaties",
                                        fuel_kind=fuel_kind,
                                    )
                                    # Max weight of taking either the car or pt or the bike
                                    combined_weights.set(key, max_matrix)
                            else:
                                key = DataKey(
                                    f"{car_kind}_vk",
                                    part_of_day=part_of_day,
                                    preference=preference,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                )
                                car_matrix = single_weights.get(key)

                                max_matrix = elementwise_max(elementwise_max(car_matrix, bike_matrix), pt_matrix)
                                key = DataKey(
                                    f"{car_kind}_{pt_kind}_{modality_bike}_vk",
                                    part_of_day=part_of_day,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                    preference=preference,
                                    subtopic="combinaties",
                                )
                                # Max weight of taking either the car or pt or the bike
                                combined_weights.set(key, max_matrix)
