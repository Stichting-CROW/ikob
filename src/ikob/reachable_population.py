import logging
from dataclasses import replace
from pathlib import Path

import numpy as np

from ikob import utils
from ikob.combined_weights import load_weight_matrix, weight_matrix_request
from ikob.datasource import DataKey, DataSource, DataType, SegsSource
from ikob.distribute_over_groups import BASE_GROUPS, INCOME_LEVELS, NUM_GROUPS_PER_INCOME_CLASS
from ikob.output_tables import assemble_income_tables

logger = logging.getLogger(__name__)


def create_citizens_file(distribution_matrix, working_population):
    return np.asarray(working_population)[:, np.newaxis] * np.asarray(distribution_matrix)


def calculate_reachable_population(
    config,
    single_weights: DataSource,
    combined_weights: DataSource,
    *,
    selected_income: str | None = None,
    results: DataSource | None = None,
) -> DataSource:
    """
    From combined weights to number of citizens that can reach the destination in a zone.

    Corresponds to section D5 in the IKOB-algorithm.pdf.

    If a selected income is given, the full results cannot be assembled directly as they include overviews of
    reach across all income groups. The caller will have to call assemble_destination_outputs on the final datasource
    containing results for all income groups.
    """
    logger.info("Starting step: Reachable population for destinations.")

    project_config = config["project"]
    skims_config = config["skims"]
    distribution_config = config["verdeling"]
    part_of_days = skims_config["dagsoort"]
    advanced_config = config["geavanceerd"]

    scenario = project_config["verstedelijkingsscenario"]
    regimes = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]
    traveling_population_path = Path(project_config["motief"]["reizende populatie"])
    car_possession_groups = advanced_config["welke_groepen"]
    configured_income_groups = project_config["welke_inkomensgroepen"]
    electric_percentage = distribution_config["Percelektrisch"]

    modalities = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)

    working_population = np.asarray(traveling_population, dtype=utils.FLOAT_DTYPE).sum(axis=1)

    # section D5: derive group sizes $I_{gh}$ per origin zone by distributing the origin-zone working population
    # over groups using the SEG distribution matrix.

    origins = results if results is not None else DataSource(config, DataType.ORIGINS)

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=utils.FLOAT_DTYPE,
            scenario=scenario,
            group=motive_name,
            modifier="alleen_autobezit" if car_possession_group == "alleen autobezit" else "",
            has_id_column=True,
        )

        citizens = create_citizens_file(distribution_matrix, working_population)
        citizens_transpose = utils.transpose(citizens)

        for part_of_day in part_of_days:
            for i_income_group, income_group in enumerate(INCOME_LEVELS):
                if selected_income is not None and income_group != selected_income:
                    continue
                general_possibility_totals = []
                for modality in modalities:
                    working_population_list = utils.zeros(len(working_population))
                    # We cannot cache the matrix vector product because the vector changes per group
                    # But, rather then doing a number of matrix vector products and summing the results with the same matrix
                    # We can sum all vectors using the same matrix and do a single load_weight_matrix call and product
                    citizens_by_weight_matrix = {}

                    active_groups = BASE_GROUPS if income_group in configured_income_groups else ()
                    for igroup, group in enumerate(active_groups, start=i_income_group * NUM_GROUPS_PER_INCOME_CLASS):
                        K = electric_percentage.get(income_group) / 100
                        weights, weight_key, electric_key = weight_matrix_request(
                            single_weights,
                            combined_weights,
                            group,
                            modality,
                            motive_name,
                            regimes,
                            part_of_day,
                            income_group,
                            K,
                        )
                        cache_key = (weights is combined_weights, weight_key, electric_key, K)
                        if cache_key not in citizens_by_weight_matrix:
                            citizens_by_weight_matrix[cache_key] = citizens_transpose[igroup].copy()
                        else:
                            citizens_by_weight_matrix[cache_key] += citizens_transpose[igroup]

                    # Section D5: $B_{gbv} = \sum_h I_{gh} \cdot G_{ghbvm}$ and
                    # $B_{ibv} = \sum_{g \in i} B_{gbv}$. K mixes fuel weights when applicable.
                    # Sum citizens sharing a weight matrix before applying it, avoiding repeated weight loads
                    # and matrix-vector products without retaining the matrices.
                    for (is_combined, weight_key, electric_key, K), group_citizens in citizens_by_weight_matrix.items():
                        weights = combined_weights if is_combined else single_weights
                        # Weights are indexed [origin, destination] in D5.
                        working_population_list += (
                            load_weight_matrix(weights, weight_key, electric_key, K).T @ group_citizens
                        )

                    key = DataKey(
                        id=utils.INCOME_VECTOR_RESULT_ID,
                        part_of_day=part_of_day,
                        group=car_possession_group,
                        income=income_group,
                        motive=motive_name,
                        modality=modality,
                        is_intermediate=True,
                    )
                    origins.set(key, working_population_list)
                    general_possibility_totals.append(origins.get(key))

                key = DataKey(
                    id="Pot_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    income=income_group,
                    motive=motive_name,
                    header=modalities,
                )

                origins_total = utils.transpose(general_possibility_totals)
                origins_total = np.round(origins_total).astype(int)
                origins.set(key, origins_total)

    if selected_income is None:
        assemble_population_outputs(config, origins)
    return origins


def assemble_population_outputs(config, origins: DataSource):
    project = config["project"]
    destinations = SegsSource(config).read(
        Path(project["motief"]["bestemmingsplaatsen"]).name, scenario=project["verstedelijkingsscenario"]
    )
    for key, values in assemble_income_tables(origins, ["laag", "middellaag", "middelhoog", "hoog"]):
        # Rename the per income group result for output
        total_id = "Pot_totaal"
        origins.set(replace(key, id=total_id), np.round(values).astype(int))
        # Section D5 of the algorithm region result is a destinations-weighted average of reachability
        # Store the per-zone numerator contribution here. Regional summation and division by total population could happen later.
        origins.set(replace(key, id=f"{total_id}product"), values * destinations)
