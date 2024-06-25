import logging
import math
import ikob.Constantengenerator as Constantengenerator
import numpy as np

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


def gewichten_berekenen_enkel_scenarios(config, datasource):
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
                        GGRskim = datasource.read_csv('Ervarenreistijd', 'Fiets', ds, type_caster=int, regime=regime, mot=mot)
                        Gewichten = gewichtenberekenen(GGRskim, mod, vk, mot)
                        if vk == 'Auto':
                            datasource.write_csv(Gewichten, 'Gewichten', f'{mod}_vk', ds, regime=regime, mot=mot)
                        else :
                            datasource.write_csv(Gewichten, 'Gewichten', f'{mod}_vk', ds, vk=vk, regime=regime, mot=mot)

            # Nu Auto
            for ink in inkomen:
                for vk in voorkeuren:
                    for srtbr in soortbrandstof:
                        GGRskim = datasource.read_csv('Ervarenreistijd', f'Auto_{srtbr}', ds, ink=ink, type_caster=int, regime=regime, mot=mot)
                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        datasource.write_csv(Gewichten, 'Gewichten', 'Auto_vk', ds, vk=vk, ink=ink, srtbr=srtbr, regime=regime, mot=mot)

            soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
            voorkeurengeenauto = ['Neutraal', 'OV', 'Fiets']
            for sga in soortgeenauto:
                for vk in voorkeurengeenauto:
                    for ink in inkomen:
                        GGRskim = datasource.read_csv('Ervarenreistijd', f'{sga}', ds, ink=ink, type_caster=int, regime=regime, mot=mot)
                        Gewichten = gewichtenberekenen(GGRskim, 'Auto', vk, mot)
                        datasource.write_csv(Gewichten, 'Gewichten', f'{sga}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)

            modaliteitenOV = ['OV']
            for modOV in modaliteitenOV:
                for ink in inkomen:
                    for vk in voorkeuren:
                        GGRskim = datasource.read_csv('Ervarenreistijd', f'{modOV}', ds, ink=ink, type_caster=int, regime=regime, mot=mot)
                        Gewichten = gewichtenberekenen(GGRskim, modOV, vk, mot)
                        datasource.write_csv(Gewichten, 'Gewichten', f'{modOV}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)

            for ink in inkomen:
                GGRskim = datasource.read_csv('Ervarenreistijd', 'GratisAuto', ds, ink=ink, type_caster=int, regime=regime, mot=mot)
                Gewichten = gewichtenberekenen(GGRskim, 'Auto', 'Auto', mot)
                specialauto = ['Neutraal', 'Auto']
                for vks in specialauto:
                    datasource.write_csv(Gewichten, 'Gewichten', 'GratisAuto_vk', ds, vk=vks, ink=ink, regime=regime, mot=mot)

                GGRskim = datasource.read_csv('Ervarenreistijd', 'GratisOV', ds, type_caster=int, regime=regime, mot=mot)
                Gewichten = gewichtenberekenen(GGRskim, 'OV', 'OV', mot)
                specialOV = ['Neutraal', 'OV']
                for vks in specialOV:
                    datasource.write_csv(Gewichten, 'Gewichten', 'GratisOV_vk', ds, vk=vks, ink=ink, regime=regime, mot=mot)
