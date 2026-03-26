import logging
from pathlib import Path

import numpy as np

import ikob.utils as utils
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def compute_income_distributions(citizens_or_destinations):
    totals = [sum(row) for row in citizens_or_destinations]

    income_distributions = np.zeros((len(citizens_or_destinations), len(citizens_or_destinations[0])))
    for i in range(len(citizens_or_destinations)):
        for j in range(len(citizens_or_destinations[0])):
            if totals[i] > 0:
                income_distributions[i][j] = citizens_or_destinations[i][j] / totals[i]

    return income_distributions


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
    preference = utils.find_preference(group, modality)

    if modality == "Fiets" or modality == "EFiets":
        preference_bike = "Fiets" if preference == "Fiets" else ""
        key = DataKey(
            f"{modality}_vk",
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            preference=preference_bike,
            income=income,
        )
        return single_weights.get(key)

    single_group = utils.single_group(modality, group)
    combined_group = utils.combined_group(modality, group)

    if modality == "Auto" and "WelAuto" in group or combined_group[0] == "A":
        subtopic = "" if modality == "Auto" else "combinaties"
        weights = single_weights if modality == "Auto" else combined_weights
        string = single_group if modality == "Auto" else combined_group
        key = DataKey(
            f"{string}_vk",
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            preference=preference,
            income=income,
            subtopic=subtopic,
            fuel_kind="fossiel",
        )
        matrix_fossil = weights.get(key)

        key = DataKey(
            f"{string}_vk",
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            preference=preference,
            income=income,
            subtopic=subtopic,
            fuel_kind="elektrisch",
        )
        matrix_electric = weights.get(key)
        return ratio_electric * matrix_electric + (1 - ratio_electric) * matrix_fossil

    if modality == "Auto" or modality == "OV":
        key = DataKey(
            f"{single_group}_vk",
            part_of_day=part_of_day,
            regime=regime,
            motive=motive,
            preference=preference,
            income=income,
        )
        return single_weights.get(key)

    key = DataKey(
        f"{combined_group}_vk",
        part_of_day=part_of_day,
        regime=regime,
        motive=motive,
        preference=preference,
        income=income,
        subtopic="combinaties",
    )
    return combined_weights.get(key)


def competition_on_destinations(
    config, single_weights: DataSource, combined_weights: DataSource, origins: DataSource
) -> DataSource:
    """
    For every zone it's determined if the zone has a (dis)advantage compared to other zones in reaching destinations.

    Corresponds to section D6 in the IKOB-algorithm.pdf.

    D6 defines a competition factor residents that discounts
    destinations with many competing residents.
    """
    logger.info("Starting step: Compute competition on destinations")
    return competition(config, single_weights, combined_weights, origins, citizens=False)


def competition_on_citizens(
    config, single_weights: DataSource, combined_weights: DataSource, origins: DataSource
) -> DataSource:
    """
    For every zone it's determined if the zone has a (dis)advantage compared to other zones in attracting citizens.

    Corresponds to section D7 in the IKOB-algorithm.pdf.

    D7 is the "mirror" of D6: it defines a competition factor for jobs/destinations that discounts
    origins with many competing jobs/destinations.
    """
    logger.info("Starting step: Compute competition on citizens")
    return competition(config, single_weights, combined_weights, origins, citizens=True)


