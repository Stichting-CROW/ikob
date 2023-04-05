import Routines
import os
from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.

config = getConfigFromArgs()
Project_filename = config['__filename__']  # nieuw Carmatisch toegevoegd config item.

# Haal (voor het gemak) onderdelen voor dit script er uit.
project_config = config['project']
paths_config = config['project']['paths']
skims_config = config['skims']


# Ophalen van instellingen
scenario = project_config['scenario']
Basedirectory = paths_config['base_directory']
motieven = project_config['motives']
daypart = skims_config['part of the day']
#Scenario = config['project']['scenario']

# Vaste waarden
income = ['high', 'middle high', 'middle low', 'low']
Preferenceen = ['Car', 'Neutral', 'Bike', 'Transit']
Bikemodalities = ['Bike', 'EBike']
CategoryCar = ['Car', 'NoCar', 'NoLicense', 'FreeCar']
CategoryTransit = ['Transit', 'FreeTransit']


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

def Preferencepossible(CategoryCar, CategoryTransit, Preference) :
    if CategoryCar == 'NoCar' or CategoryCar == 'NoLicense':
        if Preference == 'Car':
            return False
        else :
            if CategoryTransit == 'FreeTransit':
                if Preference != 'Transit':
                    return False
                else:
                    return True
            else:
                return True
    elif CategoryCar == 'FreeCar':
        if CategoryTransit == 'FreeTransit':
            if Preference != 'Neutral':
                return False
            else :
                return True
        else:
            if Preference != 'Car' :
                return False
            else :
                return True
    elif CategoryTransit == 'FreeTransit' :
                if Preference != 'Transit':
                    return False
                else :
                    return True
    else :
        return True

def Calculate_max_and_store (Matrix1, Matrix2,mod1, mod2,pr,inc):
    Maxmatrix = minmaxmatrix ( Matrix1, Matrix2 )
    Uitvoerfilenaam = os.path.join (Combinationdirectory, f'{mod1}_{mod2}_pref{pr}_{inc}')
    Routines.csvwegschrijven ( Maxmatrix, Uitvoerfilenaam )
    return

def Calculate_max_and_storeof3 (Matrix1, Matrix2, Matrix3, mod1, mod2, mod3, pr,inc):
    Maxmatrix = minmaxmatrix3 ( Matrix1, Matrix2, Matrix3 )
    Uitvoerfilenaam = os.path.join (Combinationdirectory, f'{mod1}_{mod2}_{mod3}_pref{pr}_{inc}')
    Routines.csvwegschrijven ( Maxmatrix, Uitvoerfilenaam )
    return

for ds in daypart:

    Combinationdirectory = os.path.join(Basedirectory, 'Weights', 'Combinations', ds)
    Singledirectory = os.path.join(Basedirectory, 'Weights', ds)
    #Combinationdirectory = os.path.join ( Skimsdirectory, 'Weights', 'Combinations', Scenario, ds )
    #Singledirectory = os.path.join ( Skimsdirectory, 'Weights', Scenario, ds )
    os.makedirs(Combinationdirectory, exist_ok=True)

    for inc in income:
        for pr in Preferenceen:
            for modft in Bikemodalities:
                for Transitcat in CategoryTransit:
                    if Preferencepossible ('Car', Transitcat, pr):
                        if pr == 'Bike':
                            prklad = 'Bike'
                        else:
                            prklad = ''
                        Bikefile = os.path.join (Singledirectory, f'{modft}_pref{prklad}')
                        Bikematrix = Routines.csvlezen(Bikefile)
                        Transitfile = os.path.join (Singledirectory, f'{Transitcat}_pref{pr}_{inc}')
                        Transitmatrix = Routines.csvlezen(Transitfile)
                        Calculate_max_and_store(Bikematrix,Transitmatrix, Transitcat, modft, pr, inc)

                for Carcat in CategoryCar:
                    if Preferencepossible (Carcat, 'Transit', pr):
                        if pr == 'Bike':
                            prklad = 'Bike'
                        else:
                            prklad = ''
                        Bikefile = os.path.join ( Singledirectory, f'{modft}_pref{prklad}' )
                        Bikematrix = Routines.csvlezen ( Bikefile )
                        Carfile = os.path.join ( Singledirectory, f'{Carcat}_pref{pr}_{inc}' )
                        Carmatrix = Routines.csvlezen ( Carfile )
                        Calculate_max_and_store ( Bikematrix, Carmatrix, Carcat, modft, pr, inc )

            for Transitcat in CategoryTransit:
                for Carcat in CategoryCar:
                    if Preferencepossible (Carcat, Transitcat, pr):
                        Transitfile = os.path.join ( Singledirectory, f'{Transitcat}_pref{pr}_{inc}' )
                        Transitmatrix = Routines.csvlezen ( Transitfile )
                        Carfile = os.path.join ( Singledirectory, f'{Carcat}_pref{pr}_{inc}' )
                        Carmatrix = Routines.csvlezen ( Carfile )
                        Calculate_max_and_store ( Transitmatrix, Carmatrix, Carcat, Transitcat, pr, inc )

            for modft in Bikemodalities:
                for Transitcat in CategoryTransit:
                    for Carcat in CategoryCar:
                        if Preferencepossible (Carcat, Transitcat, pr):
                            if pr == 'Bike':
                                prklad = 'Bike'
                            else:
                                prklad = ''
                            Bikefile = os.path.join (Singledirectory, f'{modft}_pref{prklad}')
                            Bikematrix = Routines.csvlezen(Bikefile)
                            Transitfile = os.path.join (Singledirectory, f'{Transitcat}_pref{pr}_{inc}')
                            Transitmatrix = Routines.csvlezen(Transitfile)
                            Carfile = os.path.join ( Singledirectory, f'{Carcat}_pref{pr}_{inc}' )
                            Carmatrix = Routines.csvlezen ( Carfile )
                            Calculate_max_and_storeof3(Carmatrix, Bikematrix, Transitmatrix, Carcat, Transitcat, modft, pr, inc)
