import logging
from pathlib import Path

import numpy as np

import ikob.utils as utils
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def create_citizens_file(distribution_matrix, working_population):
    citizens_file = []
    for i in range(len(working_population)):
        citizens_file.append([])
        for j in range(len(distribution_matrix[0])):
            citizens_file[i].append(working_population[i] * distribution_matrix[i][j])
    return citizens_file


def reachable_population(config, single_weights: DataSource, combined_weights: DataSource) -> DataSource:
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

    for i in range(len(traveling_population)):
        working_population.append(sum(traveling_population[i]))

    # section D5: derive group sizes $I_{gh}$ per origin zone by distributing the origin-zone working population
    # over groups using the SEG distribution matrix.

    origins = DataSource(config, DataType.ORIGINS)

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=float,
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
                    working_population_list = utils.zeros(len(working_population))
                    for igroup, group in enumerate(groups):
                        income = utils.group_income_level(group)
                        if income_group == income or income_group == "alle":
                            preference = utils.find_preference(group, modality)
                            if modality == "Fiets" or modality == "EFiets":
                                if preference == "Fiets":
                                    tmp_preference = "Fiets"
                                else:
                                    tmp_preference = ""

                                key = DataKey(
                                    f"{modality}_vk",
                                    part_of_day=part_of_day,
                                    preference=tmp_preference,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                )
                                bike_matrix = single_weights.get(key).T

                                # section D5: $B_{gbv} = \sum_h I_{gh} \cdot G_{ghbvm}$.
                                working_population_list += bike_matrix @ citizens_transpose[igroup]

                            elif modality == "Auto":
                                string = utils.single_group(modality, group)
                                if "WelAuto" in group:
                                    for fuel_kind in fuel_kinds:
                                        key = DataKey(
                                            f"{string}_vk",
                                            part_of_day=part_of_day,
                                            preference=preference,
                                            income=income,
                                            regime=regimes,
                                            motive=motive_name,
                                            fuel_kind=fuel_kind,
                                        )
                                        matrix = single_weights.get(key).T

                                        if fuel_kind == "elektrisch":
                                            K = electric_percentage.get(income_group) / 100
                                        else:
                                            K = 1 - electric_percentage.get(income_group) / 100

                                        # section D5: same $\sum_h I_{gh} \cdot G_{ghbvm}$ computation, with fuel share K.
                                        working_population_list += K * matrix @ citizens_transpose[igroup]
                                else:
                                    key = DataKey(
                                        f"{string}_vk",
                                        part_of_day=part_of_day,
                                        preference=preference,
                                        income=income,
                                        regime=regimes,
                                        motive=motive_name,
                                    )
                                    matrix = single_weights.get(key).T

                                    # section D5: $\sum_h I_{gh} \cdot G_{ghbvm}$ for auto groups without fuel split.
                                    working_population_list += matrix @ citizens_transpose[igroup]

                            elif modality == "OV":
                                string = utils.single_group(modality, group)
                                key = DataKey(
                                    f"{string}_vk",
                                    part_of_day=part_of_day,
                                    preference=preference,
                                    income=income,
                                    regime=regimes,
                                    motive=motive_name,
                                )
                                matrix = single_weights.get(key).T

                                # section D5: $\sum_h I_{gh} \cdot G_{ghbvm}$ for OV.
                                working_population_list += matrix @ citizens_transpose[igroup]
                            else:
                                string = utils.combined_group(modality, group)
                                logger.debug("de gr is %s", group)
                                logger.debug("de string is %s", string)
                                if string[0] == "A":
                                    # Its a group with auto, so we need to split by fuel kind
                                    for fuel_kind in fuel_kinds:
                                        key = DataKey(
                                            f"{string}_vk",
                                            part_of_day=part_of_day,
                                            preference=preference,
                                            income=income,
                                            regime=regimes,
                                            motive=motive_name,
                                            subtopic="combinaties",
                                            fuel_kind=fuel_kind,
                                        )
                                        matrix = combined_weights.get(key).T

                                        if fuel_kind == "elektrisch":
                                            K = electric_percentage.get(income_group) / 100
                                        else:
                                            K = 1 - electric_percentage.get(income_group) / 100

                                        # section D5: combined-mode $\sum_h I_{gh} \cdot G_{ghbvm}$, with fuel share K.
                                        working_population_list += K * matrix @ citizens_transpose[igroup]

                                else:
                                    key = DataKey(
                                        f"{string}_vk",
                                        part_of_day=part_of_day,
                                        preference=preference,
                                        income=income,
                                        regime=regimes,
                                        motive=motive_name,
                                        subtopic="combinaties",
                                    )
                                    matrix = combined_weights.get(key).T

                                    # section D5: combined-mode $\sum_h I_{gh} \cdot G_{ghbvm}$.
                                    working_population_list += matrix @ citizens_transpose[igroup]

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
                )

                origins_total = utils.transpose(general_possibility_totals)
                origins_total = np.round(origins_total).astype(int)
                origins.write_csv(origins_total, key, header=headstring)

            header = ["laag", "middellaag", "middelhoog", "hoog"]
            for modality in modalities:
                general_matrix_product = []
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
                for i in range(len(destinations)):
                    general_matrix_product.append([])
                    for j in range(len(destinations[0])):
                        if destinations[i][j] > 0:
                            general_matrix_product[i].append(general_total_transpose[i][j] * destinations[i][j])
                        else:
                            general_matrix_product[i].append(0)

                general_total_transpose = np.round(general_total_transpose).astype(int)
                key = DataKey(
                    id="Pot_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    motive=motive_name,
                    modality=modality,
                    index=DataKey.zone_index(num_zones),
                )
                origins.write_csv(general_total_transpose, key, header=header)

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
                )
                origins.write_csv(general_matrix_product, key, header=header)

    return origins
