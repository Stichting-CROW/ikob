import logging
import math
import ikob.Constantengenerator as Constantengenerator
import numpy as np

logger = logging.getLogger(__name__)


def gewichtenberekenen(skim, alpha, omega, weging):
    logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
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
    project_config = config['project']
    skims_config = config['skims']

    # Ophalen van instellingen
    dagsoort = skims_config['dagsoort']
    motieven = project_config['motieven']
    regime = project_config['beprijzingsregime']

    # Vaste waarden
    inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
    voorkeuren = ['Auto','Neutraal','Fiets','OV']
    modaliteitenfiets = ['Fiets']
    soortbrandstof = ['fossiel','elektrisch']

    def constantenwerk (mod, voorkeur):
        alpha = 0.125
        omega = 45
        weging = 1
        if mod == 'Fiets':
            alpha = 0.225
            omega = 25
        elif mod == 'EFiets':
            alpha = 0.175
            omega = 35
        if voorkeur == 'Auto':
            if mod == 'Auto' :
                omega = 50
            elif mod == 'OV':
                omega = 30
                weging = 0.95
        elif voorkeur == 'OV':
            if mod == 'Auto':
                weging = 0.96
                alpha = 0.125
                omega = 45
            elif mod == 'OV' :
                alpha = 0.12
                omega = 60
        elif voorkeur == 'Fiets':
            if mod == 'Auto':
                weging = 0.75
            elif mod == 'Fiets':
                alpha = 0.175
                omega = 35
            elif mod == 'EFiets':
                alpha = 0.125
                omega = 55
        return alpha, omega, weging


    # Avondspits en Ochtendspits eruit verwijderd

    for ds in dagsoort:
        for mot in motieven:
            for mod in modaliteitenfiets:
                for vk in voorkeuren:
                    if vk == 'Auto' or vk == 'Fiets':
                        GGRskim = datasource.read_csv('Ervarenreistijd', 'Fiets', ds, type_caster=int, regime=regime, mot=mot)

                        if mot == 'werk' or mot == 'sociaal-recreatief':
                            constanten = Constantengenerator.alomwerk ( mod, vk )
                        elif mot == 'winkeldagelijkszorg':
                            constanten = Constantengenerator.alomwinkeldagelijkszorg ( mod, vk )
                        else:
                            constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( mod, vk )
                        alpha = constanten[0]
                        omega = constanten[1]
                        weging = constanten[2]
                        logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
                        Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging)
                        if vk == 'Auto':
                            datasource.write_csv(Gewichten, 'Gewichten', f'{mod}_vk', ds, regime=regime, mot=mot)
                        else :
                            datasource.write_csv(Gewichten, 'Gewichten', f'{mod}_vk', ds, vk=vk, regime=regime, mot=mot)
            # Nu Auto
            for ink in inkomen:
                for vk in voorkeuren:
                    for srtbr in soortbrandstof:
                        GGRskim = datasource.read_csv('Ervarenreistijd', f'Auto_{srtbr}', ds, ink=ink, type_caster=int, regime=regime, mot=mot)
                        if mot == 'werk' or mot == 'sociaal-recreatief':
                            constanten = Constantengenerator.alomwerk ('Auto', vk )
                        elif mot == 'winkeldagelijkszorg':
                            constanten = Constantengenerator.alomwinkeldagelijkszorg ('Auto', vk )
                        else:
                            constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ('Auto', vk )
                        alpha = constanten[0]
                        omega = constanten[1]
                        weging = constanten[2]
                        logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
                        Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging )
                        datasource.write_csv(Gewichten, 'Gewichten', 'Auto_vk', ds, vk=vk, ink=ink, srtbr=srtbr, regime=regime, mot=mot)

            soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
            voorkeurengeenauto = ['Neutraal', 'OV', 'Fiets']
            for sga in soortgeenauto:
                for vk in voorkeurengeenauto :
                    for ink in inkomen:
                        GGRskim = datasource.read_csv('Ervarenreistijd', f'{sga}', ds, ink=ink, regime=regime, mot=mot)
                        if mot == 'werk' or mot == 'sociaal-recreatief':
                            constanten = Constantengenerator.alomwerk ( 'Auto',vk )
                        elif mot == 'winkeldagelijkszorg':
                            constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'Auto', vk )
                        else:
                            constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'Auto', vk )
                        alpha = constanten[0]
                        omega = constanten[1]
                        weging = constanten[2]
                        logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
                        Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging)
                        datasource.write_csv(Gewichten, 'Gewichten', f'{sga}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)

            # Nu OV
            modaliteitenOV = ['OV']
            for modOV in modaliteitenOV:
                for ink in inkomen:
                    for vk in voorkeuren:
                        GGRskim = datasource.read_csv('Ervarenreistijd', f'{modOV}', ds, ink=ink, type_caster=int, regime=regime, mot=mot)

                        if mot == 'werk' or mot == 'sociaal-recreatief':
                            constanten = Constantengenerator.alomwerk ( modOV, vk )
                        elif mot == 'winkeldagelijks' or 'onderwijs':
                            constanten = Constantengenerator.alomwinkeldagelijkszorg ( modOV, vk )
                        else:
                            constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( modOV, vk )
                        alpha = constanten[0]
                        omega = constanten[1]
                        weging = constanten[2]
                        logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
                        Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging)
                        datasource.write_csv(Gewichten, 'Gewichten', f'{modOV}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)

            for ink in inkomen:
                GGRskim = datasource.read_csv('Ervarenreistijd', 'GratisAuto', ds, ink=ink, type_caster=int, regime=regime, mot=mot)
                if mot == 'werk' or mot == 'sociaal-recreatief':
                    constanten = Constantengenerator.alomwerk ( 'Auto', 'Auto' )
                elif mot == 'winkeldagelijkszorg':
                    constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'Auto', 'Auto' )
                else:
                    constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'Auto', 'Auto' )
                alpha = constanten[0]
                omega = constanten[1]
                weging = constanten[2]
                logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
                Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging )
                specialauto = ['Neutraal', 'Auto']
                for vks in specialauto:
                    datasource.write_csv(Gewichten, 'Gewichten', 'GratisAuto_vk', ds, vk=vks, ink=ink, regime=regime, mot=mot)

                GGRskim = datasource.read_csv('Ervarenreistijd', 'GratisOV', ds, type_caster=int, regime=regime, mot=mot)
                if mot == 'werk' or mot == 'sociaal-recreatief':
                    constanten = Constantengenerator.alomwerk ( 'OV', 'OV' )
                elif mot == 'winkeldagelijkszorg':
                    constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'OV', 'OV' )
                else:
                    constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'OV', 'OV' )
                alpha = constanten[0]
                omega = constanten[1]
                weging = constanten[2]
                logger.debug("alpha: %f, omega: %f, weging: %f", alpha, omega, weging)
                Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging )
                specialOV = ['Neutraal', 'OV']
                for vks in specialOV:
                    datasource.write_csv(Gewichten, 'Gewichten', 'GratisOV_vk', ds, vk=vks, ink=ink, regime=regime, mot=mot)
