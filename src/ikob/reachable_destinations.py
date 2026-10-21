import logging
from dataclasses import replace
from pathlib import Path

import numpy as np

from ikob import utils
from ikob.combined_weights import get_weight_matrix, weight_matrix_request
from ikob.datasource import DataKey, DataSource, DataType, SegsSource
from ikob.output_tables import assemble_income_tables

logger = logging.getLogger(__name__)


def calculate_reachable_destinations(
    config,
    single_weights: DataSource,
    combined_weights: DataSource,
    *,
    selected_income: str | None = None,
    results: DataSource | None = None,
) -> DataSource:
    """
    From (combined) weights to reachable destinations per zone.

    The definition of destinations and the population to consider changes based on the travel motive to consider.

    Corresponds to section D4 in the IKOB-algorithm.pdf
    """
    logger.info("Starting step: Reachable destinations for citizens.")

    project_config = config["project"]
    skims_config = config["skims"]
    distribution_config = config["verdeling"]
    part_of_days = skims_config["dagsoort"]
    advanced_config = config["geavanceerd"]

    scenario = project_config["verstedelijkingsscenario"]
    regime = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]
    traveling_population_path = Path(project_config["motief"]["reizende populatie"])
    destinations_path = Path(project_config["motief"]["bestemmingsplaatsen"])
    car_possession_groups = advanced_config["welke_groepen"]
    income_groups = project_config["welke_inkomensgroepen"]
    electric_percentage = distribution_config["Percelektrisch"]

    base_groups = [
        "GratisAuto",
        "GratisAuto_GratisOV",
        "WelAuto_GratisOV",
        "WelAuto_vkAuto",
        "WelAuto_vkNeutraal",
        "WelAuto_vkFiets",
        "WelAuto_vkOV",
        "GeenAuto_GratisOV",
        "GeenAuto_vkNeutraal",
        "GeenAuto_vkFiets",
        "GeenAuto_vkOV",
        "GeenRijbewijs_GratisOV",
        "GeenRijbewijs_vkNeutraal",
        "GeenRijbewijs_vkFiets",
        "GeenRijbewijs_vkOV",
    ]

    groups = []
    for income_group in income_groups:
        for base_group in base_groups:
            groups.append(f"{base_group}_{income_group}")

    modalities = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)
    destinations_segs = segs_source.read(destinations_path.name, scenario=scenario)
    destinations = utils.transpose(destinations_segs)

    traveling_population_totals = [sum(bbpk) for bbpk in traveling_population]

    income_distributions = np.zeros((len(traveling_population), len(traveling_population[0])), dtype=utils.FLOAT_DTYPE)
    for i in range(len(traveling_population)):
        for j in range(len(traveling_population[0])):
            if traveling_population_totals[i] > 0:
                income_distributions[i][j] = traveling_population[i][j] / traveling_population_totals[i]

    income_distributions_transposed = utils.transpose(income_distributions)

    potencies = results if results is not None else DataSource(config, DataType.DESTINATIONS)

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=utils.FLOAT_DTYPE,
            scenario=scenario,
            group=motive_name,
            modifier="alleen_autobezit" if car_possession_group == "alleen autobezit" else "",
            has_id_column=True,
        )

        distribution_matrix_transpose = utils.transpose(distribution_matrix)

        for part_of_day in part_of_days:
            for i_income_group, income_group in enumerate(income_groups):
                if selected_income is not None and income_group != selected_income:
                    continue
                destinations_for_income = np.asarray(destinations[i_income_group], dtype=utils.FLOAT_DTYPE)

                incomes = np.asarray(income_distributions_transposed[i_income_group], dtype=utils.FLOAT_DTYPE)
                general_possibility_totals = []

                for modality in modalities:
                    possibility_sum = np.zeros(len(destinations_segs), dtype=utils.FLOAT_DTYPE)
                    possibility_vectors = {}

                    for i_group, group in enumerate(groups):
                        distribution = np.asarray(distribution_matrix_transpose[i_group], dtype=utils.FLOAT_DTYPE)

                        income = utils.group_income_level(group)
                        if income_group == income or income_group == "alle":
                            K = electric_percentage.get(income_group) / 100
                            weights, weight_key, electric_key = weight_matrix_request(
                                single_weights,
                                combined_weights,
                                group,
                                modality,
                                motive_name,
                                regime,
                                part_of_day,
                                income,
                                K,
                            )
                            cache_key = (weights is combined_weights, weight_key, electric_key, K)
                            if cache_key not in possibility_vectors:
                                matrix = get_weight_matrix(
                                    single_weights,
                                    combined_weights,
                                    group,
                                    modality,
                                    motive_name,
                                    regime,
                                    part_of_day,
                                    income,
                                    K,
                                )
                                possibility_vectors[cache_key] = matrix @ destinations_for_income

                            # section D4: compute reachable opportunities via origin-destination weights and destination totals.
                            # - `matrix` corresponds to $G_{ghbvm}$
                            # - `destinations_for_income` corresponds to $A_{ib}$ (chosen by motive)
                            # The matrix-vector product yields $\sum_b G_{ghbvm} \cdot A_{ib}$ per origin zone $h$.
                            possibility = possibility_vectors[cache_key]

                            # D4: apply group size/share in the origin zone.
                            # This corresponds to multiplying by $V_{gh}$ to obtain $B_{ghv}$ for the current group.
                            # Since the 'distribution' is a distribution of the whole target population over groups (e.g. WelAuto_vkAuto_laag, WelAuto_vkFiets_hoog)
                            # and here we need the distribution on a specific income group (e.g. laag), we need to divide by the share of the income group in the total population
                            possibility = possibility * distribution
                            np.divide(possibility, incomes, where=incomes != 0, out=possibility)
                            possibility[incomes <= 0] = 0

                            # Sum contributions of all groups that belong to the selected `income_group`, this computes B_{ihv}
                            possibility_sum += possibility

                    key = DataKey(
                        utils.INCOME_VECTOR_RESULT_ID,
                        part_of_day=part_of_day,
                        income=income_group,
                        group=car_possession_group,
                        motive=motive_name,
                        modality=modality,
                        is_intermediate=True,
                    )
                    potencies.set(key, possibility_sum)
                    general_possibility_totals.append(potencies.get(key))

                general_possibility_totals_transposed = utils.transpose(general_possibility_totals)
                general_possibility_totals_transposed = np.round(general_possibility_totals_transposed).astype(int)

                key = DataKey(
                    "Ontpl_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    income=income_group,
                    motive=motive_name,
                    header=modalities,
                )
                potencies.set(key, general_possibility_totals_transposed)

    if selected_income is None:
        assemble_destination_outputs(config, potencies)
    return potencies


def assemble_destination_outputs(config, potencies: DataSource):
    project = config["project"]
    population = SegsSource(config).read(
        Path(project["motief"]["reizende populatie"]).name, scenario=project["verstedelijkingsscenario"]
    )
    for key, values in assemble_income_tables(potencies, project["welke_inkomensgroepen"]):
        # Rename the per income group result for output
        total_id = "Ontpl_totaal"
        potencies.set(replace(key, id=total_id), np.round(values).astype(int))
        # Section D4 of the algorithm region result is a population-weighted average of reachability
        # Store the per-zone numerator contribution here. Regional summation and division by total population could happen later.
        potencies.set(replace(key, id=f"{total_id}product"), np.round(values * population).astype(int))
