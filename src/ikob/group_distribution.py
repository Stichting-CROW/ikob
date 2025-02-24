import itertools
import logging

import numpy as np

from ikob.datasource import SegsSource, read_csv_from_config

logger = logging.getLogger(__name__)


def distribute_over_groups(config):
    logger.info("Verdeling van de groepen over de buurten of zones")

    project_config = config['project']
    verdeling_config = config['verdeling']
    advanced_config = config['geavanceerd']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    artificial = advanced_config['kunstmab']['gebruiken']
    free_pt_percentage = verdeling_config['GratisOVpercentage']
    motieven = project_config['motieven']

    # Vaste waarden
    income_levels = ['laag', 'middellaag', 'middelhoog', 'hoog']
    preferences = ['Auto', 'Neutraal', 'Fiets', 'OV']
    preferences_no_car = ['Neutraal', 'Fiets', 'OV']
    kinds = ['GratisAuto', 'WelAuto', 'GeenAuto', 'GeenRijbewijs']

    segs_source = SegsSource(config)

    car_possessions_per_household_segs = segs_source.read(
        'CBS_autos_per_huishouden')
    urbanisation_grade_segs = segs_source.read('Stedelijkheidsgraad')
    # Decrement one to account for zero-based indexing later on.
    urbanisation = [int(sgg) - 1 for sgg in urbanisation_grade_segs]

    free_car_per_income = [0, 0.02, 0.175, 0.275]
    min_car_possession = car_possessions_per_household_segs

    if artificial:
        artifical_car_possession_segs = read_csv_from_config(
            config, key='geavanceerd', id='kunstmab', type_caster=int)
        min_car_possession = list(
            itertools.starmap(
                min, zip(
                    car_possessions_per_household_segs, artifical_car_possession_segs)))

    # Read SEGS input files.
    no_license_segs = segs_source.read('GeenRijbewijs')
    no_car_segs = segs_source.read('GeenAuto')
    with_car_segs = segs_source.read('WelAuto')
    preferences_segs = segs_source.read('Voorkeuren')
    preferences_no_car_segs = segs_source.read('VoorkeurenGeenAuto')

    header = []
    for ink in income_levels:
        for srt in kinds:
            if srt == 'GratisAuto':
                header.append(f'{srt}_{ink}')
                header.append(f'{srt}_GratisOV_{ink}')
            elif srt == 'WelAuto':
                header.append(f'{srt}_GratisOV_{ink}')
                for vk in preferences:
                    header.append(f'{srt}_vk{vk}_{ink}')
            else:
                header.append(f'{srt}_GratisOV_{ink}')
                for vkg in preferences_no_car:
                    header.append(f'{srt}_vk{vkg}_{ink}')

    total_survey = []
    total_car_possession_survey = []
    survey_per_income_class = []

    free_car = []
    no_free_car = []
    no_car_with_license = []

    for mot in motieven:
        if mot == 'werk':
            population_share = 'Beroepsbevolking'
            citizens_per_class = segs_source.read(
                f'{population_share}_inkomensklasse', scenario=scenario)
        elif mot == 'winkelnietdagelijksonderwijs':
            population_share = 'Leerlingen'
            citizens_per_class = segs_source.read(
                f'{population_share}', scenario=scenario)
        else:
            population_share = 'Inwoners'
            citizens_per_class = segs_source.read(
                f'{population_share}_inkomensklasse', scenario=scenario)

        citizens_totals = np.sum(citizens_per_class, axis=1)

        # Avoid division by zero by inserting ones. Afterwards, make
        # sure to zero out entries that would have been divided by zero.
        citizens_totals[citizens_totals == 0] = 1
        income_distributions = citizens_per_class / citizens_totals[:, None]
        income_distributions[citizens_totals == 0][:] = 0

        # First determine theoretical car and possessions.
        for i, income_distribution in enumerate(income_distributions):
            total_survey.append([])
            total_car_possession_survey.append([])
            survey_per_income_class.append([])
            car_possession_share = []
            for id, wc in zip(income_distribution,
                              with_car_segs[urbanisation[i]]):
                car_possession_share.append(id * wc / 100)
            car_possession_shares = sum(car_possession_share)

            # Determine if car possessions are lower.
            car_possession_correction = 1
            if min_car_possession[i] > 0 and min_car_possession[i] / \
                    100 < car_possession_shares:
                car_possession_correction = (
                    min_car_possession[i] / 100) / car_possession_shares
                car_possession_shares = min_car_possession[i] / 100

            # Car possessions, license possessions, income classes.
            for i_income in range(len(income_levels)):
                with_car_share_theoretical = with_car_segs[urbanisation[i]
                                                           ][i_income] / 100
                with_car = with_car_share_theoretical * car_possession_correction
                if car_possession_correction != 1:
                    no_car_correction = (1 - with_car) / \
                        (1 - with_car_share_theoretical)
                else:
                    no_car_correction = 1

                no_car_with_license = no_car_segs[urbanisation[i]
                                                  ][i_income] / 100 * no_car_correction
                no_license = no_license_segs[urbanisation[i]
                                             ][i_income] / 100 * no_car_correction

                # Van de auto's de gratisauto's en gratisauto en OV-bepalen en
                # de rest overhouden

                income_share = income_distribution[i_income]

                free_car = with_car * free_car_per_income[i_income]
                no_free_car = with_car - free_car
                free_car_share = free_car * \
                    (1 - free_pt_percentage) * income_share
                total_survey[i].append(free_car_share)
                survey_per_income_class[i].append(free_car_share / with_car)

                free_car_and_pt_share = free_car * free_pt_percentage * income_share
                total_survey[i].append(free_car_and_pt_share)
                survey_per_income_class[i].append(
                    free_car_and_pt_share / with_car)

                free_pt_share = no_free_car * free_pt_percentage * income_share
                total_survey[i].append(free_pt_share)
                survey_per_income_class[i].append(free_pt_share / with_car)

                for i_preference in range(len(preferences)):
                    share_perference = no_free_car * \
                        (1 - free_pt_percentage) * preferences_segs[urbanisation[i]][i_preference] / 100
                    preference_share = share_perference * income_share
                    total_survey[i].append(preference_share)
                    survey_per_income_class[i].append(
                        preference_share / with_car)

                no_car_free_pt_share = no_car_with_license * free_pt_percentage * income_share
                total_survey[i].append(no_car_free_pt_share)
                survey_per_income_class[i].append(0)

                for i_preference in range(len(preferences_no_car)):
                    share_perference = no_car_with_license * \
                        (1 - free_pt_percentage) * preferences_no_car_segs[urbanisation[i]][i_preference] / 100
                    preference_share = share_perference * income_share
                    total_survey[i].append(preference_share)
                    survey_per_income_class[i].append(0)

                no_license_free_pt_share = no_license * free_pt_percentage * income_share
                total_survey[i].append(no_license_free_pt_share)
                survey_per_income_class[i].append(0)

                for i_preference in range(len(preferences_no_car)):
                    share_perference = no_license * \
                        (1 - free_pt_percentage) * preferences_no_car_segs[urbanisation[i]][i_preference] / 100
                    preference_share = share_perference * income_share
                    total_survey[i].append(preference_share)
                    survey_per_income_class[i].append(0)

        logger.debug("Total car posessions: %s", total_car_possession_survey)
        segs_source.write_csv(
            total_survey,
            'Verdeling_over_groepen',
            group=population_share,
            scenario=scenario,
            header=header)
        segs_source.write_csv(
            survey_per_income_class,
            'Verdeling_over_groepen',
            group=population_share,
            modifier="alleen_autobezit",
            scenario=scenario,
            header=header)
        segs_source.write_xlsx(
            total_survey,
            'Verdeling_over_groepen',
            group=population_share,
            scenario=scenario,
            header=[
                'Zone',
                *header])
        segs_source.write_xlsx(
            survey_per_income_class,
            'Verdeling_over_groepen',
            group=population_share,
            modifier="alleen_autobezit",
            scenario=scenario,
            header=[
                'Zone',
                *header])
