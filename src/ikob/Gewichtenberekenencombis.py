import logging
import ikob.Routines as Routines

logger = logging.getLogger(__name__)


def kanvoorkeur(soortauto, soortOV, voorkeur) :
    if soortauto == 'GeenAuto' or soortauto == 'GeenRijbewijs':
        if voorkeur == 'Auto':
            return False
        else :
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
            else :
                return True
        else:
            if voorkeur != 'Auto' :
                return False
            else :
                return True
    elif soortOV == 'GratisOV' :
                if voorkeur != 'OV':
                    return False
                else :
                    return True
    else :
        return True


def gewichten_berekenen_combis(config, datasource):
    project_config = config['project']
    skims_config = config['skims']

    # Ophalen van instellingen
    motieven = project_config['motieven']
    regime = project_config['beprijzingsregime']
    dagsoort = skims_config['dagsoort']
    #Scenario = config['project']['scenario']

    # Vaste waarden
    inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
    voorkeuren = ['Auto', 'Neutraal', 'Fiets', 'OV']
    modaliteitenfiets = ['Fiets']
    soortauto = ['Auto', 'GeenAuto', 'GeenRijbewijs', 'GratisAuto']
    soortOV = ['OV', 'GratisOV']
    soortbrandstof = ['fossiel','elektrisch']


    for mot in motieven:
        for ds in dagsoort:
            for ink in inkomen:
                for vk in voorkeuren:
                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            if kanvoorkeur ('Auto', srtOV, vk):
                                if vk == 'Fiets':
                                    vkklad = 'Fiets'
                                else:
                                    vkklad = ''
                                Fietsmatrix = datasource.read_csv('Gewichten', f'{modft}_vk',ds,vk=vkklad, regime=regime, mot=mot)
                                OVmatrix = datasource.read_csv('Gewichten', f'{srtOV}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                max = Routines.maxmatrix(Fietsmatrix, OVmatrix)
                                datasource.write_csv(max, 'Gewichten', f"{srtOV}_{modft}_vk", ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot)
                        for srtauto in soortauto:
                            if kanvoorkeur (srtauto, 'OV', vk):
                                if vk == 'Fiets':
                                    vkklad = 'Fiets'
                                else:
                                    vkklad = ''
                                Fietsmatrix = datasource.read_csv('Gewichten', f'{modft}_vk',ds, vk=vkklad, regime=regime, mot=mot)
                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, srtbr=srtbr, mot=mot, regime=regime)
                                        max = Routines.maxmatrix(Fietsmatrix, Automatrix)
                                        datasource.write_csv(max, 'Gewichten', f"{srtauto}_{modft}_vk", ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                else:
                                    Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, mot=mot, regime=regime)
                                    max = Routines.maxmatrix(Fietsmatrix, Automatrix)
                                    datasource.write_csv(max, 'Gewichten', f"{srtauto}_{modft}_vk", ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot)

                    for srtOV in soortOV:
                        for srtauto in soortauto:
                            if kanvoorkeur (srtauto, srtOV, vk):
                                OVmatrix = datasource.read_csv('Gewichten', f'{srtOV}_vk',ds,vk=vk,ink=ink,regime=regime, mot=mot)
                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink,srtbr=srtbr, regime=regime, mot=mot)
                                        max = Routines.maxmatrix(OVmatrix, Automatrix)
                                        datasource.write_csv(max, 'Gewichten', f"{srtauto}_{srtOV}_vk", ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                else:
                                    Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, regime=regime, mot=mot)
                                    max = Routines.maxmatrix(OVmatrix, Automatrix)
                                    datasource.write_csv(max, 'Gewichten', f"{srtauto}_{srtOV}_vk", ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot)
                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            for srtauto in soortauto:
                                if kanvoorkeur (srtauto, srtOV, vk):
                                    if vk == 'Fiets':
                                        vkklad = 'Fiets'
                                    else:
                                        vkklad = ''
                                    Fietsmatrix = datasource.read_csv('Gewichten', f'{modft}_vk',ds,vk=vkklad, regime=regime, mot=mot)
                                    OVmatrix= datasource.read_csv('Gewichten', f'{srtOV}_vk',ds,vk=vk,ink=ink, regime=regime, mot=mot)
                                    if srtauto == 'Auto':
                                        for srtbr in soortbrandstof:
                                            Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink,srtbr=srtbr, regime=regime, mot=mot)
                                            max = Routines.maxmatrix(Automatrix, Fietsmatrix, OVmatrix)
                                            datasource.write_csv(max,'Gewichten', f"{srtauto}_{srtOV}_{modft}_vk",ds,subtopic='Combinaties', vk=vk,ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                    else:
                                        Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, regime=regime, mot=mot)
                                        max = Routines.maxmatrix(Automatrix, Fietsmatrix, OVmatrix)
                                        datasource.write_csv(max,'Gewichten', f"{srtauto}_{srtOV}_{modft}_vk",ds,subtopic='Combinaties', vk=vk,ink=ink, regime=regime, mot=mot)
