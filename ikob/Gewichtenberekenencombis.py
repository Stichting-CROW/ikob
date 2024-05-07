import logging
import Routines
import os

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

def Maxberekenen_en_wegschrijven (Directory,Matrix1, Matrix2,mod1, mod2,vk,ink):
    Maxmatrix = Routines.minmaxmatrix ( Matrix1, Matrix2 )
    Uitvoerfilenaam = os.path.join (Directory, f'{mod1}_{mod2}_vk{vk}_{ink}')
    logger.debug("Uitvoerfilenaam is %s", Uitvoerfilenaam)
    Routines.csvwegschrijven ( Maxmatrix, Uitvoerfilenaam )
    return

def Maxberekenen_en_wegschrijvenvan3 (Directory, Matrix1, Matrix2, Matrix3, mod1, mod2, mod3, vk,ink):
    Maxmatrix = Routines.minmaxmatrix3 ( Matrix1, Matrix2, Matrix3 )
    Uitvoerfilenaam = os.path.join (Directory, f'{mod1}_{mod2}_{mod3}_vk{vk}_{ink}')
    Routines.csvwegschrijven ( Maxmatrix, Uitvoerfilenaam )
    return

def gewichten_berekenen_combis(config):
    project_config = config['project']
    paden_config = config['project']['paden']
    skims_config = config['skims']


    # Ophalen van instellingen
    Basisdirectory = paden_config['skims_directory']
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

            Combinatiedirectory = os.path.join(Basisdirectory, regime, mot, 'Gewichten', 'Combinaties', ds)
            Enkeldirectory = os.path.join(Basisdirectory, regime, mot, 'Gewichten', ds)
            #Combinatiedirectory = os.path.join ( Skimsdirectory, 'Gewichten', 'Combinaties', Scenario, ds )
            #Enkeldirectory = os.path.join ( Skimsdirectory, 'Gewichten', Scenario, ds )
            os.makedirs(Combinatiedirectory, exist_ok=True)

            for ink in inkomen:
                for vk in voorkeuren:
                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            if kanvoorkeur ('Auto', srtOV, vk):
                                if vk == 'Fiets':
                                    vkklad = 'Fiets'
                                else:
                                    vkklad = ''
                                Fietsfile = os.path.join (Enkeldirectory, f'{modft}_vk{vkklad}')
                                Fietsmatrix = Routines.csvlezen(Fietsfile)
                                OVfile = os.path.join (Enkeldirectory, f'{srtOV}_vk{vk}_{ink}')
                                OVmatrix = Routines.csvlezen(OVfile)
                                Maxberekenen_en_wegschrijven(Combinatiedirectory, Fietsmatrix,OVmatrix, srtOV, modft, vk, ink)
                        for srtauto in soortauto:
                            if kanvoorkeur (srtauto, 'OV', vk):
                                if vk == 'Fiets':
                                    vkklad = 'Fiets'
                                else:
                                    vkklad = ''
                                Fietsfile = os.path.join ( Enkeldirectory, f'{modft}_vk{vkklad}' )
                                Fietsmatrix = Routines.csvlezen ( Fietsfile )
                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        Autofile = os.path.join ( Enkeldirectory, srtbr, f'{srtauto}_vk{vk}_{ink}' )
                                        Automatrix = Routines.csvlezen ( Autofile )
                                        logger.debug("Autofile: %s", Autofile)
                                        logger.debug("Fietsfile: %s", Fietsfile)
                                        Brandstofdirectory = os.path.join (Combinatiedirectory, srtbr)
                                        os.makedirs(Brandstofdirectory, exist_ok=True)
                                        Maxberekenen_en_wegschrijven ( Brandstofdirectory, Fietsmatrix,
                                                                       Automatrix, srtauto, modft, vk, ink )
                                else:
                                    Autofile = os.path.join(Enkeldirectory, f'{srtauto}_vk{vk}_{ink}')
                                    Automatrix = Routines.csvlezen(Autofile)
                                    Maxberekenen_en_wegschrijven(Combinatiedirectory, Fietsmatrix, Automatrix, srtauto, modft, vk, ink)

                    for srtOV in soortOV:
                        for srtauto in soortauto:
                            if kanvoorkeur (srtauto, srtOV, vk):
                                OVfile = os.path.join ( Enkeldirectory, f'{srtOV}_vk{vk}_{ink}' )
                                OVmatrix = Routines.csvlezen ( OVfile )
                                if srtauto == 'Auto':
                                    for srtbr in soortbrandstof:
                                        Autofile = os.path.join(Enkeldirectory, srtbr, f'{srtauto}_vk{vk}_{ink}')
                                        Automatrix = Routines.csvlezen(Autofile)
                                        logger.debug("Autofile: %s", Autofile)
                                        logger.debug("Belangrijk! OVFile=%s", OVfile)
                                        Brandstofdirectory = os.path.join (Combinatiedirectory, srtbr)
                                        os.makedirs(Brandstofdirectory, exist_ok=True)
                                        Maxberekenen_en_wegschrijven ( Brandstofdirectory, OVmatrix, Automatrix, srtauto, srtOV, vk, ink )
                                else:
                                    Autofile = os.path.join(Enkeldirectory, f'{srtauto}_vk{vk}_{ink}')
                                    Automatrix = Routines.csvlezen(Autofile)
                                    Maxberekenen_en_wegschrijven(Combinatiedirectory, OVmatrix, Automatrix,
                                                                 srtauto, srtOV, vk, ink)
                    for modft in modaliteitenfiets:
                        for srtOV in soortOV:
                            for srtauto in soortauto:
                                if kanvoorkeur (srtauto, srtOV, vk):
                                    if vk == 'Fiets':
                                        vkklad = 'Fiets'
                                    else:
                                        vkklad = ''
                                    Fietsfile = os.path.join (Enkeldirectory, f'{modft}_vk{vkklad}')
                                    Fietsmatrix = Routines.csvlezen(Fietsfile)
                                    OVfile = os.path.join (Enkeldirectory, f'{srtOV}_vk{vk}_{ink}')
                                    OVmatrix = Routines.csvlezen(OVfile)
                                    if srtauto == 'Auto':
                                        for srtbr in soortbrandstof:
                                            Autofile = os.path.join(Enkeldirectory, srtbr, f'{srtauto}_vk{vk}_{ink}')
                                            Automatrix = Routines.csvlezen(Autofile)
                                            logger.debug("Autofile: %s", Autofile)
                                            logger.debug("Fietsfile: %s", Fietsfile)
                                            logger.debug("OVfile: %s", OVfile)
                                            Brandstofdirectory = os.path.join(Combinatiedirectory, srtbr)
                                            os.makedirs(Brandstofdirectory, exist_ok=True)
                                            Maxberekenen_en_wegschrijvenvan3(Brandstofdirectory,Automatrix,
                                                                             Fietsmatrix, OVmatrix, srtauto, srtOV,
                                                                             modft, vk, ink)
                                    else:
                                        Autofile = os.path.join(Enkeldirectory,f'{srtauto}_vk{vk}_{ink}')
                                        Automatrix = Routines.csvlezen(Autofile)
                                        Maxberekenen_en_wegschrijvenvan3(Combinatiedirectory,Automatrix,
                                                                         Fietsmatrix, OVmatrix, srtauto, srtOV,
                                                                         modft, vk, ink)
