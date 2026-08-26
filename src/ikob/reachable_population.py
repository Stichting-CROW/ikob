import logging
from pathlib import Path

import numpy as np
import numpy.typing as npt

from ikob import utils
from ikob.datasource import DataKey, DataSource, DataType, SegsSource
from ikob.generalized_travel_time import weight_matrix_recipes

logger = logging.getLogger(__name__)


def _compute_modality_working_population(
    modality,
    groups,
    income_group,
    part_of_day,
    regimes,
    motive_name,
    single_weights,
    combined_weights,
    citizens_transpose,
    electric_percentage,
    fuel_kinds,
    num_working_population,
):
    # This computes the sum over all groups of weight_matrix(modality, group) @ population(group).
    # The weight matrix of many groups is equal for a given modality. E.g. the "GratisOV" part of a
    # group name is irrelevant to a modality that doesn't involve OV.
    # So for each weight matrix (identified by a data source and a data key) we can first sum the population
    # and then do a single matrix multiplication with the weight matrix.

    # Some modalities are split in multiple sub modalities (specifically the car is split in fossil and electric cars)
    # each of which comes with a weight.

    weighted_vectors_by_key: dict[tuple[str, DataKey], npt.NDArray] = {}
    for group_idx, group in enumerate(groups):
        income = utils.group_income_level(group)
        if income_group != income and income_group != "alle":
            continue

        recipes = weight_matrix_recipes(
            group, modality, motive_name, regimes, part_of_day, income, electric_percentage.get(income_group)
        )

        for source, key, citizen_weight in recipes:
            weighted_vector = citizen_weight * citizens_transpose[group_idx]
            existing = weighted_vectors_by_key.get((source, key))
            weighted_vectors_by_key[(source, key)] = weighted_vector if existing is None else existing + weighted_vector

    working_population_list = utils.zeros(num_working_population)
    for (source, key), weighted_vector in weighted_vectors_by_key.items():
        weights_source = single_weights if source == "single" else combined_weights
        # Get the transpose because normally the weights are indexed [origin, destination].
        matrix = weights_source.get(key).T
        # section D5: $B_{gbv} = \sum_h I_{gh} \cdot G_{ghbvm}$, batched across groups sharing a matrix.
        working_population_list += matrix @ weighted_vector

    return working_population_list


def create_citizens_file(distribution_matrix, working_population):
    return np.asarray(working_population)[:, np.newaxis] * np.asarray(distribution_matrix)


def calculate_reachable_population(config, single_weights: DataSource, combined_weights: DataSource) -> DataSource:
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
    destinations_path = Path(project_config["motief"]["bestemmingsplaatsen"])
    car_possession_groups = advanced_config["welke_groepen"]
    income_groups = project_config["welke_inkomensgroepen"]
    fuel_kinds = ["fossiel", "elektrisch"]
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
    headstring = modalities

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)
    destinations = segs_source.read(destinations_path.name, scenario=scenario)

    num_zones = len(traveling_population)

    working_population = []

    working_population = np.asarray(traveling_population, dtype=utils.FLOAT_DTYPE).sum(axis=1)

    # section D5: derive group sizes $I_{gh}$ per origin zone by distributing the origin-zone working population
    # over groups using the SEG distribution matrix.

    origins = DataSource(config, DataType.ORIGINS)

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=utils.FLOAT_DTYPE,
            scenario=scenario,
            group=motive_name,
            modifier="alleen_autobezit" if car_possession_group == "alleen autobezit" else "",
            has_index_column=True,
        )

        citizens = create_citizens_file(distribution_matrix, working_population)
        citizens_transpose = utils.transpose(citizens)

        for part_of_day in part_of_days:
            for income_group in income_groups:
                general_possibility_totals = []
                for modality in modalities:
                    working_population_list = _compute_modality_working_population(
                        modality,
                        groups,
                        income_group,
                        part_of_day,
                        regimes,
                        motive_name,
                        single_weights,
                        combined_weights,
                        citizens_transpose,
                        electric_percentage,
                        fuel_kinds,
                        len(working_population),
                    )

                    key = DataKey(
                        id="Totaal",
                        part_of_day=part_of_day,
                        group=car_possession_group,
                        income=income_group,
                        motive=motive_name,
                        modality=modality,
                        is_temporary=True,
                    )
                    origins.set(key, working_population_list)
                    general_possibility_totals.append(origins.get(key))

                key = DataKey(
                    id="Pot_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    income=income_group,
                    motive=motive_name,
                    index=DataKey.zone_index(num_zones),
                    header=headstring,
                )

                origins_total = utils.transpose(general_possibility_totals)
                origins_total = np.round(origins_total).astype(int)
                origins.set(key, origins_total)

            header = ["laag", "middellaag", "middelhoog", "hoog"]
            for modality in modalities:
                general_matrix = []
                for income_group in income_groups:
                    key = DataKey(
                        "Totaal",
                        part_of_day=part_of_day,
                        income=income_group,
                        motive=motive_name,
                        group=car_possession_group,
                        modality=modality,
                        subtopic="",
                    )
                    total_row = origins.get(key)

                    general_matrix.append(total_row)
                general_total_transpose = utils.transpose(general_matrix)
                general_matrix_product = general_total_transpose * destinations

                general_total_transpose = np.round(general_total_transpose).astype(int)
                key = DataKey(
                    id="Pot_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    motive=motive_name,
                    modality=modality,
                    index=DataKey.zone_index(num_zones),
                    header=header,
                )
                origins.set(key, general_total_transpose)

                # Section D5 regional aggregation note:
                # The PDF defines $B_{irv}$ as a jobs-weighted aggregation over destination zones in a region.
                # Here `Pot_totaalproduct` prepares the numerator term $B_{ibv} \cdot A_{ib}$ by multiplying
                # the destination-level reach (`general_total_transpose`) by the number of jobs/pupil-places
                # in that destination zone (`destinations`).

                key = DataKey(
                    id="Pot_totaalproduct",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    motive=motive_name,
                    modality=modality,
                    index=DataKey.zone_index(num_zones),
                    header=header,
                )
                origins.set(key, np.asarray(general_matrix_product))

    return origins
