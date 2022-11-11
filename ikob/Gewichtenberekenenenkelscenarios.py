import Routines
import Berekeningen
import Constantengenerator
from tkinter import filedialog
from tkinter import *
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
Skimsdirectory = paden_config['skims_directory']
dagsoort = skims_config['dagsoort']
#Scenario = project_config['scenario']
motieven = project_config['motieven']


# Vaste waarden
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
voorkeuren = ['Auto','Neutraal','Fiets','OV']
modaliteitenfiets = ['Fiets', 'EFiets']


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

def gewichtenberekenen (skim, alpha, omega, weging):
    import math
    print (alpha, omega, weging)
    Gewichtenmatrix = []

    for r in range(0, len(skim)):
        Gewichtenmatrix.append([])
        for k in range(0, len(skim)):
            ervaren_reistijd = skim[r][k]
            if ervaren_reistijd < 180:
                reistijdwaarde = (1 / (1 + math.exp((-omega + ervaren_reistijd)*alpha)))*weging
            else:
                reistijdwaarde = 0
            if reistijdwaarde < 0.001 :
                reistijdwaarde = 0
            Gewichtenmatrix[r].append( round(reistijdwaarde,4) )
    return Gewichtenmatrix

# Avondspits en Ochtendspits eruit verwijderd

