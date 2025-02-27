import logging

import numpy as np

from ikob.datasource import DataKey, DataSource, DataType

logger = logging.getLogger(__name__)


def has_preference(kind_car, kind_pt, preference):
    if kind_car == 'GeenAuto' or kind_car == 'GeenRijbewijs':
        if preference == 'Auto':
            return False
        else:
            if kind_pt == 'GratisOV':
                if preference != 'OV':
                    return False
                else:
                    return True
            else:
                return True
    elif kind_car == 'GratisAuto':
        if kind_pt == 'GratisOV':
            if preference != 'Neutraal':
                return False
            else:
                return True
        else:
            if preference != 'Auto':
                return False
            else:
                return True
    elif kind_pt == 'GratisOV':
        return preference == 'OV'
    else:
        return True


def calculate_combined_weights(config,
                               single_weights: DataSource,
                               combined_weigths: DataSource):
    logger.info("Maximum weights by multiple modalities.")

    project_config = config['project']
    skims_config = config['skims']

    motives = project_config['motieven']
    regimes = project_config['beprijzingsregime']
    part_of_days = skims_config['dagsoort']

    incomes = ['hoog', 'middelhoog', 'middellaag', 'laag']
    preferences = ['Auto', 'Neutraal', 'Fiets', 'OV']
    modalities_bike = ['Fiets']
    car_kinds = ['Auto', 'GeenAuto', 'GeenRijbewijs', 'GratisAuto']
    pt_kinds = ['OV', 'GratisOV']
    fuel_kinds = ['fossiel', 'elektrisch']

    for motive in motives:
        for part_of_day in part_of_days:
            for income in incomes:
                for preference in preferences:
                    for modality_bike in modalities_bike:
                        for pt_kind in pt_kinds:
                            if not has_preference('Auto', pt_kind, preference):
                                continue

                            preference_bike = 'Fiets' if preference == 'Fiets' else ''
                            key = DataKey(f'{modality_bike}_vk',
                                          part_of_day=part_of_day,
                                          preference=preference_bike,
                                          regime=regimes,
                                          motive=motive)
                            bike_matrix = single_weights.get(key)

                            key = DataKey(f'{pt_kind}_vk',
                                          part_of_day=part_of_day,
                                          preference=preference,
                                          income=income,
                                          regime=regimes,
                                          motive=motive)
                            pt_matrix = single_weights.get(key)

                            max = np.maximum.reduce((bike_matrix, pt_matrix))
                            key = DataKey(f"{pt_kind}_{modality_bike}_vk",
                                          part_of_day=part_of_day,
                                          income=income,
                                          regime=regimes,
                                          motive=motive,
                                          preference=preference,
                                          subtopic='combinaties')
                            combined_weigths.set(key, max.copy())

                        for car_kind in car_kinds:
                            if not has_preference(car_kind, 'OV', preference):
                                continue

                            preference_bike = 'Fiets' if preference == 'Fiets' else ''
                            key = DataKey(f'{modality_bike}_vk',
                                          part_of_day=part_of_day,
                                          preference=preference_bike,
                                          regime=regimes,
                                          motive=motive)
                            bike_matrix = single_weights.get(key)

                            if car_kind == 'Auto':
                                for fuel_kind in fuel_kinds:
                                    key = DataKey(f'{car_kind}_vk',
                                                  part_of_day=part_of_day,
                                                  preference=preference,
                                                  income=income,
                                                  regime=regimes,
                                                  motive=motive,
                                                  fuel_kind=fuel_kind)
                                    car_matrix = single_weights.get(key)

                                    max = np.maximum.reduce(
                                        (bike_matrix, car_matrix))
                                    key = DataKey(
                                        f"{car_kind}_{modality_bike}_vk",
                                        part_of_day=part_of_day,
                                        income=income,
                                        regime=regimes,
                                        motive=motive,
                                        preference=preference,
                                        subtopic='combinaties',
                                        fuel_kind=fuel_kind)
                                    combined_weigths.set(key, max.copy())
                            else:
                                key = DataKey(f'{car_kind}_vk',
                                              part_of_day=part_of_day,
                                              preference=preference,
                                              income=income,
                                              regime=regimes,
                                              motive=motive)
                                car_matrix = single_weights.get(key)

                                max = np.maximum.reduce(
                                    (bike_matrix, car_matrix))
                                key = DataKey(f"{car_kind}_{modality_bike}_vk",
                                              part_of_day=part_of_day,
                                              income=income,
                                              regime=regimes,
                                              motive=motive,
                                              preference=preference,
                                              subtopic='combinaties')
                                combined_weigths.set(key, max.copy())

                    for pt_kind in pt_kinds:
                        for car_kind in car_kinds:
                            if not has_preference(
                                    car_kind, pt_kind, preference):
                                continue

                            key = DataKey(f'{pt_kind}_vk',
                                          part_of_day=part_of_day,
                                          preference=preference,
                                          income=income,
                                          regime=regimes,
                                          motive=motive)
                            pt_matrix = single_weights.get(key)

                            if car_kind == 'Auto':
                                for fuel_kind in fuel_kinds:
                                    key = DataKey(f'{car_kind}_vk',
                                                  part_of_day=part_of_day,
                                                  preference=preference,
                                                  income=income,
                                                  regime=regimes,
                                                  motive=motive,
                                                  fuel_kind=fuel_kind)
                                    car_matrix = single_weights.get(key)
                                    max = np.maximum.reduce(
                                        (pt_matrix, car_matrix))
                                    key = DataKey(f"{car_kind}_{pt_kind}_vk",
                                                  part_of_day=part_of_day,
                                                  income=income,
                                                  regime=regimes,
                                                  motive=motive,
                                                  preference=preference,
                                                  subtopic='combinaties',
                                                  fuel_kind=fuel_kind)
                                    combined_weigths.set(key, max.copy())
                            else:
                                key = DataKey(f'{car_kind}_vk',
                                              part_of_day=part_of_day,
                                              preference=preference,
                                              income=income,
                                              regime=regimes,
                                              motive=motive)
                                car_matrix = single_weights.get(key)

                                max = np.maximum.reduce(
                                    (pt_matrix, car_matrix))
                                key = DataKey(f"{car_kind}_{pt_kind}_vk",
                                              part_of_day=part_of_day,
                                              income=income,
                                              regime=regimes,
                                              motive=motive,
                                              preference=preference,
                                              subtopic='combinaties')
                                combined_weigths.set(key, max.copy())

                    for modality_bike in modalities_bike:
                        for pt_kind in pt_kinds:
                            for car_kind in car_kinds:
                                if not has_preference(
                                        car_kind, pt_kind, preference):
                                    continue

                                preference_bike = 'Fiets' if preference == 'Fiets' else ''
                                key = DataKey(f'{modality_bike}_vk',
                                              part_of_day=part_of_day,
                                              preference=preference_bike,
                                              regime=regimes,
                                              motive=motive)
                                bike_matrix = single_weights.get(key)

                                key = DataKey(f'{pt_kind}_vk',
                                              part_of_day=part_of_day,
                                              preference=preference,
                                              income=income,
                                              regime=regimes,
                                              motive=motive)
                                pt_matrix = single_weights.get(key)

                                if car_kind == 'Auto':
                                    for fuel_kind in fuel_kinds:
                                        key = DataKey(f'{car_kind}_vk',
                                                      part_of_day=part_of_day,
                                                      preference=preference,
                                                      income=income,
                                                      regime=regimes,
                                                      motive=motive,
                                                      fuel_kind=fuel_kind)
                                        car_matrix = single_weights.get(key)

                                        max = np.maximum.reduce(
                                            (car_matrix, bike_matrix, pt_matrix))
                                        key = DataKey(
                                            f"{car_kind}_{pt_kind}_{modality_bike}_vk",
                                            part_of_day=part_of_day,
                                            income=income,
                                            regime=regimes,
                                            motive=motive,
                                            preference=preference,
                                            subtopic='combinaties',
                                            fuel_kind=fuel_kind)
                                        combined_weigths.set(key, max.copy())
                                else:
                                    key = DataKey(f'{car_kind}_vk',
                                                  part_of_day=part_of_day,
                                                  preference=preference,
                                                  income=income,
                                                  regime=regimes,
                                                  motive=motive)
                                    car_matrix = single_weights.get(key)

                                    max = np.maximum.reduce(
                                        (car_matrix, bike_matrix, pt_matrix))
                                    key = DataKey(
                                        f"{car_kind}_{pt_kind}_{modality_bike}_vk",
                                        part_of_day=part_of_day,
                                        income=income,
                                        regime=regimes,
                                        motive=motive,
                                        preference=preference,
                                        subtopic='combinaties')
                                    combined_weigths.set(key, max.copy())

    return combined_weigths
