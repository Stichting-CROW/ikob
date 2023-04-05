import Routines
import Calculations
import Parametergenerator
from tkinter import filedialog
from tkinter import *
import os
from ikobconfig import getConfigFromArgs


config = getConfigFromArgs()
Project_filename = config['__filename__']  # nieuw Carmatisch toegevoegd config item.

project_config = config['project']
paths_config = config['project']['paths']
skims_config = config['skims']
tvom_config = config['TVOM']

scenario = project_config['scenario']
Basedirectory = paths_config['base_directory']
daypart = skims_config['part of the day']
#Scenario = project_config['scenario']
motives = project_config['motives']


# Fixed values
income = ['high', 'middle high', 'middle low', 'low']
preferences = ['Car','Neutral','Bike','Transit']
bikemodalities = ['Bike', 'EBike']


def constantenwork (mod, voorkeur):
    alpha = 0.125
    omega = 45
    weighing = 1
    if mod == 'Bike':
        alpha = 0.225
        omega = 25
    elif mod == 'EBike':
        alpha = 0.175
        omega = 35
    if voorkeur == 'Car':
        if mod == 'Car' :
            omega = 50
        elif mod == 'Transit':
            omega = 30
            weighing = 0.95
    elif voorkeur == 'Transit':
        if mod == 'Car':
            weighing = 0.96
            alpha = 0.125
            omega = 45
        elif mod == 'Transit' :
            alpha = 0.12
            omega = 60
    elif voorkeur == 'Bike':
        if mod == 'Car':
            weighing = 0.75
        elif mod == 'Bike':
            alpha = 0.175
            omega = 35
        elif mod == 'EBike':
            alpha = 0.125
            omega = 55
    return alpha, omega, weighing

def calculateweights (skim, alpha, omega, weighing):
    import math
    print (alpha, omega, weighing)
    Weightsmatrix = []

    for r in range(0, len(skim)):
        Weightsmatrix.append([])
        for k in range(0, len(skim)):
            ervaren_reistijd = skim[r][k]
            if ervaren_reistijd < 180:
                travelvalue = (1 / (1 + math.exp((-omega + ervaren_reistijd)*alpha)))*weighing
            else:
                travelvalue = 0
            if travelvalue < 0.001 :
                travelvalue = 0
            Weightsmatrix[r].append( round(travelvalue,4) )
    return Weightsmatrix

# Avondspits en Ochtendspits eruit verwijderd

