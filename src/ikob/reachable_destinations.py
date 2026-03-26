import logging
from pathlib import Path

import numpy as np

import ikob.utils as utils
from ikob.competition import get_weight_matrix
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def reachable_destinations(config, single_weights: DataSource, combined_weights: DataSource) -> DataSource:
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
    headstring = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)
    destinations_segs = segs_source.read(destinations_path.name, scenario=scenario)
    destinations = utils.transpose(destinations_segs)

    num_zones = len(destinations_segs)

    traveling_population_totals = [sum(bbpk) for bbpk in traveling_population]

    income_distributions = np.zeros((len(traveling_population), len(traveling_population[0])))
    for i in range(len(traveling_population)):
        for j in range(len(traveling_population[0])):
            if traveling_population_totals[i] > 0:
                income_distributions[i][j] = traveling_population[i][j] / traveling_population_totals[i]

    income_distributions_transposed = utils.transpose(income_distributions)

    potencies = DataSource(config, DataType.DESTINATIONS)

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=float,
            scenario=scenario,
            group=motive_name,
            modifier="alleen_autobezit" if car_possession_group == "alleen autobezit" else "",
            has_index_column=True,
        )

        distribution_matrix_transpose = utils.transpose(distribution_matrix)

        for part_of_day in part_of_days:
            for i_income_group, income_group in enumerate(income_groups):
                destinations_for_income = np.array(destinations[i_income_group])

                incomes = np.array(income_distributions_transposed[i_income_group])
                general_possibility_totals = []

                for modality in modalities:
                    possibility_sum = np.zeros(len(destinations_segs))

                    for i_group, group in enumerate(groups):
                        distribution = np.array(distribution_matrix_transpose[i_group])

                        income = utils.group_income_level(group)
                        if income_group == income or income_group == "alle":
                            K = electric_percentage.get(income_group) / 100
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

                            # section D4: compute reachable opportunities via origin-destination weights and destination totals.
                            # - `matrix` corresponds to $G_{ghbvm}$
                            # - `destinations_for_income` corresponds to $A_{ib}$ (chosen by motive)
                            # The matrix-vector product yields $\sum_b G_{ghbvm} \cdot A_{ib}$ per origin zone $h$.
                            possibility = matrix @ destinations_for_income

                            # D4: apply group size/share in the origin zone.
                            # This corresponds to multiplying by $V_{gh}$ to obtain $B_{ghv}$ for the current group.
                            # Since the 'distribution' is a distribution of the whole target population over groups (e.g. WelAuto_vkAuto_laag, WelAuto_vkFiets_hoog)
                            # and here we need the distribution on a specific income group (e.g. laag), we need to divide by the share of the income group in the total population
                            possibility = possibility * distribution
                            possibility = np.divide(possibility, incomes, where=incomes != 0)
                            possibility[incomes <= 0] = 0

                            # Sum contributions of all groups that belong to the selected `income_group`, this computes B_{ihv}
                            possibility_sum += possibility

                    key = DataKey(
                        "Totaal",
                        part_of_day=part_of_day,
                        income=income_group,
                        group=car_possession_group,
                        motive=motive_name,
                        modality=modality,
                        is_temporary=True,
                    )
                    potencies.set(key, possibility_sum.copy())
                    general_possibility_totals.append(potencies.get(key))

                general_possibility_totals_transposed = utils.transpose(general_possibility_totals)
                general_possibility_totals_transposed = np.round(general_possibility_totals_transposed).astype(int)

                key = DataKey(
                    "Ontpl_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    income=income_group,
                    motive=motive_name,
                    index=DataKey.zone_index(num_zones),
                )
                potencies.write_csv(general_possibility_totals_transposed, key, header=headstring)

            header = ["laag", "middellaag", "middelhoog", "hoog"]
            for modality in modalities:
                general_matrix_product = []
                general_matrix = []
                for income_group in income_groups:
                    key = DataKey(
                        "Totaal",
                        part_of_day=part_of_day,
                        income=income_group,
                        group=car_possession_group,
                        motive=motive_name,
                        modality=modality,
                    )
                    totals_row = potencies.get(key)
                    general_matrix.append(totals_row)
                if len(income_groups) > 1:
                    general_possibility_totals_transposed = utils.transpose(general_matrix)
                else:
                    general_possibility_totals_transposed = general_matrix
                for i in range(len(traveling_population)):
                    general_matrix_product.append([])
                    for j in range(len(traveling_population[0])):
                        if traveling_population[i][j] > 0:
                            general_matrix_product[i].append(
                                general_possibility_totals_transposed[i][j] * traveling_population[i][j]
                            )
                        else:
                            general_matrix_product[i].append(0)

                general_possibility_totals_transposed = np.round(general_possibility_totals_transposed).astype(int)
                key = DataKey(
                    "Ontpl_totaal",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    motive=motive_name,
                    modality=modality,
                    index=DataKey.zone_index(num_zones),
                )
                potencies.write_csv(general_possibility_totals_transposed, key, header=header)

                # section D4 regional aggregation note:
                # The PDF defines $B_{irv}$ as a population-weighted aggregation of zone-level reachability
                # $B_{ihv}$ over the zones $h$ that belong to a region $r$:
                #   $B_{irv} = (\sum_{h \in r} B_{ihv} \cdot I_{ih}) / (\sum_{h \in r} I_{ih})$.
                # This function does not explicitly group zones into regions or compute that weighted average.
                # Instead, `Ontpl_totaalproduct` prepares the numerator term $B_{ihv} \cdot I_{ih}$ by
                # multiplying the per-zone reachability by the (income-class) population per zone.
                # The denominator $\sum_{h \in r} I_{ih}$ and the sum in the numerator would need to be applied in a later aggregation step.

                general_matrix_product = np.round(general_matrix_product).astype(int)
                key = DataKey(
                    "Ontpl_totaalproduct",
                    part_of_day=part_of_day,
                    group=car_possession_group,
                    motive=motive_name,
                    modality=modality,
                    index=DataKey.zone_index(num_zones),
                )
                potencies.write_csv(general_matrix_product, key, header=header)

    return potencies
