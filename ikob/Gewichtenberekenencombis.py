import Routines
import os
from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()
Projectbestandsnaam = config['__filename__']  # nieuw automatisch toegevoegd config item.
project_config = config['project']
paden_config = config['project']['paden']
skims_config = config['skims']


# Ophalen van instellingen
Basisdirectory = paden_config['skims_directory']
motieven = project_config['motieven']
dagsoort = skims_config['dagsoort']
#Scenario = config['project']['scenario']

# Vaste waarden
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
voorkeuren = ['Auto', 'Neutraal', 'Fiets', 'OV']
modaliteitenfiets = ['Fiets', 'EFiets']
soortauto = ['Auto', 'GeenAuto', 'GeenRijbewijs', 'GratisAuto']
soortOV = ['OV', 'GratisOV']


def minmaxmatrix(matrix1, matrix2, minmax="max"):
    eindmatrix = []
    for i in range(0, len(matrix1)):
        eindmatrix.append([])
        for j in range(0, len(matrix1)):
            if minmax == "max":
                eindmatrix[i].append(max(matrix1[i][j], matrix2[i][j]))
            else:
                eindmatrix[i].append(min(matrix1[i][j], matrix2[i][j]))
    return eindmatrix


def minmaxmatrix3(matrix1, matrix2, matrix3, minmax="max"):
    eindmatrix = []
    for i in range(0, len(matrix1)):
        eindmatrix.append([])
        for j in range(0, len(matrix1)):
            if minmax == "max":
                eindmatrix[i].append(max(matrix1[i][j], matrix2[i][j], matrix3[i][j]))
            else:
                eindmatrix[i].append(min(matrix1[i][j], matrix2[i][j], matrix3[i][j]))
    return eindmatrix

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

def Maxberekenen_en_wegschrijven (Matrix1, Matrix2,mod1, mod2,vk,ink):
    Maxmatrix = minmaxmatrix ( Matrix1, Matrix2 )
    Uitvoerfilenaam = os.path.join (Combinatiedirectory, f'{mod1}_{mod2}_vk{vk}_{ink}')
    Routines.csvwegschrijven ( Maxmatrix, Uitvoerfilenaam )
    return

def Maxberekenen_en_wegschrijvenvan3 (Matrix1, Matrix2, Matrix3, mod1, mod2, mod3, vk,ink):
    Maxmatrix = minmaxmatrix3 ( Matrix1, Matrix2, Matrix3 )
    Uitvoerfilenaam = os.path.join (Combinatiedirectory, f'{mod1}_{mod2}_{mod3}_vk{vk}_{ink}')
    Routines.csvwegschrijven ( Maxmatrix, Uitvoerfilenaam )
    return

for ds in dagsoort:

    Combinatiedirectory = os.path.join(Basisdirectory, 'Gewichten', 'Combinaties', ds)
    Enkeldirectory = os.path.join(Basisdirectory, 'Gewichten', ds)
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
                        Maxberekenen_en_wegschrijven(Fietsmatrix,OVmatrix, srtOV, modft, vk, ink)

                for srtauto in soortauto:
                    if kanvoorkeur (srtauto, 'OV', vk):
                        if vk == 'Fiets':
                            vkklad = 'Fiets'
                        else:
                            vkklad = ''
                        Fietsfile = os.path.join ( Enkeldirectory, f'{modft}_vk{vkklad}' )
                        Fietsmatrix = Routines.csvlezen ( Fietsfile )
                        Autofile = os.path.join ( Enkeldirectory, f'{srtauto}_vk{vk}_{ink}' )
                        Automatrix = Routines.csvlezen ( Autofile )
                        Maxberekenen_en_wegschrijven ( Fietsmatrix, Automatrix, srtauto, modft, vk, ink )

            for srtOV in soortOV:
                for srtauto in soortauto:
                    if kanvoorkeur (srtauto, srtOV, vk):
                        OVfile = os.path.join ( Enkeldirectory, f'{srtOV}_vk{vk}_{ink}' )
                        OVmatrix = Routines.csvlezen ( OVfile )
                        Autofile = os.path.join ( Enkeldirectory, f'{srtauto}_vk{vk}_{ink}' )
                        Automatrix = Routines.csvlezen ( Autofile )
                        Maxberekenen_en_wegschrijven ( OVmatrix, Automatrix, srtauto, srtOV, vk, ink )

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
                            Autofile = os.path.join ( Enkeldirectory, f'{srtauto}_vk{vk}_{ink}' )
                            Automatrix = Routines.csvlezen ( Autofile )
                            Maxberekenen_en_wegschrijvenvan3(Automatrix, Fietsmatrix, OVmatrix, srtauto, srtOV, modft, vk, ink)
