import logging

from scipy import sparse

from ikob import utils
from ikob.datasource import DataKey, DataSource, DataType

logger = logging.getLogger(__name__)


class CombinedWeightsSource(DataSource):
    """Compute combined weights from single weights when they are requested."""

    # cutoff determined experimentally
    MATRIX_NUM_NON_ZERO_CACHE_CUTOFF = 5_000_000

    def __init__(self, config, single_weights: DataSource):
        super().__init__(config, DataType.WEIGHTS, has_zone_id_header=True)
        self.single_weights = single_weights

    def get(self, key: DataKey):

        if key in self.cache:
            return self.cache[key]

        components = key.id.split("_")
        if (
            key.subtopic != "combinaties"
            or not components
            or any(
                component not in {"Auto", "GeenAuto", "GeenRijbewijs", "GratisAuto", "OV", "GratisOV", "Fiets"}
                for component in components
            )
        ):
            raise ValueError(f"Key not meant for combined weights source given to combined weights source. Key {key}")

        result = None
        for component in components:
            component_key = DataKey(
                f"{component}",
                part_of_day=key.part_of_day,
                regime=key.regime,
                motive=key.motive,
                income=key.income,
                fuel_kind=key.fuel_kind if component == "Auto" else "",
            )
            try:
                matrix = self.single_weights.get(component_key)
            except (FileNotFoundError, OSError) as error:
                raise KeyError(f"Missing single weight {component_key} required for combined weight {key}") from error
            result = sparse.csr_matrix(matrix) if result is None else sparse_elementwise_max(result, matrix)

        if result is None:
            raise KeyError(f"Cannot compute combined weight key: {key}")

        # Only cache if the matrix is sufficiently small to limit memory usage on large projects
        if result.nnz <= CombinedWeightsSource.MATRIX_NUM_NON_ZERO_CACHE_CUTOFF:
            self.cache[key] = result

        return result


def sparse_elementwise_max(left, right) -> sparse.csr_matrix:
    """Return elementwise max, converting the input to a sparse matrix if necessary and returning a CSR matrix."""
    left_sparse = left if sparse.issparse(left) else sparse.csr_matrix(left)
    right_sparse = right if sparse.issparse(right) else sparse.csr_matrix(right)
    return left_sparse.maximum(right_sparse).tocsr()


def calculate_combined_weights(
    config, single_weights: DataSource, write_weights: bool = False, *, selected_income: str | None = None
) -> DataSource:
    combined_weights = CombinedWeightsSource(config, single_weights)
    if write_weights:
        _materialize_combined_weights(config, combined_weights, selected_income=selected_income)
    return combined_weights


def get_weight_matrix(
    single_weights: DataSource,
    combined_weights: DataSource,
    group,
    modality,
    motive,
    regime,
    part_of_day,
    income,
    ratio_electric: float,
):
    weights, key, electric_key = weight_matrix_request(
        single_weights,
        combined_weights,
        group,
        modality,
        motive,
        regime,
        part_of_day,
        income,
        ratio_electric,
    )
    return load_weight_matrix(weights, key, electric_key, ratio_electric)


def load_weight_matrix(weights: DataSource, key: DataKey, electric_key: DataKey | None, ratio_electric: float):
    matrix = weights.get(key)
    if electric_key is None or ratio_electric == 0:
        return matrix
    matrix_electric = weights.get(electric_key)
    return ratio_electric * matrix_electric + (1 - ratio_electric) * matrix


def weight_matrix_request(
    single_weights: DataSource,
    combined_weights: DataSource,
    group,
    modality,
    motive,
    regime,
    part_of_day,
    income,
    ratio_electric: float,
) -> tuple[DataSource, DataKey, DataKey | None]:

    if any(component not in {"Auto", "OV", "Fiets"} for component in modality.split("_")):
        raise ValueError(f"Unknown modality: '{modality}'")

    if modality == "Fiets":
        key = DataKey(
            modality,
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            income=income,
        )
        return single_weights, key, None

    single_group = utils.single_group(modality, group)
    combined_group = utils.combined_group(modality, group)

    if modality == "Auto" and "WelAuto" in group or combined_group[0] == "A":
        subtopic = "" if modality == "Auto" else "combinaties"
        weights = single_weights if modality == "Auto" else combined_weights
        id = single_group if modality == "Auto" else combined_group
        if id is None or id == "":
            raise ValueError(
                f"Computed key id is {id}. Unable to compute valid id from modality {modality} and group {group}"
            )
        key = DataKey(
            id,
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            income=income,
            subtopic=subtopic,
            fuel_kind="fossiel",
        )
        if ratio_electric == 0:
            return weights, key, None
        electric_key = DataKey(
            id,
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            income=income,
            subtopic=subtopic,
            fuel_kind="elektrisch",
        )
        fossil_key = key
        return weights, fossil_key, electric_key

    if modality == "Auto" or modality == "OV":
        if single_group is None or single_group == "":
            raise ValueError(
                f"Computed key id is {single_group}. Unable to compute valid id from modality {modality} and group {group}"
            )
        key = DataKey(
            single_group,
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            income=income,
        )
        return single_weights, key, None

    if combined_group is None or combined_group == "":
        raise ValueError(
            f"Computed key id is {combined_group}. Unable to compute valid id from modality {modality} and group {group}"
        )
    key = DataKey(
        combined_group,
        part_of_day=part_of_day,
        regime=regime,
        motive=motive,
        income=income,
        subtopic="combinaties",
    )
    return combined_weights, key, None


def _materialize_combined_weights(
    config, combined_weights: CombinedWeightsSource, *, selected_income: str | None = None
) -> None:
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

    incomes = [selected_income] if selected_income is not None else ["hoog", "middelhoog", "middellaag", "laag"]
    car_kinds = ["Auto", "GeenAuto", "GeenRijbewijs", "GratisAuto"]
    pt_kinds = ["OV", "GratisOV"]
    combinations = (
        [(pt, "Fiets") for pt in pt_kinds]
        + [(car, "Fiets") for car in car_kinds]
        + [(car, pt) for pt in pt_kinds for car in car_kinds]
        + [(car, pt, "Fiets") for pt in pt_kinds for car in car_kinds]
    )

    for part_of_day in part_of_days:
        for income in incomes:
            for components in combinations:
                fuel_kinds = ("fossiel", "elektrisch") if "Auto" in components else ("",)
                for fuel_kind in fuel_kinds:
                    key = DataKey(
                        "_".join(components),
                        part_of_day=part_of_day,
                        income=income,
                        regime=regimes,
                        motive=motive_name,
                        subtopic="combinaties",
                        fuel_kind=fuel_kind,
                    )
                    combined_weights.set(key, combined_weights.get(key))
