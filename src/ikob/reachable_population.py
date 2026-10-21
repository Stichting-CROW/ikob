import logging
from dataclasses import replace
from pathlib import Path

import numpy as np

from ikob import utils
from ikob.combined_weights import load_weight_matrix, weight_matrix_request
from ikob.datasource import DataKey, DataSource, DataType, SegsSource
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
    income_groups = project_config["welke_inkomensgroepen"]
    electric_percentage = distribution_config["Percelektrisch"]

    # Vaste waarden
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

    income_groups = ["laag", "middellaag", "middelhoog", "hoog"]

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)

    working_population = []

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
            for income_group in income_groups:
                if selected_income is not None and income_group != selected_income:
                    continue
                general_possibility_totals = []
                for modality in modalities:
                    working_population_list = utils.zeros(len(working_population))

                    for igroup, group in enumerate(groups):
                        income = utils.group_income_level(group)
                        if income_group == income or income_group == "alle":
                            K = electric_percentage.get(income_group) / 100
                            weights, weight_key, electric_key = weight_matrix_request(
                                single_weights,
                                combined_weights,
                                group,
                                modality,
                                motive_name,
                                regimes,
                                part_of_day,
                                income,
                                K,
                            )
                            # Weights are indexed [origin, destination] in D5.
                            working_population_list += (
                                load_weight_matrix(weights, weight_key, electric_key, K).T @ citizens_transpose[igroup]
                            ).T

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
