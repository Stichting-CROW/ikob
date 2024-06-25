import logging
import numpy as np
from ikob.datasource import DataSource, DataKey

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


def gewichten_berekenen_combis(config, datasource: DataSource):
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
                            key = DataKey('gewichten', f'{modft}_vk',
                                          dagsoort=ds,
                                          voorkeur=vkfiets,
                                          regime=regime,
                                          motief=mot)
                            Fietsmatrix = datasource.read_csv(key)

                            key = DataKey('gewichten', f'{srtOV}_vk',
                                          dagsoort=ds,
                                          voorkeur=vk,
                                          inkomen=ink,
                                          regime=regime,
                                          motief=mot)
                            OVmatrix = datasource.read_csv(key)

                            max = np.maximum.reduce((Fietsmatrix, OVmatrix))
                            key = DataKey('gewichten',
                                          f"{srtOV}_{modft}_vk",
                                          dagsoort=ds,
                                          inkomen=ink,
                                          regime=regime,
                                          motief=mot,
                                          voorkeur=vk,
                                          subtopic='combinaties')
                            datasource.write_csv(max, key)

                        for srtauto in soortauto:
                            if not kanvoorkeur(srtauto, 'OV', vk):
                                continue

                            vkfiets = 'Fiets' if vk == 'Fiets' else ''
                            key = DataKey('gewichten', f'{modft}_vk',
                                          dagsoort=ds,
                                          voorkeur=vkfiets,
                                          regime=regime,
                                          motief=mot)
                            Fietsmatrix = datasource.read_csv(key)

                            if srtauto == 'Auto':
                                for srtbr in soortbrandstof:
                                    key = DataKey('gewichten', f'{srtauto}_vk',
                                                  dagsoort=ds,
                                                  voorkeur=vk,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  brandstof=srtbr)
                                    Automatrix = datasource.read_csv(key)

                                    max = np.maximum.reduce((Fietsmatrix, Automatrix))
                                    key = DataKey('gewichten',
                                                  f"{srtauto}_{modft}_vk",
                                                  dagsoort=ds,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  voorkeur=vk,
                                                  subtopic='combinaties',
                                                  brandstof=srtbr)
                                    datasource.write_csv(max, key)
                            else:
                                key = DataKey('gewichten', f'{srtauto}_vk',
                                              dagsoort=ds,
                                              voorkeur=vk,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot)
                                Automatrix = datasource.read_csv(key)

                                max = np.maximum.reduce((Fietsmatrix, Automatrix))
                                key = DataKey('gewichten',
                                              f"{srtauto}_{modft}_vk",
                                              dagsoort=ds,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot,
                                              voorkeur=vk,
                                              subtopic='combinaties')
                                datasource.write_csv(max, key)

                    for srtOV in soortOV:
                        for srtauto in soortauto:
                            if not kanvoorkeur(srtauto, srtOV, vk):
                                continue

                            key = DataKey('gewichten', f'{srtOV}_vk',
                                          dagsoort=ds,
                                          voorkeur=vk,
                                          inkomen=ink,
                                          regime=regime,
                                          motief=mot)
                            OVmatrix = datasource.read_csv(key)

                            if srtauto == 'Auto':
                                for srtbr in soortbrandstof:
                                    key = DataKey('gewichten', f'{srtauto}_vk',
                                                  dagsoort=ds,
                                                  voorkeur=vk,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  brandstof=srtbr)
                                    Automatrix = datasource.read_csv(key)
                                    max = np.maximum.reduce((OVmatrix, Automatrix))
                                    key = DataKey('gewichten',
                                                  f"{srtauto}_{srtOV}_vk",
                                                  dagsoort=ds,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  voorkeur=vk,
                                                  subtopic='combinaties',
                                                  brandstof=srtbr)
                                    datasource.write_csv(max, key)
                            else:
                                key = DataKey('gewichten', f'{srtauto}_vk',
                                              dagsoort=ds,
                                              voorkeur=vk,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot)
                                Automatrix = datasource.read_csv(key)

                                max = np.maximum.reduce((OVmatrix, Automatrix))
                                key = DataKey('gewichten',
                                              f"{srtauto}_{srtOV}_vk",
                                              dagsoort=ds,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot,
                                              voorkeur=vk,
                                              subtopic='combinaties')
                                datasource.write_csv(max, key)

                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            for srtauto in soortauto:
                                if not kanvoorkeur(srtauto, srtOV, vk):
                                    continue

                                vkfiets = 'Fiets' if vk == 'Fiets' else ''
                                key = DataKey('gewichten', f'{modft}_vk',
                                              dagsoort=ds,
                                              voorkeur=vkfiets,
                                              regime=regime,
                                              motief=mot)
                                Fietsmatrix = datasource.read_csv(key)

                                key = DataKey('gewichten', f'{srtOV}_vk',
                                              dagsoort=ds,
                                              voorkeur=vk,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot)
                                OVmatrix = datasource.read_csv(key)

                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        key = DataKey('gewichten', f'{srtauto}_vk',
                                                      dagsoort=ds,
                                                      voorkeur=vk,
                                                      inkomen=ink,
                                                      regime=regime,
                                                      motief=mot,
                                                      brandstof=srtbr)
                                        Automatrix = datasource.read_csv(key)

                                        max = np.maximum.reduce((Automatrix, Fietsmatrix, OVmatrix))
                                        key = DataKey('gewichten',
                                                      f"{srtauto}_{srtOV}_{modft}_vk",
                                                      dagsoort=ds,
                                                      inkomen=ink,
                                                      regime=regime,
                                                      motief=mot,
                                                      voorkeur=vk,
                                                      subtopic='combinaties',
                                                      brandstof=srtbr)
                                        datasource.write_csv(max, key)
                                else:
                                    key = DataKey('gewichten', f'{srtauto}_vk',
                                                  dagsoort=ds,
                                                  voorkeur=vk,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot)
                                    Automatrix = datasource.read_csv(key)

                                    max = np.maximum.reduce((Automatrix, Fietsmatrix, OVmatrix))
                                    key = DataKey('gewichten',
                                                  f"{srtauto}_{srtOV}_{modft}_vk",
                                                  dagsoort=ds,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  voorkeur=vk,
                                                  subtopic='combinaties')
                                    datasource.write_csv(max, key)
