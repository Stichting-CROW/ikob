import logging
import math
import ikob.Constantengenerator as Constantengenerator
import numpy as np
from typing import Dict
from numpy.typing import NDArray
from ikob.datasource import DataSource, DataKey

logger = logging.getLogger(__name__)


def gewichtenberekenen(skim, mod, vk, mot):
    alpha, omega, weging = Constantengenerator.alomwerk(mod, vk, mot)
    Gewichtenmatrix = np.zeros((len(skim), len(skim)))

    for r in range(0, len(skim)):
        for k in range(0, len(skim)):
            ervaren_reistijd = skim[r][k]

            if ervaren_reistijd < 180:
                reistijdwaarde = (1 / (1 + math.exp((-omega + ervaren_reistijd)*alpha)))*weging
            else:
                reistijdwaarde = 0

            if reistijdwaarde < 0.001:
                reistijdwaarde = 0

            Gewichtenmatrix[r][k] = round(reistijdwaarde, 4)
    return Gewichtenmatrix


def gewichten_berekenen_enkel_scenarios(config, datasource: DataSource, ervaren_reistijd: Dict[DataKey, NDArray]) -> Dict[DataKey, NDArray]:
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

    gewichten: Dict[DataKey, NDArray] = dict()

    for ds in dagsoort:
        for mot in motieven:
            for mod in modaliteitenfiets:
                for vk in voorkeuren:
                    if vk == 'Auto' or vk == 'Fiets':
                        key = DataKey('Ervarenreistijd',
                                      'Fiets',
                                      dagsoort=ds,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = ervaren_reistijd[key]
                        Gewichten = gewichtenberekenen(GGRskim, mod, vk, mot)

                        if vk == 'Auto':
                            key = DataKey('Gewichten',
                                          f'{mod}_vk',
                                          dagsoort=ds,
                                          regime=regime,
                                          motief=mot)
                        else:
                            key = DataKey('Gewichten',
                                          f'{mod}_vk',
                                          dagsoort=ds,
                                          regime=regime,
                                          motief=mot,
                                          voorkeur=vk)

                        gewichten[key] = Gewichten.copy()

            # Nu Auto
            for ink in inkomen:
                for vk in voorkeuren:
                    for srtbr in soortbrandstof:
                        key = DataKey('Ervarenreistijd',
                                      f'Auto_{srtbr}',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = ervaren_reistijd[key]

                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        key = DataKey('Gewichten',
                                      'Auto_vk',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot,
                                      voorkeur=vk,
                                      brandstof=srtbr)
                        gewichten[key] = Gewichten.copy()

            soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
            voorkeurengeenauto = ['Neutraal', 'OV', 'Fiets']
            for sga in soortgeenauto:
                for vk in voorkeurengeenauto:
                    for ink in inkomen:
                        key = DataKey('Ervarenreistijd',
                                      f'{sga}',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = ervaren_reistijd[key]

                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        key = DataKey('Gewichten',
                                      f'{sga}_vk',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      voorkeur=vk,
                                      motief=mot)
                        gewichten[key] = Gewichten.copy()

            modaliteitenOV = ['OV']
            for modOV in modaliteitenOV:
                for ink in inkomen:
                    for vk in voorkeuren:
                        key = DataKey('Ervarenreistijd',
                                      f'{modOV}',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = ervaren_reistijd[key]

                        Gewichten = gewichtenberekenen(GGRskim, modOV, vk, mot)
                        key = DataKey('Gewichten',
                                      f'{modOV}_vk',
                                      dagsoort=ds,
                                      voorkeur=vk,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        gewichten[key] = Gewichten.copy()

            for ink in inkomen:
                key = DataKey('Ervarenreistijd',
                              'GratisAuto',
                              dagsoort=ds,
                              inkomen=ink,
                              regime=regime,
                              motief=mot)
                GGRskim = ervaren_reistijd[key]

                Gewichten = gewichtenberekenen(GGRskim, 'Auto', 'Auto', mot)
                specialauto = ['Neutraal', 'Auto']
                for vks in specialauto:
                    key = DataKey('Gewichten',
                                  'GratisAuto_vk',
                                  dagsoort=ds,
                                  voorkeur=vks,
                                  inkomen=ink,
                                  regime=regime,
                                  motief=mot)
                    gewichten[key] = Gewichten.copy()

                key = DataKey('Ervarenreistijd',
                              'GratisOV',
                              dagsoort=ds,
                              regime=regime,
                              motief=mot)
                GGRskim = ervaren_reistijd[key]

                Gewichten = gewichtenberekenen(GGRskim, 'OV', 'OV', mot)
                specialOV = ['Neutraal', 'OV']
                for vks in specialOV:
                    key = DataKey('Gewichten',
                                  'GratisOV_vk',
                                  dagsoort=ds,
                                  voorkeur=vks,
                                  inkomen=ink,
                                  regime=regime,
                                  motief=mot)
                    gewichten[key] = Gewichten.copy()

    return gewichten
