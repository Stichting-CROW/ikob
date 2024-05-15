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

def Maxberekenen_en_wegschrijven(datasource, Matrix1, Matrix2, mod1, mod2, vk, ink, ds, regime, mot, srtbr=''):
    Maxmatrix = Routines.maxmatrix ( Matrix1, Matrix2 )
    return datasource.write_csv(Maxmatrix,'Gewichten', f"{mod1}_{mod2}_vk",ds,subtopic='Combinaties', vk=vk,ink=ink, srtbr=srtbr, regime=regime, mot=mot)

def Maxberekenen_en_wegschrijvenvan3(datasource, Matrix1, Matrix2, Matrix3, mod1, mod2, mod3, vk, ink, ds, regime, mot, srtbr=''):
    Maxmatrix = Routines.maxmatrix3 ( Matrix1, Matrix2, Matrix3 )
    return datasource.write_csv(Maxmatrix,'Gewichten', f"{mod1}_{mod2}_{mod3}_vk",ds,subtopic='Combinaties', vk=vk,ink=ink, srtbr=srtbr, regime=regime, mot=mot)

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
                                Maxberekenen_en_wegschrijven(datasource, Fietsmatrix, OVmatrix, srtOV, modft, vk, ink, ds, regime=regime, mot=mot)
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
                                        Maxberekenen_en_wegschrijven(datasource, Fietsmatrix, Automatrix, srtauto, modft, vk, ink, ds, regime=regime, mot=mot, srtbr=srtbr)
                                else:
                                    Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, mot=mot, regime=regime)
                                    Maxberekenen_en_wegschrijven(datasource, Fietsmatrix, Automatrix, srtauto, modft, vk, ink, ds, regime=regime, mot=mot)

                    for srtOV in soortOV:
                        for srtauto in soortauto:
                            if kanvoorkeur (srtauto, srtOV, vk):
                                OVmatrix = datasource.read_csv('Gewichten', f'{srtOV}_vk',ds,vk=vk,ink=ink,regime=regime, mot=mot)
                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink,srtbr=srtbr, regime=regime, mot=mot)
                                        Maxberekenen_en_wegschrijven(datasource, OVmatrix, Automatrix, srtauto, srtOV, vk, ink, ds, regime=regime, mot=mot, srtbr=srtbr)
                                else:
                                    Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, regime=regime, mot=mot)
                                    Maxberekenen_en_wegschrijven(datasource, OVmatrix, Automatrix, srtauto, srtOV, vk, ink, ds, regime=regime, mot=mot)
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
                                            Maxberekenen_en_wegschrijvenvan3(datasource, Automatrix, Fietsmatrix, OVmatrix, srtauto, srtOV, modft, vk, ink, ds, regime=regime, mot=mot, srtbr=srtbr)
                                    else:
                                        Automatrix = datasource.read_csv('Gewichten', f'{srtauto}_vk',ds,vk=vk,ink=ink, regime=regime, mot=mot)
                                        Maxberekenen_en_wegschrijvenvan3(datasource, Automatrix, Fietsmatrix, OVmatrix, srtauto, srtOV, modft, vk, ink, ds, mot=mot, regime=regime)
