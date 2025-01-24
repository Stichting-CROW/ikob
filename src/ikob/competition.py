import logging

import numpy as np

import ikob.utils as utils
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def get_weight_matrix(
        single_weights: DataSource,
        combined_weights: DataSource,
        group,
        modality,
        motive,
        regime,
        part_of_day,
        income,
        income_group,
        ratio_electric: float):
    preference = utils.find_preference(group, modality)

    if modality == 'Fiets' or modality == 'EFiets':
        preference_bike = 'Fiets' if preference == 'Fiets' else ''
        key = DataKey(f"{modality}_vk",
                      part_of_day=part_of_day,
                      regime=regime,
                      motive=motive,
                      preference=preference_bike)
        return single_weights.get(key)

    single_group = utils.single_group(modality, group)
    combined_group = utils.combined_group(modality, group)

    if modality == 'Auto' and 'WelAuto' in group or combined_group[0] == 'A':
        subtopic = '' if modality == 'Auto' else 'combinaties'
        weights = single_weights if modality == 'Auto' else combined_weights
        string = single_group if modality == 'Auto' else combined_group
        key = DataKey(f"{string}_vk",
                      part_of_day=part_of_day,
                      regime=regime,
                      motive=motive,
                      preference=preference,
                      income=income,
                      subtopic=subtopic,
                      fuel_kind="fossiel")
        matrix_fossil = weights.get(key)

        key = DataKey(f"{string}_vk",
                      part_of_day=part_of_day,
                      regime=regime,
                      motive=motive,
                      preference=preference,
                      income=income,
                      subtopic=subtopic,
                      fuel_kind="elektrisch")
        matrix_electric = weights.get(key)
        return ratio_electric * matrix_electric + \
            (1 - ratio_electric) * matrix_fossil

    if modality == 'Auto' or modality == 'OV':
        key = DataKey(f"{single_group}_vk",
                      part_of_day=part_of_day,
                      regime=regime,
                      motive=motive,
                      preference=preference,
                      income=income)
        return single_weights.get(key)

    key = DataKey(f"{combined_group}_vk",
                  part_of_day=part_of_day,
                  regime=regime,
                  motive=motive,
                  preference=preference,
                  income=income,
                  subtopic="combinaties")
    return combined_weights.get(key)


def competition_on_jobs(config,
                        single_weights: DataSource,
                        combined_weights: DataSource,
                        origins: DataSource) -> DataSource:
    return competition(
        config,
        single_weights,
        combined_weights,
        origins,
        citizens=False)


def competition_on_citizens(config,
                            single_weights: DataSource,
                            combined_weights: DataSource,
                            origins: DataSource) -> DataSource:
    return competition(
        config,
        single_weights,
        combined_weights,
        origins,
        citizens=True)


