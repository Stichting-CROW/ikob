import logging
import math
import ikob.constants as Constantengenerator
import numpy as np
from ikob.datasource import DataSource, DataKey, DataType

logger = logging.getLogger(__name__)


def gewichtenberekenen(skim, mod, vk, mot):
    alpha, omega, scaling = Constantengenerator.work_constants(mod, vk, mot)
    Gewichtenmatrix = np.zeros((len(skim), len(skim)))

    for r in range(0, len(skim)):
        for k in range(0, len(skim)):
            ervaren_reistijd = skim[r][k]

            if ervaren_reistijd < 180:
                reistijdwaarde = (1 / (1 + math.exp((-omega + ervaren_reistijd)*alpha)))*scaling
            else:
                reistijdwaarde = 0

            if reistijdwaarde < 0.001:
                reistijdwaarde = 0

            Gewichtenmatrix[r][k] = round(reistijdwaarde, 4)
    return Gewichtenmatrix


def calculate_single_weights(config, ervaren_reistijd: DataSource) -> DataSource:
    logger.info("Gewichten (reistijdvervalscurven) voor auto, OV, fiets en E-fiets apart.")

    project_config = config['project']
    skims_config = config['skims']

    # Ophalen van instellingen
    dagsoort = skims_config['dagsoort']
    motieven = project_config['motieven']
    regime = project_config['beprijzingsregime']

    # Vaste waarden
    inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
    voorkeuren = ['Auto', 'Neutraal', 'Fiets', 'OV']
    modaliteitenfiets = ['Fiets']
    soortbrandstof = ['fossiel', 'elektrisch']

    gewichten = DataSource(config, DataType.WEIGHTS)

    for ds in dagsoort:
        for mot in motieven:
            for mod in modaliteitenfiets:
                for vk in voorkeuren:
                    if vk == 'Auto' or vk == 'Fiets':
                        key = DataKey('Fiets',
                                      part_of_day=ds,
                                      regime=regime,
                                      motive=mot)
                        GGRskim = ervaren_reistijd.get(key)
                        Gewichten = gewichtenberekenen(GGRskim, mod, vk, mot)

                        if vk == 'Auto':
                            key = DataKey(f'{mod}_vk',
                                          part_of_day=ds,
                                          regime=regime,
                                          motive=mot)
                        else:
                            key = DataKey(f'{mod}_vk',
                                          part_of_day=ds,
                                          regime=regime,
                                          motive=mot,
                                          preference=vk)

                        gewichten.set(key, Gewichten.copy())

            # Nu Auto
            for ink in inkomen:
                for vk in voorkeuren:
                    for srtbr in soortbrandstof:
                        key = DataKey(f'Auto_{srtbr}',
                                      part_of_day=ds,
                                      income=ink,
                                      regime=regime,
                                      motive=mot)
                        GGRskim = ervaren_reistijd.get(key)

                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        key = DataKey('Auto_vk',
                                      part_of_day=ds,
                                      income=ink,
                                      regime=regime,
                                      motive=mot,
                                      preference=vk,
                                      fuel_kind=srtbr)
                        gewichten.set(key, Gewichten.copy())

            soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
            voorkeurengeenauto = ['Neutraal', 'OV', 'Fiets']
            for sga in soortgeenauto:
                for vk in voorkeurengeenauto:
                    for ink in inkomen:
                        key = DataKey(f'{sga}',
                                      part_of_day=ds,
                                      income=ink,
                                      regime=regime,
                                      motive=mot)
                        GGRskim = ervaren_reistijd.get(key)

                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        key = DataKey(f'{sga}_vk',
                                      part_of_day=ds,
                                      income=ink,
                                      regime=regime,
                                      preference=vk,
                                      motive=mot)
                        gewichten.set(key, Gewichten.copy())

            modaliteitenOV = ['OV']
            for modOV in modaliteitenOV:
                for ink in inkomen:
                    for vk in voorkeuren:
                        key = DataKey(f'{modOV}',
                                      part_of_day=ds,
                                      income=ink,
                                      regime=regime,
                                      motive=mot)
                        GGRskim = ervaren_reistijd.get(key)

                        Gewichten = gewichtenberekenen(GGRskim, modOV, vk, mot)
                        key = DataKey(f'{modOV}_vk',
                                      part_of_day=ds,
                                      preference=vk,
                                      income=ink,
                                      regime=regime,
                                      motive=mot)
                        gewichten.set(key, Gewichten.copy())

            for ink in inkomen:
                key = DataKey('GratisAuto',
                              part_of_day=ds,
                              income=ink,
                              regime=regime,
                              motive=mot)
                GGRskim = ervaren_reistijd.get(key)

                Gewichten = gewichtenberekenen(GGRskim, 'Auto', 'Auto', mot)
                specialauto = ['Neutraal', 'Auto']
                for vks in specialauto:
                    key = DataKey('GratisAuto_vk',
                                  part_of_day=ds,
                                  preference=vks,
                                  income=ink,
                                  regime=regime,
                                  motive=mot)
                    gewichten.set(key, Gewichten.copy())

                key = DataKey('GratisOV',
                              part_of_day=ds,
                              regime=regime,
                              motive=mot)
                GGRskim = ervaren_reistijd.get(key)

                Gewichten = gewichtenberekenen(GGRskim, 'OV', 'OV', mot)
                specialOV = ['Neutraal', 'OV']
                for vks in specialOV:
                    key = DataKey('GratisOV_vk',
                                  part_of_day=ds,
                                  preference=vks,
                                  income=ink,
                                  regime=regime,
                                  motive=mot)
                    gewichten.set(key, Gewichten.copy())

    return gewichten