for ds in daypart:
    for mot in motives:
        Weightsdirectory = os.path.join ( Basedirectory, 'Weights', ds )
        #Weightsdirectory = os.path.join ( Skimsdirectory, 'Weights', Scenario, ds )
        os.makedirs(Weightsdirectory,exist_ok=True)
        Gen_traveltimedirectory = os.path.join ( Basedirectory, 'Gen_traveltime_', ds)
        #Gen_traveltimedirectory = os.path.join ( Skimsdirectory, 'Gen_traveltime', Scenario, ds )
        for mod in bikemodalities:
            for pref in preferences:
                if pref == 'Car' or pref == 'Bike':
                    Filename = os.path.join(Gen_traveltimedirectory,'Bike')
                    GGRskim = Routines.csvintlezen(Filename, aantal_lege_regels=0)

                    if mot == 'work':
                        constanten = Parametergenerator.alomwork ( mod, pref )
                    elif mot == 'dailyshopping_healthcare':
                        constanten = Parametergenerator.alomdailyshopping_healthcare ( mod, pref )
                    else:
                        constanten = Parametergenerator.alomnondailyshopping_education( mod, pref )
                    alpha = constanten[0]
                    omega = constanten[1]
                    weighing = constanten[2]
                    print ( alpha, omega, weighing )
                    Weights = calculateweights ( GGRskim, alpha, omega, weighing)
                    if pref == 'Car':
                        Outputfilename = os.path.join(Weightsdirectory, f'{mod}_pref')
                    else :
                        Outputfilename = os.path.join(Weightsdirectory, f'{mod}_pref{pref}' )
                    Routines.csvwegschrijven(Weights,Outputfilename)
        # Nu Car
        for inc in income:
            for pref in preferences:
                if mot != 'work':
                    Category = 'other'
                else:
                    Category = 'work'
                Gen_traveltimefilename = os.path.join(Gen_traveltimedirectory, f'Car_{inc}')
                #Gen_traveltimefilename = os.path.join(Gen_traveltimedirectory, f'Car_{Category}_{inc}')
                GGRskim = Routines.csvintlezen(Gen_traveltimefilename)
                if mot == 'work':
                    constanten = Parametergenerator.alomwork ('Car', pref )
                elif mot == 'dailyshopping_healthcare':
                    constanten = Parametergenerator.alomdailyshopping_healthcare ('Car', pref )
                else:
                    constanten = Parametergenerator.alomnondailyshopping_education('Car', pref )
                alpha = constanten[0]
                omega = constanten[1]
                weighing = constanten[2]
                print ( alpha, omega, weighing )
                Weights = calculateweights ( GGRskim, alpha, omega, weighing )
                Outputfilename = os.path.join (Weightsdirectory,f'Car_pref{pref}_{inc}')
                Routines.csvwegschrijven(Weights,Outputfilename)

        CategoryNoCar = ['NoCar', 'NoLicense']
        preferencesNoCar = ['Neutral', 'Transit', 'Bike']
        for sga in CategoryNoCar:
            for pref in preferencesNoCar :
                for inc in income:
                    if mot != 'work':
                        Category = 'other'
                    else:
                        Category = 'work'
                    Gen_traveltimefilename = os.path.join ( Gen_traveltimedirectory, f'{sga}_{inc}' )
                    #Gen_traveltimefilename = os.path.join ( Gen_traveltimedirectory, f'{sga}_{Category}_{inc}' )
                    GGRskim = Routines.csvfloatlezen ( Gen_traveltimefilename )
                    if mot == 'work':
                        constanten = Parametergenerator.alomwork ( 'Car',pref )
                    elif mot == 'dailyshopping_healthcare':
                        constanten = Parametergenerator.alomdailyshopping_healthcare ( 'Car', pref )
                    else:
                        constanten = Parametergenerator.alomnondailyshopping_education( 'Car', pref )
                    alpha = constanten[0]
                    omega = constanten[1]
                    weighing = constanten[2]
                    print ( alpha, omega, weighing )
                    Weights = calculateweights ( GGRskim, alpha, omega, weighing)
                    Outputfilename = os.path.join ( Weightsdirectory, f'{sga}_pref{pref}_{inc}' )
                    Routines.csvwegschrijven ( Weights, Outputfilename )

        # Nu Transit
        modaliteitenTransit = ['Transit']
        for modTransit in modaliteitenTransit:
            for inc in income:
                for pref in preferences:
                    if mot != 'work':
                        Category = 'other'
                    else:
                        Category = 'work'
                    #Gen_traveltimefilename = os.path.join(Gen_traveltimedirectory, f'{modTransit}_{Category}_{inc}')
                    Gen_traveltimefilename = os.path.join ( Gen_traveltimedirectory, f'{modTransit}_{inc}' )
                    GGRskim = Routines.csvintlezen(Gen_traveltimefilename)

                    if mot == 'work':
                        constanten = Parametergenerator.alomwork ( modTransit, pref )
                    elif mot == 'winceldagelijks' or 'onderwijs':
                        constanten = Parametergenerator.alomdailyshopping_healthcare ( modTransit, pref )
                    else:
                        constanten = Parametergenerator.alomnondailyshopping_education( modTransit, pref )
                    alpha = constanten[0]
                    omega = constanten[1]
                    weighing = constanten[2]
                    print ( alpha, omega, weighing )
                    Weights = calculateweights ( GGRskim, alpha, omega, weighing)
                    Outputfilename = os.path.join(Weightsdirectory, f'{modTransit}_pref{pref}_{inc}')
                    Routines.csvwegschrijven(Weights,Outputfilename)

        for inc in income:
            if mot != 'work':
                Category = 'other'
            else:
                Category = 'work'
            #Gen_traveltimefilename = os.path.join ( Gen_traveltimedirectory, f'FreeCar_{Category}_{inc}')
            Gen_traveltimefilename = os.path.join ( Gen_traveltimedirectory, f'FreeCar_{inc}' )
            GGRskim = Routines.csvintlezen ( Gen_traveltimefilename )
            if mot == 'work':
                constanten = Parametergenerator.alomwork ( 'Car', 'Car' )
            elif mot == 'dailyshopping_healthcare':
                constanten = Parametergenerator.alomdailyshopping_healthcare ( 'Car', 'Car' )
            else:
                constanten = Parametergenerator.alomnondailyshopping_education( 'Car', 'Car' )
            alpha = constanten[0]
            omega = constanten[1]
            weighing = constanten[2]
            print ( alpha, omega, weighing )
            Weights = calculateweights ( GGRskim, alpha, omega, weighing )
            specialCar = ['Neutral', 'Car']
            for prefs in specialCar:
                Outputfilename = os.path.join ( Weightsdirectory, f'FreeCar_pref{prefs}_{inc}' )
                Routines.csvwegschrijven ( Weights, Outputfilename )

            Gen_traveltimefilename = os.path.join ( Gen_traveltimedirectory, f'FreeTransit' )
            GGRskim = Routines.csvintlezen ( Gen_traveltimefilename )
            GGRskimLen = len(GGRskim)
            if mot == 'work':
                constanten = Parametergenerator.alomwork ( 'Transit', 'Transit' )
            elif mot == 'dailyshopping_healthcare':
                constanten = Parametergenerator.alomdailyshopping_healthcare ( 'Transit', 'Transit' )
            else:
                constanten = Parametergenerator.alomnondailyshopping_education( 'Transit', 'Transit' )
            alpha = constanten[0]
            omega = constanten[1]
            weighing = constanten[2]
            print ( alpha, omega, weighing )
            Weights = calculateweights ( GGRskim, alpha, omega, weighing )
            specialTransit = ['Neutral', 'Transit']
            for prefs in specialTransit:
                Outputfilename = os.path.join ( Weightsdirectory, f'FreeTransit_pref{prefs}_{inc}' )
                Routines.csvwegschrijven ( Weights, Outputfilename )