def competition(config,
                single_weights: DataSource,
                combined_weights: DataSource,
                origins: DataSource,
                citizens: bool = True) -> DataSource:
    if citizens:
        msg = "Competition for companies and accessiblity."
    else:
        msg = "Competition for places of employment."
    logger.info(msg)

    project_config = config['project']
    skims_config = config['skims']
    distribution_config = config['verdeling']
    part_of_days = skims_config['dagsoort']
    advanced_config = config['geavanceerd']

    scenario = project_config['verstedelijkingsscenario']
    regimes = project_config['beprijzingsregime']
    motives = project_config['motieven']
    car_possession_groups = advanced_config['welke_groepen']
    electric_percentage = distribution_config['Percelektrisch']

    income_groups = ['laag', 'middellaag', 'middelhoog', 'hoog']

    # Vaste waarden
    base_groups = [
            'GratisAuto',
            'GratisAuto_GratisOV',
            'WelAuto_GratisOV',
            'WelAuto_vkAuto',
            'WelAuto_vkNeutraal',
            'WelAuto_vkFiets',
            'WelAuto_vkOV',
            'GeenAuto_GratisOV',
            'GeenAuto_vkNeutraal',
            'GeenAuto_vkFiets',
            'GeenAuto_vkOV',
            'GeenRijbewijs_GratisOV',
            'GeenRijbewijs_vkNeutraal',
            'GeenRijbewijs_vkFiets',
            'GeenRijbewijs_vkOV']

    groups = []
    for income_group in income_groups:
        for base_group in base_groups:
            groups.append(f'{base_group}_{income_group}')

    modalities = [
        'Fiets',
        'Auto',
        'OV',
        'Auto_Fiets',
        'OV_Fiets',
        'Auto_OV',
        'Auto_OV_Fiets']
    income_groups = ['laag', 'middellaag', 'middelhoog', 'hoog']
    headstring = [
        'Fiets',
        'Auto',
        'OV',
        'Auto_Fiets',
        'OV_Fiets',
        'Auto_OV',
        'Auto_OV_Fiets']
    headstringExcel = [
        'Zone',
        'Fiets',
        'Auto',
        'OV',
        'Auto-Fiets'
        'OV_Fiets',
        'Auto_OV',
        'Auto_OV_Fiets']

    segs_source = SegsSource(config)

    if 'winkelnietdagelijksonderwijs' in motives:
        citizens_per_class = segs_source.read(
            "Leerlingen", scenario=scenario, type_caster=float)
        places_of_employment = segs_source.read(
            "Leerlingenplaatsen", scenario=scenario, type_caster=float)
    else:
        citizens_per_class = segs_source.read(
            "Beroepsbevolking_inkomensklasse",
            scenario=scenario,
            type_caster=float)
        places_of_employment = segs_source.read(
            "Arbeidsplaatsen_inkomensklasse",
            scenario=scenario,
            type_caster=float)

    citizens_totals = [sum(ipk) for ipk in citizens_per_class]

    income_distributions = np.zeros(
        (len(citizens_per_class), len(
            citizens_per_class[0])))
    for i in range(len(citizens_per_class)):
        for j in range(len(citizens_per_class[0])):
            if citizens_totals[i] > 0:
                income_distributions[i][j] = citizens_per_class[i][j] / \
                    citizens_totals[i]

    subtopic_competition = "inwoners" if citizens else "arbeidsplaatsen"
    competitions = DataSource(config, DataType.COMPETITION)

    for car_possession_group in car_possession_groups:
        for motive in motives:
            if motive == 'werk':
                target_group = 'Beroepsbevolking'
            elif motive == 'winkelnietdagelijksonderwijs':
                target_group = 'Leerlingen'
            else:
                target_group = 'Inwoners'

            if car_possession_group == "alle groepen":
                distribution_matrix = segs_source.read(
                    f"Verdeling_over_groepen_{target_group}",
                    scenario=scenario,
                    type_caster=float)
            else:
                distribution_matrix = segs_source.read(
                    f"Verdeling_over_groepen_{target_group}_alleen_autobezit",
                    scenario=scenario,
                    type_caster=float)

            for part_of_day in part_of_days:
                for i_income_group, income_group in enumerate(income_groups):
                    general_possibility_totals = []
                    for modality in modalities:
                        key = DataKey("Totaal",
                                      part_of_day=part_of_day,
                                      motive=motive,
                                      modality=modality,
                                      income=income_group,
                                      group=car_possession_group)
                        reach = origins.get(key)

                        competition_total = np.zeros(len(places_of_employment))
                        for i_group, group in enumerate(groups):
                            if citizens:
                                citizens_or_places_of_employment = citizens_per_class.T[i_income_group]
                            else:
                                citizens_or_places_of_employment = places_of_employment.T[i_income_group]
                            distribution = distribution_matrix[:, i_group]
                            income_distribution = income_distributions[:,
                                                                       i_income_group]

                            income = utils.group_income_level(group)
                            if income_group == income or income_group == 'alle':
                                K = electric_percentage.get(income_group) / 100
                                matrix = get_weight_matrix(
                                    single_weights,
                                    combined_weights,
                                    group,
                                    modality,
                                    motive,
                                    regimes,
                                    part_of_day,
                                    income,
                                    income_group,
                                    K)

                                competition = matrix @ (
                                    citizens_or_places_of_employment /
                                    np.where(
                                        reach > 0,
                                        reach,
                                        1.0))
                                competition_total += competition * distribution / \
                                    np.where(income_distribution > 0, income_distribution, 1)

                        key = DataKey(id='Totaal',
                                      part_of_day=part_of_day,
                                      subtopic=subtopic_competition,
                                      income=income_group,
                                      motive=motive,
                                      modality=modality)
                        competitions.set(key, competition_total.copy())

                        general_possibility_totals.append(
                            competitions.get(key))
                        general_totals_transpose = utils.transpose(
                            general_possibility_totals)
                        key = DataKey(id='Ontpl_conc',
                                      part_of_day=part_of_day,
                                      subtopic=subtopic_competition,
                                      income=income_group,
                                      motive=motive)
                        competitions.write_csv(
                            general_totals_transpose, key, header=headstring)
                        competitions.write_xlsx(
                            general_totals_transpose, key, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for modality in modalities:
                    general_matrix_product = []
                    general_matrix = []
                    for income_group in income_groups:
                        key = DataKey("Totaal",
                                      part_of_day=part_of_day,
                                      motive=motive,
                                      modality=modality,
                                      income=income_group,
                                      subtopic=subtopic_competition)
                        general_matrix.append(competitions.get(key))
                        general_totals_transpose = utils.transpose(
                            general_matrix)

                    for i in range(len(citizens_per_class)):
                        general_matrix_product.append([])
                        for j in range(len(citizens_per_class[0])):
                            if citizens_per_class[i][j] > 0:
                                general_matrix_product[i].append(
                                    general_totals_transpose[i][j] * citizens_per_class[i][j])
                            else:
                                general_matrix_product[i].append(0)

                    key = DataKey(id='Ontpl_conc',
                                  part_of_day=part_of_day,
                                  subtopic=subtopic_competition,
                                  motive=motive,
                                  modality=modality)
                    competitions.write_xlsx(
                        general_totals_transpose, key, header=header)

                    key = DataKey(id='Ontpl_concproduct',
                                  part_of_day=part_of_day,
                                  subtopic=subtopic_competition,
                                  motive=motive,
                                  modality=modality)
                    competitions.write_xlsx(
                        general_matrix_product, key, header=header)

    return competitions
