import logging
import numpy as np
from ikob.datasource import DataSource, DataKey, DataType

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


def gewichten_berekenen_combis(config, gewichten_enkel: DataSource) -> DataSource:
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

    gewichten_combi = DataSource(config, DataType.GEWICHTEN)

    for mot in motieven:
        for ds in dagsoort:
            for ink in inkomen:
                for vk in voorkeuren:
                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            if not kanvoorkeur('Auto', srtOV, vk):
                                continue

                            vkfiets = 'Fiets' if vk == 'Fiets' else ''
                            key = DataKey(f'{modft}_vk',
                                          dagsoort=ds,
                                          voorkeur=vkfiets,
                                          regime=regime,
                                          motief=mot)
                            Fietsmatrix = gewichten_enkel.get(key)

                            key = DataKey(f'{srtOV}_vk',
                                          dagsoort=ds,
                                          voorkeur=vk,
                                          inkomen=ink,
                                          regime=regime,
                                          motief=mot)
                            OVmatrix = gewichten_enkel.get(key)

                            max = np.maximum.reduce((Fietsmatrix, OVmatrix))
                            key = DataKey(f"{srtOV}_{modft}_vk",
                                          dagsoort=ds,
                                          inkomen=ink,
                                          regime=regime,
                                          motief=mot,
                                          voorkeur=vk,
                                          subtopic='combinaties')
                            gewichten_combi.set(key, max.copy())

                        for srtauto in soortauto:
                            if not kanvoorkeur(srtauto, 'OV', vk):
                                continue

                            vkfiets = 'Fiets' if vk == 'Fiets' else ''
                            key = DataKey(f'{modft}_vk',
                                          dagsoort=ds,
                                          voorkeur=vkfiets,
                                          regime=regime,
                                          motief=mot)
                            Fietsmatrix = gewichten_enkel.get(key)

                            if srtauto == 'Auto':
                                for srtbr in soortbrandstof:
                                    key = DataKey(f'{srtauto}_vk',
                                                  dagsoort=ds,
                                                  voorkeur=vk,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  brandstof=srtbr)
                                    Automatrix = gewichten_enkel.get(key)

                                    max = np.maximum.reduce((Fietsmatrix, Automatrix))
                                    key = DataKey(f"{srtauto}_{modft}_vk",
                                                  dagsoort=ds,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  voorkeur=vk,
                                                  subtopic='combinaties',
                                                  brandstof=srtbr)
                                    gewichten_combi.set(key, max.copy())
                            else:
                                key = DataKey(f'{srtauto}_vk',
                                              dagsoort=ds,
                                              voorkeur=vk,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot)
                                Automatrix = gewichten_enkel.get(key)

                                max = np.maximum.reduce((Fietsmatrix, Automatrix))
                                key = DataKey(f"{srtauto}_{modft}_vk",
                                              dagsoort=ds,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot,
                                              voorkeur=vk,
                                              subtopic='combinaties')
                                gewichten_combi.set(key, max.copy())

                    for srtOV in soortOV:
                        for srtauto in soortauto:
                            if not kanvoorkeur(srtauto, srtOV, vk):
                                continue

                            key = DataKey(f'{srtOV}_vk',
                                          dagsoort=ds,
                                          voorkeur=vk,
                                          inkomen=ink,
                                          regime=regime,
                                          motief=mot)
                            OVmatrix = gewichten_enkel.get(key)

                            if srtauto == 'Auto':
                                for srtbr in soortbrandstof:
                                    key = DataKey(f'{srtauto}_vk',
                                                  dagsoort=ds,
                                                  voorkeur=vk,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  brandstof=srtbr)
                                    Automatrix = gewichten_enkel.get(key)
                                    max = np.maximum.reduce((OVmatrix, Automatrix))
                                    key = DataKey(f"{srtauto}_{srtOV}_vk",
                                                  dagsoort=ds,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  voorkeur=vk,
                                                  subtopic='combinaties',
                                                  brandstof=srtbr)
                                    gewichten_combi.set(key, max.copy())
                            else:
                                key = DataKey(f'{srtauto}_vk',
                                              dagsoort=ds,
                                              voorkeur=vk,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot)
                                Automatrix = gewichten_enkel.get(key)

                                max = np.maximum.reduce((OVmatrix, Automatrix))
                                key = DataKey(f"{srtauto}_{srtOV}_vk",
                                              dagsoort=ds,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot,
                                              voorkeur=vk,
                                              subtopic='combinaties')
                                gewichten_combi.set(key, max.copy())

                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            for srtauto in soortauto:
                                if not kanvoorkeur(srtauto, srtOV, vk):
                                    continue

                                vkfiets = 'Fiets' if vk == 'Fiets' else ''
                                key = DataKey(f'{modft}_vk',
                                              dagsoort=ds,
                                              voorkeur=vkfiets,
                                              regime=regime,
                                              motief=mot)
                                Fietsmatrix = gewichten_enkel.get(key)

                                key = DataKey(f'{srtOV}_vk',
                                              dagsoort=ds,
                                              voorkeur=vk,
                                              inkomen=ink,
                                              regime=regime,
                                              motief=mot)
                                OVmatrix = gewichten_enkel.get(key)

                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        key = DataKey(f'{srtauto}_vk',
                                                      dagsoort=ds,
                                                      voorkeur=vk,
                                                      inkomen=ink,
                                                      regime=regime,
                                                      motief=mot,
                                                      brandstof=srtbr)
                                        Automatrix = gewichten_enkel.get(key)

                                        max = np.maximum.reduce((Automatrix, Fietsmatrix, OVmatrix))
                                        key = DataKey(f"{srtauto}_{srtOV}_{modft}_vk",
                                                      dagsoort=ds,
                                                      inkomen=ink,
                                                      regime=regime,
                                                      motief=mot,
                                                      voorkeur=vk,
                                                      subtopic='combinaties',
                                                      brandstof=srtbr)
                                        gewichten_combi.set(key, max.copy())
                                else:
                                    key = DataKey(f'{srtauto}_vk',
                                                  dagsoort=ds,
                                                  voorkeur=vk,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot)
                                    Automatrix = gewichten_enkel.get(key)

                                    max = np.maximum.reduce((Automatrix, Fietsmatrix, OVmatrix))
                                    key = DataKey(f"{srtauto}_{srtOV}_{modft}_vk",
                                                  dagsoort=ds,
                                                  inkomen=ink,
                                                  regime=regime,
                                                  motief=mot,
                                                  voorkeur=vk,
                                                  subtopic='combinaties')
                                    gewichten_combi.set(key, max.copy())

    return gewichten_combi
