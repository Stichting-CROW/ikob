import logging
import math
import ikob.Constantengenerator as Constantengenerator
import numpy as np
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
    return Gewichtenmatrix.tolist()


def gewichten_berekenen_enkel_scenarios(config, datasource: DataSource):
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

    for ds in dagsoort:
        for mot in motieven:
            for mod in modaliteitenfiets:
                for vk in voorkeuren:
                    if vk == 'Auto' or vk == 'Fiets':
                        key = DataKey('ervarenreistijd',
                                      'Fiets',
                                      dagsoort=ds,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = datasource.read_csv(key, type_caster=int)
                        Gewichten = gewichtenberekenen(GGRskim, mod, vk, mot)
                        if vk == 'Auto':
                            key = DataKey('gewichten',
                                          f'{mod}_vk',
                                          dagsoort=ds,
                                          regime=regime,
                                          motief=mot)
                            datasource.write_csv(Gewichten, key)
                        else:
                            key = DataKey('gewichten',
                                          f'{mod}_vk',
                                          dagsoort=ds,
                                          regime=regime,
                                          motief=mot,
                                          voorkeur=vk)
                            datasource.write_csv(Gewichten, key)

            # Nu Auto
            for ink in inkomen:
                for vk in voorkeuren:
                    for srtbr in soortbrandstof:
                        key = DataKey('ervarenreistijd',
                                      f'Auto_{srtbr}',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = datasource.read_csv(key, type_caster=int)

                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        key = DataKey('gewichten',
                                      'Auto_vk',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot,
                                      voorkeur=vk,
                                      brandstof=srtbr)
                        datasource.write_csv(Gewichten, key)

            soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
            voorkeurengeenauto = ['Neutraal', 'OV', 'Fiets']
            for sga in soortgeenauto:
                for vk in voorkeurengeenauto:
                    for ink in inkomen:
                        key = DataKey('ervarenreistijd',
                                      f'{sga}',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = datasource.read_csv(key, type_caster=int)

                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        key = DataKey('gewichten',
                                      f'{sga}_vk',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      voorkeur=vk,
                                      motief=mot)
                        datasource.write_csv(Gewichten, key)

            modaliteitenOV = ['OV']
            for modOV in modaliteitenOV:
                for ink in inkomen:
                    for vk in voorkeuren:
                        key = DataKey('ervarenreistijd',
                                      f'{modOV}',
                                      dagsoort=ds,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        GGRskim = datasource.read_csv(key, type_caster=int)

                        Gewichten = gewichtenberekenen(GGRskim, modOV, vk, mot)
                        key = DataKey('gewichten',
                                      f'{modOV}_vk',
                                      dagsoort=ds,
                                      voorkeur=vk,
                                      inkomen=ink,
                                      regime=regime,
                                      motief=mot)
                        datasource.write_csv(Gewichten, key)

            for ink in inkomen:
                key = DataKey('ervarenreistijd',
                              'GratisAuto',
                              dagsoort=ds,
                              inkomen=ink,
                              regime=regime,
                              motief=mot)
                GGRskim = datasource.read_csv(key, type_caster=int)

                Gewichten = gewichtenberekenen(GGRskim, 'Auto', 'Auto', mot)
                specialauto = ['Neutraal', 'Auto']
                for vks in specialauto:
                    key = DataKey('gewichten',
                                  'GratisAuto_vk',
                                  dagsoort=ds,
                                  voorkeur=vks,
                                  inkomen=ink,
                                  regime=regime,
                                  motief=mot)
                    datasource.write_csv(Gewichten, key)

                key = DataKey('ervarenreistijd',
                              'GratisOV',
                              dagsoort=ds,
                              regime=regime,
                              motief=mot)
                GGRskim = datasource.read_csv(key, type_caster=int)

                Gewichten = gewichtenberekenen(GGRskim, 'OV', 'OV', mot)
                specialOV = ['Neutraal', 'OV']
                for vks in specialOV:
                    key = DataKey('gewichten',
                                  'GratisOV_vk',
                                  dagsoort=ds,
                                  voorkeur=vks,
                                  inkomen=ink,
                                  regime=regime,
                                  motief=mot)
                    datasource.write_csv(Gewichten, key)
