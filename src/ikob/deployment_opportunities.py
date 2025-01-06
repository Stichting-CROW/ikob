import logging

import numpy as np

import ikob.utils as utils
from ikob.competition import get_weight_matrix
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def deployment_opportunities(config,
                             single_weights: DataSource,
                             combined_weights: DataSource) -> DataSource:
    logger.info("Deployment opportunities for citizens.")

    project_config = config['project']
    skims_config = config['skims']
    distribution_config = config['verdeling']
    part_of_days = skims_config['dagsoort']

    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motives = project_config['motieven']
    car_possession_groups = project_config['welke_groepen']
    income_groups = project_config['welke_inkomensgroepen']
    electric_percentage = distribution_config['Percelektrisch']

    if 'alle groepen' in car_possession_groups:
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
    else:
        base_groups = [
            'GratisAuto',
            'GratisAuto_GratisOV',
            'WelAuto_GratisOV',
            'WelAuto_vkAuto',
            'WelAuto_vkNeutraal',
            'WelAuto_vkFiets',
            'WelAuto_vkOV']

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
        'Auto_Fiets',
        'OV_Fiets',
        'Auto_OV',
        'Auto_OV_Fiets']

    segs_source = SegsSource(config)

    if 'winkelnietdagelijksonderwijs' in motives:
        working_population_per_class = segs_source.read(
            "Leerlingen", scenario=scenario, type_caster=float)
        employment_segs = segs_source.read(
            "Leerlingenplaatsen",
            scenario=scenario,
            type_caster=float)
        place_of_employments = utils.transpose(employment_segs)
    else:
        working_population_per_class = segs_source.read(
            "Beroepsbevolking_inkomensklasse", scenario=scenario, type_caster=float)
        employment_segs = segs_source.read(
            "Arbeidsplaatsen_inkomensklasse",
            scenario=scenario,
            type_caster=float)
        place_of_employments = utils.transpose(employment_segs)

    working_population_totals = [sum(bbpk)
                                 for bbpk in working_population_per_class]

    if 'sociaal-recreatief' in motives:
        id = "L65plus_inkomensklasse" if '65+' in regime else "Inwoners_inkomensklasse"
        citizens_per_class = segs_source.read(
            id, scenario=scenario, type_caster=float)
        citizen_totals = [sum(ipk) for ipk in citizens_per_class]

    income_distributions = np.zeros(
        (len(working_population_per_class), len(
            working_population_per_class[0])))
    for i in range(len(working_population_per_class)):
        for j in range(len(working_population_per_class[0])):
            if working_population_totals[i] > 0:
                income_distributions[i][j] = working_population_per_class[i][j] / \
                    working_population_totals[i]

    income_distributions_transposed = utils.transpose(income_distributions)

    potencies = DataSource(config, DataType.DESTINATIONS)

    for car_possession_group in car_possession_groups:
        for motive in motives:
            if motive == 'werk':
                target_group = 'Beroepsbevolking'
            elif motive == 'winkelnietdagelijksonderwijs':
                target_group = 'Leerlingen'
            else:
                target_group = 'Inwoners'

            if car_possession_group == 'alle groepen':
                distribution_matrix = segs_source.read(
                    f"Verdeling_over_groepen_{target_group}", type_caster=float, scenario=scenario)
            else:
                distribution_matrix = segs_source.read(
                    f"Verdeling_over_groepen_{target_group}_alleen_autobezit",
                    type_caster=float,
                    scenario=scenario)

            distribution_matrix = segs_source.read(
                f"Verdeling_over_groepen_{target_group}",
                type_caster=float,
                scenario=scenario)
            distribution_matrix_transpose = utils.transpose(
                distribution_matrix)

            for part_of_day in part_of_days:
                for i_income_group, income_group in enumerate(income_groups):
                    if motive == 'werk' or motive == 'winkelnietdagelijksonderwijs':
                        place_of_employment = np.array(
                            place_of_employments[i_income_group])
                    else:
                        place_of_employment = citizen_totals

                    incomes = np.array(
                        income_distributions_transposed[i_income_group])
                    general_possibility_totals = []

                    for modality in modalities:
                        possibility_sum = np.zeros(len(employment_segs))

                        for i_group, group in enumerate(groups):
                            if motive == 'werk' or motive == 'winkelnietdagelijksonderwijs':
                                distribution = np.array(
                                    distribution_matrix_transpose[i_group])
                            else:
                                distribution = distribution_matrix_transpose

                            income = utils.group_income_level(group)
                            if income_group == income or income_group == 'alle':
                                K = electric_percentage.get(income_group) / 100
                                matrix = get_weight_matrix(
                                    single_weights,
                                    combined_weights,
                                    group,
                                    modality,
                                    motive,
                                    regime,
                                    part_of_day,
                                    income,
                                    income_group,
                                    K)
                                possibility = matrix @ place_of_employment * distribution
                                possibility = np.divide(
                                    possibility, incomes, where=incomes > 0)
                                possibility[incomes <= 0] = 0
                                possibility_sum += possibility

                        key = DataKey('Totaal',
                                      part_of_day=part_of_day,
                                      income=income_group,
                                      group=car_possession_group,
                                      motive=motive,
                                      modality=modality)
                        potencies.set(key, possibility_sum.copy())
                        general_possibility_totals.append(potencies.get(key))

                    general_possibility_totals_transposed = utils.transpose(
                        general_possibility_totals)
                    general_possibility_totals_transposed = np.round(
                        general_possibility_totals_transposed).astype(int)

                    key = DataKey('Ontpl_totaal',
                                  part_of_day=part_of_day,
                                  group=car_possession_group,
                                  income=income_group,
                                  motive=motive)
                    potencies.write_csv(
                        general_possibility_totals_transposed, key, header=headstring)
                    potencies.write_xlsx(
                        general_possibility_totals_transposed,
                        key,
                        header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for modality in modalities:
                    general_matrix_product = []
                    general_matrix = []
                    for income_group in income_groups:
                        key = DataKey('Totaal',
                                      part_of_day=part_of_day,
                                      income=income_group,
                                      group=car_possession_group,
                                      motive=motive,
                                      modality=modality)
                        totals_row = potencies.get(key)
                        general_matrix.append(totals_row)
                    if len(income_groups) > 1:
                        general_possibility_totals_transposed = utils.transpose(
                            general_matrix)
                    else:
                        general_possibility_totals_transposed = general_matrix
                    for i in range(len(working_population_per_class)):
                        general_matrix_product.append([])
                        for j in range(len(working_population_per_class[0])):
                            if working_population_per_class[i][j] > 0:
                                general_matrix_product[i].append(
                                    general_possibility_totals_transposed[i][j] *
                                    working_population_per_class[i][j])
                            else:
                                general_matrix_product[i].append(0)

                    general_possibility_totals_transposed = np.round(
                        general_possibility_totals_transposed).astype(int)
                    key = DataKey('Ontpl_totaal',
                                  part_of_day=part_of_day,
                                  group=car_possession_group,
                                  motive=motive,
                                  modality=modality)
                    potencies.write_xlsx(
                        general_possibility_totals_transposed, key, header=header)

                    general_matrix_product = np.round(
                        general_matrix_product).astype(int)
                    key = DataKey('Ontpl_totaalproduct',
                                  part_of_day=part_of_day,
                                  group=car_possession_group,
                                  motive=motive,
                                  modality=modality)
                    potencies.write_xlsx(
                        general_matrix_product, key, header=header)

    return potencies
