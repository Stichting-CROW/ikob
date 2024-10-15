import logging
import ikob.utils as utils
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def get_potencies(matrix, citizens_transposed, group, groups):
    group_list = []
    for i in range(len(matrix)):
        weights = []
        for m, ct in zip(matrix[i], citizens_transposed[groups.index(group)]):
            weights.append(m * ct)
        group_list.append(sum(weights))
    return group_list


def create_citizens_file(distribution_matrix, working_population):
    citizens_file = []
    for i in range (len(working_population)) :
        citizens_file.append([])
        for j in range (len(distribution_matrix[0])) :
            citizens_file[i].append(round(working_population[i]*distribution_matrix[i][j]))
    return citizens_file


def possible_companies(config,
                       single_weights: DataSource,
                       combined_weights: DataSource) -> DataSource:
    logger.info("Possibilities for companies and institutes.")

    project_config=config['project']
    skims_config = config['skims']
    distribution_config = config['verdeling']
    part_of_days = skims_config['dagsoort']

    scenarios = project_config['verstedelijkingsscenario']
    regimes = project_config['beprijzingsregime']
    motives = project_config['motieven']
    car_possession_groups = project_config['welke_groepen']
    fuel_kinds = ['fossiel', 'elektrisch']
    electric_percentage = distribution_config ['Percelektrisch']

    # Vaste waarden
    groups = ['GratisAuto_laag', 'GratisAuto_GratisOV_laag','WelAuto_GratisOV_laag','WelAuto_vkAuto_laag',
               'WelAuto_vkNeutraal_laag', 'WelAuto_vkFiets_laag','WelAuto_vkOV_laag','GeenAuto_GratisOV_laag',
               'GeenAuto_vkNeutraal_laag','GeenAuto_vkFiets_laag', 'GeenAuto_vkOV_laag','GeenRijbewijs_GratisOV_laag',
               'GeenRijbewijs_vkNeutraal_laag', 'GeenRijbewijs_vkFiets_laag', 'GeenRijbewijs_vkOV_laag', 
               'GratisAuto_middellaag', 'GratisAuto_GratisOV_middellaag','WelAuto_GratisOV_middellaag',
               'WelAuto_vkAuto_middellaag','WelAuto_vkNeutraal_middellaag','WelAuto_vkFiets_middellaag',
               'WelAuto_vkOV_middellaag','GeenAuto_GratisOV_middellaag','GeenAuto_vkNeutraal_middellaag',
               'GeenAuto_vkFiets_middellaag', 'GeenAuto_vkOV_middellaag','GeenRijbewijs_GratisOV_middellaag',
               'GeenRijbewijs_vkNeutraal_middellaag','GeenRijbewijs_vkFiets_middellaag', 'GeenRijbewijs_vkOV_middellaag',
               'GratisAuto_middelhoog', 'GratisAuto_GratisOV_middelhoog','WelAuto_GratisOV_middelhoog',
               'WelAuto_vkAuto_middelhoog','WelAuto_vkNeutraal_middelhoog','WelAuto_vkFiets_middelhoog',
               'WelAuto_vkOV_middelhoog','GeenAuto_GratisOV_middelhoog','GeenAuto_vkNeutraal_middelhoog',
               'GeenAuto_vkFiets_middelhoog', 'GeenAuto_vkOV_middelhoog','GeenRijbewijs_GratisOV_middelhoog',
               'GeenRijbewijs_vkNeutraal_middelhoog', 'GeenRijbewijs_vkFiets_middelhoog', 'GeenRijbewijs_vkOV_middelhoog',
               'GratisAuto_hoog', 'GratisAuto_GratisOV_hoog', 'WelAuto_GratisOV_hoog','WelAuto_vkAuto_hoog',
               'WelAuto_vkNeutraal_hoog','WelAuto_vkFiets_hoog','WelAuto_vkOV_hoog','GeenAuto_GratisOV_hoog',
               'GeenAuto_vkNeutraal_hoog','GeenAuto_vkFiets_hoog', 'GeenAuto_vkOV_hoog','GeenRijbewijs_GratisOV_hoog',
               'GeenRijbewijs_vkNeutraal_hoog','GeenRijbewijs_vkFiets_hoog', 'GeenRijbewijs_vkOV_hoog']

    modalities = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']

    income_groups = ['laag', 'middellaag', 'middelhoog', 'hoog']
    headstring = ['Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                      'Auto_OV_Fiets', 'Auto_OV_EFiets']
    headstringExcel=['Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                      'Auto_OV_Fiets', 'Auto_OV_EFiets']

    segs_source = SegsSource(config)

    if 'werk' in motives:
        distribution_matrix = segs_source.read("Verdeling_over_groepen_Beroepsbevolking", scenario=scenarios, type_caster=float)
    elif 'winkelnietdagelijksonderwijs' in motives:
        distribution_matrix = segs_source.read("Verdeling_over_groepen_Leerlingen", scenario=scenarios, type_caster=float)
    if 'winkelnietdagelijksonderwijs' in motives:
        working_population_income_class =  segs_source.read("Leerlingen", scenario=scenarios, type_caster=int)
        place_of_employment_class = segs_source.read("Leerlingenplaatsen", scenario=scenarios, type_caster=float)
    else:
        working_population_income_class =  segs_source.read("Beroepsbevolking_inkomensklasse", scenario=scenarios, type_caster=int)
        place_of_employment_class = segs_source.read("Arbeidsplaatsen_inkomensklasse", scenario=scenarios, type_caster=float)

    working_population = []

    for i in range (len(working_population_income_class)):
        working_population.append(sum(working_population_income_class[i]))

    citizens = create_citizens_file (distribution_matrix, working_population)
    citizens_transpose = utils.transpose(citizens)

    origins = DataSource(config, DataType.ORIGINS)

    for car_possession_group in car_possession_groups:
        for motive in motives:
            if motive == 'werk':
                target_group = 'Beroepsbevolking'
            elif motive == 'winkelnietdagelijksonderwijs':
                target_group = 'Leerlingen'
            else:
                target_group = 'Inwoners'

            if car_possession_group == "alle groepen":
                distribution_matrix = segs_source.read(f"Verdeling_over_groepen_{target_group}", scenario=scenarios, type_caster=float)
            else:
                distribution_matrix = segs_source.read(f"Verdeling_over_groepen_{target_group}_alleen_autobezit", scenario=scenarios, type_caster=float)

            for part_of_day in part_of_days:
                for income_group in income_groups:
                    general_possibility_totals = []
                    for modality in modalities:
                        working_population_list = utils.zeros(len(working_population))
                        for group in groups:
                            income = utils.group_income_level ( group )
                            if income_group == income or income_group == 'alle':
                                preference = utils.find_preference (group, modality)
                                if modality == 'Fiets' or modality == 'EFiets':
                                    if preference == 'Fiets':
                                        tmp_preference = 'Fiets'
                                    else:
                                        tmp_preference = ''

                                    key = DataKey(f'{modality}_vk',
                                                  part_of_day=part_of_day,
                                                  preference=tmp_preference,
                                                  regime=regimes,
                                                  motive=motive)
                                    bike_matrix = single_weights.get(key)
                                    group_list = get_potencies (bike_matrix, citizens_transpose, group, groups)

                                    for i in range(0, len(bike_matrix)):
                                        working_population_list[i]+= round(group_list[i])

                                elif modality == 'Auto':
                                    string = utils.single_group(modality, group)
                                    if 'WelAuto' in group:
                                        for fuel_kind in fuel_kinds:
                                            key = DataKey(f'{string}_vk',
                                                          part_of_day=part_of_day,
                                                          preference=preference,
                                                          income=income,
                                                          regime=regimes,
                                                          motive=motive,
                                                          fuel_kind=fuel_kind)
                                            matrix = single_weights.get(key)

                                            group_list_1 = get_potencies(matrix, citizens_transpose, group, groups)
                                            if fuel_kind == 'elektrisch':
                                                K = electric_percentage.get(income_group) / 100
                                                logger.debug('aandeel elektrisch is: %s', K)
                                                group_list_e = [x * K for x in group_list_1]
                                            else:
                                                L = 1 - electric_percentage.get(income_group) / 100
                                                logger.debug('aandeel fossiel is %s', L)
                                                group_list_f = [x * L for x in group_list_1]

                                        for i in range(len(matrix)):
                                            group_list[i] = group_list_e[i] + group_list_f[i]

                                        for i in range(0, len(matrix)):
                                            working_population_list[i] += int(group_list[i])

                                    else:
                                        key = DataKey(f'{string}_vk',
                                                      part_of_day=part_of_day,
                                                      preference=preference,
                                                      income=income,
                                                      regime=regimes,
                                                      motive=motive)
                                        matrix = single_weights.get(key)

                                        group_list = get_potencies(matrix, citizens_transpose, group, groups)
                                        for i in range(0, len(matrix)):
                                            working_population_list[i] += int(group_list[i])

                                elif modality == 'OV':
                                    string = utils.single_group (modality,group)
                                    key = DataKey(f'{string}_vk',
                                                  part_of_day=part_of_day,
                                                  preference=preference,
                                                  income=income,
                                                  regime=regimes,
                                                  motive=motive)
                                    matrix = single_weights.get(key)

                                    group_list = get_potencies ( matrix, citizens_transpose, group, groups)

                                    for i in range(0, len(matrix) ):
                                        working_population_list[i]+= round(group_list[i])
                                else:
                                    string = utils.combined_group(modality, group)
                                    logger.debug('de gr is %s', group)
                                    logger.debug('de string is %s', string)
                                    if string[0] == 'A':
                                        for fuel_kind in fuel_kinds:
                                            key = DataKey(f'{string}_vk',
                                                          part_of_day=part_of_day,
                                                          preference=preference,
                                                          income=income,
                                                          regime=regimes,
                                                          motive=motive,
                                                          subtopic='combinaties',
                                                          fuel_kind=fuel_kind)
                                            matrix = combined_weights.get(key)

                                            group_list_1 = get_potencies(matrix, citizens_transpose, group, groups)

                                            if fuel_kind == 'elektrisch':
                                                K = electric_percentage.get(income_group) / 100
                                                group_list_e = [x * K for x in group_list_1]
                                            else:
                                                K = 1 - electric_percentage.get(income_group) / 100
                                                group_list_f = [x * K for x in group_list_1]

                                        for i in range(len(matrix)):
                                            group_list[i] = group_list_e[i] + group_list_f[i]

                                        for i in range(0, len(matrix)):
                                            working_population_list[i] += int(group_list[i])

                                    else:
                                        key = DataKey(f'{string}_vk',
                                                      part_of_day=part_of_day,
                                                      preference=preference,
                                                      income=income,
                                                      regime=regimes,
                                                      motive=motive,
                                                      subtopic='combinaties')
                                        matrix = combined_weights.get(key)

                                        group_list = get_potencies ( matrix, citizens_transpose, group, groups)
                                        for i in range ( 0, len ( matrix ) ):
                                            working_population_list[i] += round ( group_list[i])

                        key = DataKey(id='Totaal',
                                      part_of_day=part_of_day,
                                      group=car_possession_group,
                                      income=income_group,
                                      motive=motive,
                                      modality=modality)
                        origins.set(key, working_population_list)
                        general_possibility_totals.append(origins.get(key))

                    key = DataKey(id='Pot_totaal',
                                  part_of_day=part_of_day,
                                  group=car_possession_group,
                                  income=income_group,
                                  motive=motive)

                    origins_total = utils.transpose(general_possibility_totals)
                    origins.write_csv(origins_total, key, header=headstring)
                    origins.write_xlsx(origins_total, key, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for modality in modalities:
                    general_matrix_product = []
                    general_matrix = []
                    for income_group in income_groups:
                        key = DataKey('Totaal',
                                      part_of_day=part_of_day,
                                      income=income_group,
                                      motive=motive,
                                      group=car_possession_group,
                                      modality=modality,
                                      subtopic='')
                        total_row = origins.get(key)

                        general_matrix.append(total_row)
                    general_total_transpose = utils.transpose(general_matrix)
                    for i in range (len(place_of_employment_class)):
                        general_matrix_product.append([])
                        for j in range (len(place_of_employment_class[0])):
                            if place_of_employment_class[i][j]>0:
                                general_matrix_product[i].append(int(general_total_transpose[i][j]*place_of_employment_class[i][j]))
                            else:
                                general_matrix_product[i].append(0)

                    key = DataKey(id='Pot_totaal',
                                  part_of_day=part_of_day,
                                  group=car_possession_group,
                                  motive=motive,
                                  modality=modality)
                    origins.write_xlsx(general_total_transpose, key, header=header)

                    key = DataKey(id='Pot_totaalproduct',
                                  part_of_day=part_of_day,
                                  group=car_possession_group,
                                  motive=motive,
                                  modality=modality)
                    origins.write_xlsx(general_matrix_product, key, header=header)

    return origins
