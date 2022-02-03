import Routines
import Berekeningen
import Constantengenerator
from tkinter import filedialog
from tkinter import *
import os

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'

mot = input ('Welk motief?')
# 'winkeldagelijkszorg', 'winkelnietdagelijksonderwijs' verwijderd
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
voorkeuren = ['Auto','Neutraal','Fiets','OV']
dagsoort = ['Restdag']
modaliteitenfiets = ['Fiets', 'EFiets']
Scenario = input('Voor welk scenario moet de berekening zijn?')


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
            Gewichtenmatrix[r].append( int(10000*reistijdwaarde) )
    return Gewichtenmatrix

# Avondspits en Ochtendspits eruit verwijderd

for ds in dagsoort:
        Gewichtendirectory = os.path.join (Skimsdirectory,'Gewichten', Scenario,ds)
        os.makedirs(Gewichtendirectory,exist_ok=True)
        Ervarenreistijddirectory = os.path.join ( Skimsdirectory, 'Ervarenreistijd', Scenario, ds)
        for mod in modaliteitenfiets:
            for vk in voorkeuren:
                if vk == 'Auto' or vk == 'Fiets':
                    Filenaam = os.path.join(Ervarenreistijddirectory,'Fiets')
                    GGRskim = Routines.csvintlezen(Filenaam, aantal_lege_regels=0)

                    print("GGRskim heeft {} regels.".format(len(GGRskim)))
                    if mot == 'werk':
                        constanten = Constantengenerator.alomwerk ( mod, vk )
                    elif mot == 'winkeldagelijkszorg':
                        constanten = Constantengenerator.alomwinkeldagelijkszorg ( mod, vk )
                    else:
                        constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( mod, vk )
                    Gewichten = Berekeningen.gewichten( GGRskim, constanten)
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
                alpha = constantenwerk ('Auto',vk)[0]
                omega = constantenwerk ( 'Auto', vk )[1]
                weging = constantenwerk ( 'Auto', vk )[2]
                print(alpha,omega,weging)
                Gewichten = gewichtenberekenen( GGRskim, alpha, omega, weging )
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
                    print ('Ik ben nu bezig met {}, {}, {},{}', ds, mot, sga, ink)
                    Gewichten = Berekeningen.gewichten( GGRskim, constanten)
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
                    print (modOV,vk,constanten)
                    Gewichten = Berekeningen.gewichten( GGRskim, constanten )
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
            Gewichten = Berekeningen.gewichten ( GGRskim, constanten)
            specialauto = ['Neutraal', 'Auto']
            for vks in specialauto:
                Uitvoerfilenaam = os.path.join ( Gewichtendirectory, f'GratisAuto_vk{vks}_{ink}' )
                Routines.csvwegschrijven ( Gewichten, Uitvoerfilenaam )

            ErvarenReistijdfilenaam = os.path.join ( Ervarenreistijddirectory, f'GratisOV' )
            GGRskim = Routines.csvintlezen ( ErvarenReistijdfilenaam )
            GGRskimLen = len(GGRskim)
            print("GGRskim heeft {} regels.".format(GGRskimLen))
            if mot == 'werk':
                constanten = Constantengenerator.alomwerk ( 'OV', 'OV' )
            elif mot == 'winkeldagelijkszorg':
                constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'OV', 'OV' )
            else:
                constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'OV', 'OV' )
            Gewichten = Berekeningen.gewichten( GGRskim, constanten )
            specialOV = ['Neutraal', 'OV']
            for vks in specialOV:
                Uitvoerfilenaam = os.path.join ( Gewichtendirectory, f'GratisOV_vk{vks}_{ink}' )
                Routines.csvwegschrijven ( Gewichten, Uitvoerfilenaam )
