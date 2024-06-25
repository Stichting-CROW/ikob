import logging
import numpy as np

logger = logging.getLogger(__name__)


def kanvoorkeur(soortauto, soortOV, voorkeur):
    if soortauto == 'GeenAuto' or soortauto == 'GeenRijbewijs':
        if voorkeur == 'Auto':
            return False
        else:
            if soortOV == 'GratisOV':
                if voorkeur != 'OV':
                    return False
                else:
                    return True
            else:
                return True
    elif soortauto == 'GratisAuto':
        if soortOV == 'GratisOV':
            if voorkeur != 'Neutraal':
                return False
            else:
                return True
        else:
            if voorkeur != 'Auto':
                return False
            else:
                return True
    elif soortOV == 'GratisOV':
        return voorkeur == 'OV'
    else:
        return True


def gewichten_berekenen_combis(config, datasource):
    logger.info("Maximum gewichten van meerdere modaliteiten")

    project_config = config['project']
    skims_config = config['skims']

    # Ophalen van instellingen
    motieven = project_config['motieven']
    regime = project_config['beprijzingsregime']
    dagsoort = skims_config['dagsoort']

    # Vaste waarden
    inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
    voorkeuren = ['Auto', 'Neutraal', 'Fiets', 'OV']
    modaliteitenfiets = ['Fiets']
    soortauto = ['Auto', 'GeenAuto', 'GeenRijbewijs', 'GratisAuto']
    soortOV = ['OV', 'GratisOV']
    soortbrandstof = ['fossiel', 'elektrisch']

    for mot in motieven:
        for ds in dagsoort:
            for ink in inkomen:
                for vk in voorkeuren:
                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            if not kanvoorkeur('Auto', srtOV, vk):
                                continue

                            vkfiets = 'Fiets' if vk == 'Fiets' else ''
                            Fietsmatrix = datasource.read_csv('gewichten', f'{modft}_vk', ds, vk=vkfiets, regime=regime, mot=mot)
                            OVmatrix = datasource.read_csv('gewichten', f'{srtOV}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)
                            max = np.maximum.reduce((Fietsmatrix, OVmatrix))
                            datasource.write_csv(max, 'gewichten', f"{srtOV}_{modft}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot)

                        for srtauto in soortauto:
                            if not kanvoorkeur(srtauto, 'OV', vk):
                                continue

                            vkfiets = 'Fiets' if vk == 'Fiets' else ''
                            Fietsmatrix = datasource.read_csv('gewichten', f'{modft}_vk', ds, vk=vkfiets, regime=regime, mot=mot)
                            if srtauto == 'Auto':
                                for srtbr in soortbrandstof:
                                    Automatrix = datasource.read_csv('gewichten', f'{srtauto}_vk', ds, vk=vk, ink=ink, srtbr=srtbr, mot=mot, regime=regime)
                                    max = np.maximum.reduce((Fietsmatrix, Automatrix))
                                    datasource.write_csv(max, 'gewichten', f"{srtauto}_{modft}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                            else:
                                Automatrix = datasource.read_csv('gewichten', f'{srtauto}_vk', ds, vk=vk, ink=ink, mot=mot, regime=regime)
                                max = np.maximum.reduce((Fietsmatrix, Automatrix))
                                datasource.write_csv(max, 'gewichten', f"{srtauto}_{modft}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot)

                    for srtOV in soortOV:
                        for srtauto in soortauto:
                            if not kanvoorkeur(srtauto, srtOV, vk):
                                continue

                            OVmatrix = datasource.read_csv('gewichten', f'{srtOV}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)
                            if srtauto == 'Auto':
                                for srtbr in soortbrandstof:
                                    Automatrix = datasource.read_csv('gewichten', f'{srtauto}_vk', ds, vk=vk, ink=ink, srtbr=srtbr, regime=regime, mot=mot)
                                    max = np.maximum.reduce((OVmatrix, Automatrix))
                                    datasource.write_csv(max, 'gewichten', f"{srtauto}_{srtOV}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                            else:
                                Automatrix = datasource.read_csv('gewichten', f'{srtauto}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                max = np.maximum.reduce((OVmatrix, Automatrix))
                                datasource.write_csv(max, 'gewichten', f"{srtauto}_{srtOV}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot)

                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            for srtauto in soortauto:
                                if not kanvoorkeur(srtauto, srtOV, vk):
                                    continue

                                vkfiets = 'Fiets' if vk == 'Fiets' else ''
                                Fietsmatrix = datasource.read_csv('gewichten', f'{modft}_vk', ds, vk=vkfiets, regime=regime, mot=mot)
                                OVmatrix = datasource.read_csv('gewichten', f'{srtOV}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        Automatrix = datasource.read_csv('gewichten', f'{srtauto}_vk', ds, vk=vk, ink=ink, srtbr=srtbr, regime=regime, mot=mot)
                                        max = np.maximum.reduce((Automatrix, Fietsmatrix, OVmatrix))
                                        datasource.write_csv(max, 'gewichten', f"{srtauto}_{srtOV}_{modft}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                else:
                                    Automatrix = datasource.read_csv('gewichten', f'{srtauto}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                    max = np.maximum.reduce((Automatrix, Fietsmatrix, OVmatrix))
                                    datasource.write_csv(max, 'gewichten', f"{srtauto}_{srtOV}_{modft}_vk", ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot)