for ds in dagsoort:
    for mot in motieven:
        Gewichtendirectory = os.path.join ( Skimsdirectory, Projectbestandsnaam, 'Gewichten', ds )
        #Gewichtendirectory = os.path.join ( Skimsdirectory, 'Gewichten', Scenario, ds )
        os.makedirs(Gewichtendirectory,exist_ok=True)
        Ervarenreistijddirectory = os.path.join ( Skimsdirectory, Projectbestandsnaam, 'Ervarenreistijd', ds)
        #Ervarenreistijddirectory = os.path.join ( Skimsdirectory, 'Ervarenreistijd', Scenario, ds )
        for mod in modaliteitenfiets:
            for vk in voorkeuren:
                if vk == 'Auto' or vk == 'Fiets':
                    Filenaam = os.path.join(Ervarenreistijddirectory,'Fiets')
                    GGRskim = Routines.csvintlezen(Filenaam, aantal_lege_regels=0)

                    if mot == 'werk':
                        constanten = Constantengenerator.alomwerk ( mod, vk )
                    elif mot == 'winkeldagelijkszorg':
                        constanten = Constantengenerator.alomwinkeldagelijkszorg ( mod, vk )
                    else:
                        constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( mod, vk )
                    alpha = constanten[0]
                    omega = constanten[1]
                    weging = constanten[2]
                    print ( alpha, omega, weging )
                    Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging)
                    if vk == 'Auto':
                        Uitvoerfilenaam = os.path.join(Gewichtendirectory, f'{mod}_vk')
                    else :
                        Uitvoerfilenaam = os.path.join(Gewichtendirectory, f'{mod}_vk{vk}' )
                    Routines.csvwegschrijven(Gewichten,Uitvoerfilenaam)
        # Nu Auto
        for ink in inkomen:
            for vk in voorkeuren:
                if mot != 'werk':
                    soort = 'overig'
                else:
                    soort = 'werk'
                ErvarenReistijdfilenaam = os.path.join(Ervarenreistijddirectory, f'Auto_{ink}')
                #ErvarenReistijdfilenaam = os.path.join(Ervarenreistijddirectory, f'Auto_{soort}_{ink}')
                GGRskim = Routines.csvintlezen(ErvarenReistijdfilenaam)
                if mot == 'werk':
                    constanten = Constantengenerator.alomwerk ('Auto', vk )
                elif mot == 'winkeldagelijkszorg':
                    constanten = Constantengenerator.alomwinkeldagelijkszorg ('Auto', vk )
                else:
                    constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ('Auto', vk )
                alpha = constanten[0]
                omega = constanten[1]
                weging = constanten[2]
                print ( alpha, omega, weging )
                Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging )
                Uitvoerfilenaam = os.path.join (Gewichtendirectory,f'Auto_vk{vk}_{ink}')
                Routines.csvwegschrijven(Gewichten,Uitvoerfilenaam)

        soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
        voorkeurengeenauto = ['Neutraal', 'OV', 'Fiets']
        for sga in soortgeenauto:
            for vk in voorkeurengeenauto :
                for ink in inkomen:
                    if mot != 'werk':
                        soort = 'overig'
                    else:
                        soort = 'werk'
                    ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'{sga}_{ink}' )
                    #ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'{sga}_{soort}_{ink}' )
                    GGRskim = Routines.csvfloatlezen ( ErvarenReistijdfilenaam )
                    if mot == 'werk':
                        constanten = Constantengenerator.alomwerk ( 'Auto',vk )
                    elif mot == 'winkeldagelijkszorg':
                        constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'Auto', vk )
                    else:
                        constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'Auto', vk )
                    alpha = constanten[0]
                    omega = constanten[1]
                    weging = constanten[2]
                    print ( alpha, omega, weging )
                    Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging)
                    Uitvoerfilenaam = os.path.join ( Gewichtendirectory, f'{sga}_vk{vk}_{ink}' )
                    Routines.csvwegschrijven ( Gewichten, Uitvoerfilenaam )

        # Nu OV
        modaliteitenOV = ['OV']
        for modOV in modaliteitenOV:
            for ink in inkomen:
                for vk in voorkeuren:
                    if mot != 'werk':
                        soort = 'overig'
                    else:
                        soort = 'werk'
                    #ErvarenReistijdfilenaam = os.path.join(Ervarenreistijddirectory, f'{modOV}_{soort}_{ink}')
                    ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'{modOV}_{ink}' )
                    GGRskim = Routines.csvintlezen(ErvarenReistijdfilenaam)

                    if mot == 'werk':
                        constanten = Constantengenerator.alomwerk ( modOV, vk )
                    elif mot == 'winkeldagelijks' or 'onderwijs':
                        constanten = Constantengenerator.alomwinkeldagelijkszorg ( modOV, vk )
                    else:
                        constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( modOV, vk )
                    alpha = constanten[0]
                    omega = constanten[1]
                    weging = constanten[2]
                    print ( alpha, omega, weging )
                    Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging)
                    Uitvoerfilenaam = os.path.join(Gewichtendirectory, f'{modOV}_vk{vk}_{ink}')
                    Routines.csvwegschrijven(Gewichten,Uitvoerfilenaam)

        for ink in inkomen:
            if mot != 'werk':
                soort = 'overig'
            else:
                soort = 'werk'
            #ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'GratisAuto_{soort}_{ink}')
            ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'GratisAuto_{ink}' )
            GGRskim = Routines.csvintlezen ( ErvarenReistijdfilenaam )
            if mot == 'werk':
                constanten = Constantengenerator.alomwerk ( 'Auto', 'Auto' )
            elif mot == 'winkeldagelijkszorg':
                constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'Auto', 'Auto' )
            else:
                constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'Auto', 'Auto' )
            alpha = constanten[0]
            omega = constanten[1]
            weging = constanten[2]
            print ( alpha, omega, weging )
            Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging )
            specialauto = ['Neutraal', 'Auto']
            for vks in specialauto:
                Uitvoerfilenaam = os.path.join ( Gewichtendirectory, f'GratisAuto_vk{vks}_{ink}' )
                Routines.csvwegschrijven ( Gewichten, Uitvoerfilenaam )

            ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'GratisOV' )
            GGRskim = Routines.csvintlezen ( ErvarenReistijdfilenaam )
            GGRskimLen = len(GGRskim)
            if mot == 'werk':
                constanten = Constantengenerator.alomwerk ( 'OV', 'OV' )
            elif mot == 'winkeldagelijkszorg':
                constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'OV', 'OV' )
            else:
                constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'OV', 'OV' )
            alpha = constanten[0]
            omega = constanten[1]
            weging = constanten[2]
            print ( alpha, omega, weging )
            Gewichten = gewichtenberekenen ( GGRskim, alpha, omega, weging )
            specialOV = ['Neutraal', 'OV']
            for vks in specialOV:
                Uitvoerfilenaam = os.path.join ( Gewichtendirectory, f'GratisOV_vk{vks}_{ink}' )
                Routines.csvwegschrijven ( Gewichten, Uitvoerfilenaam )
