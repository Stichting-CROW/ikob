import logging
import math

import numpy as np

from ikob.constants import work_constants
from ikob.datasource import DataKey, DataSource, DataType

logger = logging.getLogger(__name__)


def calculate_weights(generalised_travel_time, modality, preference, motive):
    alpha, omega, scaling = work_constants(modality, preference, motive)
    n = len(generalised_travel_time)
    weight_matrix = np.zeros((n, n))

    for r in range(len(generalised_travel_time)):
        for k in range(len(generalised_travel_time)):
            if generalised_travel_time[r][k] < 180:
                travel_time = (
                    1 / (1 + math.exp((-omega + generalised_travel_time[r][k]) * alpha))) * scaling
            else:
                travel_time = 0

            if travel_time < 0.001:
                travel_time = 0

            weight_matrix[r][k] = round(travel_time, 4)
    return weight_matrix


def calculate_single_weights(
        config,
        generalised_travel_time: DataSource) -> DataSource:
    logger.info(
        "Weights (travel time decay curves) for car, PT, bike, and E-bike.")

    project_config = config['project']
    skims_config = config['skims']

    # Ophalen van instellingen
    part_of_days = skims_config['dagsoort']
    motives = project_config['motieven']
    regimes = project_config['beprijzingsregime']

    # Vaste waarden
    incomes = ['hoog', 'middelhoog', 'middellaag', 'laag']
    preferences = ['Auto', 'Neutraal', 'Fiets', 'OV']
    modalities_bike = ['Fiets']
    fuel_kinds = ['fossiel', 'elektrisch']

    weights = DataSource(config, DataType.WEIGHTS)

    for part_of_day in part_of_days:
        for motive in motives:
            for modality in modalities_bike:
                for preference in preferences:
                    if preference == 'Auto' or preference == 'Fiets':
                        key = DataKey('Fiets',
                                      part_of_day=part_of_day,
                                      regime=regimes,
                                      motive=motive)
                        ggr_skim = generalised_travel_time.get(key)
                        weight_matrix = calculate_weights(
                            ggr_skim, modality, preference, motive)

                        if preference == 'Auto':
                            key = DataKey(f'{modality}_vk',
                                          part_of_day=part_of_day,
                                          regime=regimes,
                                          motive=motive)
                        else:
                            key = DataKey(f'{modality}_vk',
                                          part_of_day=part_of_day,
                                          regime=regimes,
                                          motive=motive,
                                          preference=preference)

                        weights.set(key, weight_matrix.copy())

            # Car.
            for income in incomes:
                for preference in preferences:
                    for fuel_kind in fuel_kinds:
                        key = DataKey(f'Auto_{fuel_kind}',
                                      part_of_day=part_of_day,
                                      income=income,
                                      regime=regimes,
                                      motive=motive)
                        ggr_skim = generalised_travel_time.get(key)

                        weight_matrix = calculate_weights(
                            ggr_skim, 'Auto', preference, motive)
                        key = DataKey('Auto_vk',
                                      part_of_day=part_of_day,
                                      income=income,
                                      regime=regimes,
                                      motive=motive,
                                      preference=preference,
                                      fuel_kind=fuel_kind)
                        weights.set(key, weight_matrix.copy())

            no_car_kinds = ['GeenAuto', 'GeenRijbewijs']
            no_car_preferences = ['Neutraal', 'OV', 'Fiets']
            for no_car_kind in no_car_kinds:
                for preference in no_car_preferences:
                    for income in incomes:
                        key = DataKey(f'{no_car_kind}',
                                      part_of_day=part_of_day,
                                      income=income,
                                      regime=regimes,
                                      motive=motive)
                        ggr_skim = generalised_travel_time.get(key)

                        weight_matrix = calculate_weights(
                            ggr_skim, 'Auto', preference, motive)
                        key = DataKey(f'{no_car_kind}_vk',
                                      part_of_day=part_of_day,
                                      income=income,
                                      regime=regimes,
                                      preference=preference,
                                      motive=motive)
                        weights.set(key, weight_matrix.copy())

            modalities_pt = ['OV']
            for modality in modalities_pt:
                for income in incomes:
                    for preference in preferences:
                        key = DataKey(f'{modality}',
                                      part_of_day=part_of_day,
                                      income=income,
                                      regime=regimes,
                                      motive=motive)
                        ggr_skim = generalised_travel_time.get(key)

                        weight_matrix = calculate_weights(
                            ggr_skim, modality, preference, motive)
                        key = DataKey(f'{modality}_vk',
                                      part_of_day=part_of_day,
                                      preference=preference,
                                      income=income,
                                      regime=regimes,
                                      motive=motive)
                        weights.set(key, weight_matrix.copy())

            for income in incomes:
                key = DataKey('GratisAuto',
                              part_of_day=part_of_day,
                              income=income,
                              regime=regimes,
                              motive=motive)
                ggr_skim = generalised_travel_time.get(key)

                weight_matrix = calculate_weights(
                    ggr_skim, 'Auto', 'Auto', motive)
                special_car_kinds = ['Neutraal', 'Auto']
                for special_car_kind in special_car_kinds:
                    key = DataKey('GratisAuto_vk',
                                  part_of_day=part_of_day,
                                  preference=special_car_kind,
                                  income=income,
                                  regime=regimes,
                                  motive=motive)
                    weights.set(key, weight_matrix.copy())

                key = DataKey('GratisOV',
                              part_of_day=part_of_day,
                              regime=regimes,
                              motive=motive)
                ggr_skim = generalised_travel_time.get(key)

                weight_matrix = calculate_weights(ggr_skim, 'OV', 'OV', motive)
                special_pt_kinds = ['Neutraal', 'OV']
                for special_pt_kind in special_pt_kinds:
                    key = DataKey('GratisOV_vk',
                                  part_of_day=part_of_day,
                                  preference=special_pt_kind,
                                  income=income,
                                  regime=regimes,
                                  motive=motive)
                    weights.set(key, weight_matrix.copy())

    return weights