def competition(
    config, single_weights: DataSource, combined_weights: DataSource, origins: DataSource, citizens: bool = True
) -> DataSource:
    if citizens:
        msg = "Competition for citizens."
    else:
        msg = "Competition for destinations."
    logger.info(msg)

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
    electric_percentage = distribution_config["Percelektrisch"]

    groups = [
        "GratisAuto_laag",
        "GratisAuto_GratisOV_laag",
        "WelAuto_GratisOV_laag",
        "WelAuto_vkAuto_laag",
        "WelAuto_vkNeutraal_laag",
        "WelAuto_vkFiets_laag",
        "WelAuto_vkOV_laag",
        "GeenAuto_GratisOV_laag",
        "GeenAuto_vkNeutraal_laag",
        "GeenAuto_vkFiets_laag",
        "GeenAuto_vkOV_laag",
        "GeenRijbewijs_GratisOV_laag",
        "GeenRijbewijs_vkNeutraal_laag",
        "GeenRijbewijs_vkFiets_laag",
        "GeenRijbewijs_vkOV_laag",
        "GratisAuto_middellaag",
        "GratisAuto_GratisOV_middellaag",
        "WelAuto_GratisOV_middellaag",
        "WelAuto_vkAuto_middellaag",
        "WelAuto_vkNeutraal_middellaag",
        "WelAuto_vkFiets_middellaag",
        "WelAuto_vkOV_middellaag",
        "GeenAuto_GratisOV_middellaag",
        "GeenAuto_vkNeutraal_middellaag",
        "GeenAuto_vkFiets_middellaag",
        "GeenAuto_vkOV_middellaag",
        "GeenRijbewijs_GratisOV_middellaag",
        "GeenRijbewijs_vkNeutraal_middellaag",
        "GeenRijbewijs_vkFiets_middellaag",
        "GeenRijbewijs_vkOV_middellaag",
        "GratisAuto_middelhoog",
        "GratisAuto_GratisOV_middelhoog",
        "WelAuto_GratisOV_middelhoog",
        "WelAuto_vkAuto_middelhoog",
        "WelAuto_vkNeutraal_middelhoog",
        "WelAuto_vkFiets_middelhoog",
        "WelAuto_vkOV_middelhoog",
        "GeenAuto_GratisOV_middelhoog",
        "GeenAuto_vkNeutraal_middelhoog",
        "GeenAuto_vkFiets_middelhoog",
        "GeenAuto_vkOV_middelhoog",
        "GeenRijbewijs_GratisOV_middelhoog",
        "GeenRijbewijs_vkNeutraal_middelhoog",
        "GeenRijbewijs_vkFiets_middelhoog",
        "GeenRijbewijs_vkOV_middelhoog",
        "GratisAuto_hoog",
        "GratisAuto_GratisOV_hoog",
        "WelAuto_GratisOV_hoog",
        "WelAuto_vkAuto_hoog",
        "WelAuto_vkNeutraal_hoog",
        "WelAuto_vkFiets_hoog",
        "WelAuto_vkOV_hoog",
        "GeenAuto_GratisOV_hoog",
        "GeenAuto_vkNeutraal_hoog",
        "GeenAuto_vkFiets_hoog",
        "GeenAuto_vkOV_hoog",
        "GeenRijbewijs_GratisOV_hoog",
        "GeenRijbewijs_vkNeutraal_hoog",
        "GeenRijbewijs_vkFiets_hoog",
        "GeenRijbewijs_vkOV_hoog",
    ]

    modalities = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]
    income_groups = ["laag", "middellaag", "middelhoog", "hoog"]
    headstring = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)
    destinations = segs_source.read(destinations_path.name, scenario=scenario)

    income_distributions = compute_income_distributions(traveling_population if citizens else destinations)
    subtopic_competition = "inwoners" if citizens else "bestemmingen"
    # Matches the suffix in potential_companies.py and employment_opportunities.py
    competition_filename_suffix = "Pot" if citizens else "Ontpl"
    competitions = DataSource(config, DataType.COMPETITION)

    if citizens:
        citizens_or_destinations = traveling_population
    else:
        citizens_or_destinations = destinations

    num_zones = len(citizens_or_destinations)

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=float,
            scenario=scenario,
            group=motive_name,
            modifier="alleen_autobezit" if car_possession_group == "alleen autobezit" else "",
            has_index_column=True,
        )

        for part_of_day in part_of_days:
            for i_income_group, income_group in enumerate(income_groups):
                general_possibility_totals = []

                for modality in modalities:
                    key = DataKey(
                        "Totaal",
                        part_of_day=part_of_day,
                        motive=motive_name,
                        modality=modality,
                        income=income_group,
                        group=car_possession_group,
                    )
                    reach = origins.get(key)

                    # Section D6/D7: `reach` is the previously computed reachability used as denominator.
                    # - citizens=False (D6 / competition_on_destinations): `reach` comes from D5 / reachable_population and is destination-side potential (how many
                    #   residents can reach each destination zone).
                    # - citizens=True  (D7 / competition_on_citizens): `reach` comes from D4 / reachable_destinations and is origin-side reachable opportunities
                    #   (how many jobs/places residents in an origin zone can reach).

                    competition_total = np.zeros(len(citizens_or_destinations))

                    for i_group, group in enumerate(groups):
                        distribution = distribution_matrix[:, i_group]
                        income_distribution = income_distributions[:, i_income_group]

                        income = utils.group_income_level(group)
                        if income_group == income or income_group == "alle":
                            K = electric_percentage.get(income_group) / 100
                            matrix = get_weight_matrix(
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

                            # Section D6/D7 competition term:
                            # Compute a scarcity/competition ratio per zone and propagate it through the origin-destination weights.
                            # - citizens=False (D6 / competition_on_destinations): `citizens_or_destinations` is $A_{ib}$ (jobs/places per
                            #   destination). Dividing by `reach` discounts destinations with many competing residents.
                            # - citizens=True  (D7 / competition_on_citizens): `citizens_or_destinations` is $I_{ih}$ (residents per
                            #   origin). Dividing by `reach` discounts origins with many reachable opportunities.
                            competition = matrix @ (
                                citizens_or_destinations.T[i_income_group] / np.where(reach > 0, reach, 1.0)
                            )

                            # aggregation to income-class level:
                            # We sum across all groups whose income level matches `income_group`.
                            # The `distribution` and `income_distribution` scaling makes this an income-class level
                            # score rather than a raw per-group score.
                            competition_total += (
                                competition * distribution / np.where(income_distribution > 0, income_distribution, 1)
                            )

                    key = DataKey(
                        id="Totaal",
                        part_of_day=part_of_day,
                        subtopic=subtopic_competition,
                        income=income_group,
                        motive=motive_name,
                        modality=modality,
                        group=car_possession_group,
                        is_temporary=True,
                    )
                    competitions.set(key, competition_total.copy())

                    general_possibility_totals.append(competitions.get(key))
                    general_totals_transpose = utils.transpose(general_possibility_totals)
                    key = DataKey(
                        id=f"{competition_filename_suffix}_conc",
                        part_of_day=part_of_day,
                        subtopic=subtopic_competition,
                        income=income_group,
                        motive=motive_name,
                        group=car_possession_group,
                        index=DataKey.zone_index(num_zones),
                    )
                    competitions.write_csv(general_totals_transpose, key, header=headstring)

            header = ["laag", "middellaag", "middelhoog", "hoog"]
            for modality in modalities:
                general_matrix_product = []
                general_matrix = []
                for income_group in income_groups:
                    key = DataKey(
                        "Totaal",
                        part_of_day=part_of_day,
                        motive=motive_name,
                        modality=modality,
                        income=income_group,
                        subtopic=subtopic_competition,
                        group=car_possession_group,
                    )
                    general_matrix.append(competitions.get(key))
                general_totals_transpose = utils.transpose(general_matrix)

                for i in range(len(citizens_or_destinations)):
                    general_matrix_product.append([])
                    for j in range(len(citizens_or_destinations[0])):
                        if (citizens and (destinations[i][j] > 0)) or (
                            (not citizens) and (traveling_population[i, j] > 0)
                        ):
                            general_matrix_product[i].append(
                                general_totals_transpose[i][j] * citizens_or_destinations[i][j]
                            )
                        else:
                            general_matrix_product[i].append(0)

                key = DataKey(
                    id=f"{competition_filename_suffix}_conc",
                    part_of_day=part_of_day,
                    subtopic=subtopic_competition,
                    motive=motive_name,
                    modality=modality,
                    group=car_possession_group,
                    index=DataKey.zone_index(num_zones),
                )
                competitions.write_csv(general_totals_transpose, key, header=header)

                key = DataKey(
                    id=f"{competition_filename_suffix}_concproduct",
                    part_of_day=part_of_day,
                    subtopic=subtopic_competition,
                    motive=motive_name,
                    modality=modality,
                    group=car_possession_group,
                    index=DataKey.zone_index(num_zones),
                )
                competitions.write_csv(general_matrix_product, key, header=header)

    return competitions
