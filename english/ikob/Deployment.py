import Routines
import Calculations
import Parametergenerator
from tkinter import filedialog
from tkinter import *
import os
from ikobconfig import getConfigFromArgs

# This routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()
Project_filename = config['__filename__']  # nieuw Carmatisch toegevoegd config item.
project_config = config['project']
paths_config = config['project']['paths']
distribution_config = config['distribution']
skims_config = config ['skims']
daypart = skims_config['part of the day']
#Depl_config = config['Deplooiing']

# Ophalen van instellingen
Basedirectory = paths_config['base_directory']
SEGSdirectory = paths_config['segs_directory']
scenario = project_config['scenario']
#Scenario = project_config['scenario']



Groups = ['FreeCar_low', 'FreeCar_FreeTransit_low','WelCar_FreeTransit_low','WelCar_prefCar_low',
           'WelCar_prefNeutral_low', 'WelCar_prefBike_low','WelCar_prefTransit_low','NoCar_FreeTransit_low',
           'NoCar_prefNeutral_low','NoCar_prefBike_low', 'NoCar_prefTransit_low','NoLicense_FreeTransit_low',
           'NoLicense_prefNeutral_low', 'NoLicense_prefBike_low', 'NoLicense_prefTransit_low', 
           'FreeCar_middle low', 'FreeCar_FreeTransit_middle low','WelCar_FreeTransit_middle low',
           'WelCar_prefCar_middle low','WelCar_prefNeutral_middle low','WelCar_prefBike_middle low',
           'WelCar_prefTransit_middle low','NoCar_FreeTransit_middle low','NoCar_prefNeutral_middle low',
           'NoCar_prefBike_middle low', 'NoCar_prefTransit_middle low','NoLicense_FreeTransit_middle low',
           'NoLicense_prefNeutral_middle low','NoLicense_prefBike_middle low', 'NoLicense_prefTransit_middle low',
           'FreeCar_middle high', 'FreeCar_FreeTransit_middle high','WelCar_FreeTransit_middle high',
           'WelCar_prefCar_middle high','WelCar_prefNeutral_middle high','WelCar_prefBike_middle high',
           'WelCar_prefTransit_middle high','NoCar_FreeTransit_middle high','NoCar_prefNeutral_middle high',
           'NoCar_prefBike_middle high', 'NoCar_prefTransit_middle high','NoLicense_FreeTransit_middle high',
           'NoLicense_prefNeutral_middle high', 'NoLicense_prefBike_middle high', 'NoLicense_prefTransit_middle high',
           'FreeCar_high', 'FreeCar_FreeTransit_high', 'WelCar_FreeTransit_high','WelCar_prefCar_high',
           'WelCar_prefNeutral_high','WelCar_prefBike_high','WelCar_prefTransit_high','NoCar_FreeTransit_high',
           'NoCar_prefNeutral_high','NoCar_prefBike_high', 'NoCar_prefTransit_high','NoLicense_FreeTransit_high',
           'NoLicense_prefNeutral_high','NoLicense_prefBike_high', 'NoLicense_prefTransit_high']

modalities = ['Bike', 'EBike', 'Car', 'Transit', 'Car_Bike', 'Transit_Bike', 'Car_EBike', 'Transit_EBike', 'Car_Transit',
                  'Car_Transit_Bike', 'Car_Transit_EBike']
singlemodalities = ['Bike','EBike', 'Car', 'Transit']
incGroups = ['low', 'middle low', 'middle high', 'high']
Bike = ['Bike','EBike']
TransitCar = ['Transit', 'Car']
preferencesBike = ['', 'Bike']
headstring = ['Bike', 'EBike', 'Car', 'Transit', 'Car_Bike', 'Transit_Bike', 'Car_EBike', 'Transit_EBike', 'Car_Transit',
                  'Car_Transit_Bike', 'Car_Transit_EBike']
headstringExcel=['Zone', 'Bike', 'EBike', 'Car', 'Transit', 'Car_Bike', 'Transit_Bike', 'Car_EBike', 'Transit_EBike', 'Car_Transit',
                  'Car_Transit_Bike', 'Car_Transit_EBike']


Groupdistributionfile=os.path.join(SEGSdirectory,scenario, f'Distribution_Over_groups')
Distributionmatrix = Routines.csvlezen(Groupdistributionfile, aantal_lege_regels=1)
Distributiontransmatrix = Calculations.Transponeren (Distributionmatrix)

Inhabitants_per_income_classname = os.path.join (SEGSdirectory, scenario, f'Inhabitants_per_income_class')
Inhabitants_per_income_class = Routines.csvintlezen(Inhabitants_per_income_classname, aantal_lege_regels=1)
InhabitantsTotals = []
for i in range (len(Inhabitants_per_income_class)):
    InhabitantsTotals.append(sum(Inhabitants_per_income_class[i]))
Incomesdistribution = []
for i in range (len(Inhabitants_per_income_class)):
    Incomesdistribution.append([])
    for j in range (len(Inhabitants_per_income_class[0])):
        if InhabitantsTotals[i]>0:
            Incomesdistribution[i].append(Inhabitants_per_income_class[i][j]/InhabitantsTotals[i])
        else:
            Incomesdistribution[i].append (0)
incomestransdistribution = Calculations.Transponeren (Incomesdistribution)

Jobsfilename = os.path.join (SEGSdirectory, scenario, f'Jobs_income_class')
print (Jobsfilename)
LaborPlaces = Routines.csvintlezen(Jobsfilename, aantal_lege_regels=1)
LaborPlacestrans = Calculations.Transponeren(LaborPlaces)
print ('length Laborplaces is', len(LaborPlaces))

def listofzeros(length=len(LaborPlaces)) :
    list = [] 
    for i in range (length) :
        list.append(0)
    return list

def DefineIncomeGroup(name):
    if name[-4:] == 'high':
        if name[-11:] == 'middle high':
            return 'middle high'
        else:
            return 'high'
    elif name[-3:] == 'low':
        if name[-10:] == 'middle low':
            return 'middle low'
        else:
            return 'low'
    else:
        return ''

def findpreference(name, mod):
    if 'pref' in name:
        Beginpref = name.find ('pref')
        if name[Beginpref + 4] == "C":
            return 'Car'
        elif name[Beginpref + 4] == "N":
            return 'Neutral'
        elif name[Beginpref + 4] == "T":
            return 'Transit'
        elif name[Beginpref + 4] == "B":
            return 'Bike'
        else:
            return ''
    elif 'FreeCar' in name:
        if 'FreeCar_FreeTransit' in name and 'Transit' in mod and 'Car' in mod:
            return 'Neutral'
        else:
            if 'Car' in mod:
                return 'Car'
            else:
                return 'Transit'
    elif 'FreeTransit' in name:
        return 'Transit'
    else:
        return ''

def singleGroup(mod, gr) :
    if mod == 'Car':
        if 'FreeCar' in gr:
            return 'FreeCar'
        elif 'Wel' in gr:
            return 'Car'
        if 'NoCar' in gr:
            return 'NoCar'
        if 'NoLicense' in gr:
            return 'NoLicense'
    if mod == 'Transit':
        if 'FreeTransit' in gr:
            return 'FreeTransit'
        else:
            return 'Transit'

def combiGroup(mod, gr) :
    string = ''
    if 'Car' in mod:
        if 'FreeCar' in gr:
            string = 'FreeCar'
        elif 'Wel' in gr:
            string = 'Car'
        if 'NoCar' in gr:
            string = 'NoCar'
        if 'NoLicense' in gr:
            string = 'NoLicense'
    if 'Transit' in mod:
        if 'FreeTransit' in gr:
            if string == '':
                string = string + 'FreeTransit'
            else:
                string = string + '_FreeTransit'
        else:
            if string == '':
                string = string + 'Transit'
            else:
                string = string + '_Transit'
    if 'EBike' in mod:
        string = string + '_EBike'
    elif 'Bike' in mod:
        string = string + '_Bike'
    return string



def calculate_potentials (Matrix, Jobs, Inhabitants, Inhabitantsshare, incgr, gr):
    ThisGrouplist = []
    for i in range ( len ( Matrix ) ):
        Weightedmatrix = []
        for Getal1, Getal2 in zip ( Matrix[i], Jobs[incGroups.index ( incgr )] ):
            Weightedmatrix.append ( Getal1 * Getal2 * Inhabitants[Groups.index ( gr )][i] )
        if Inhabitantsshare[i]>0:
            ThisGrouplist.append ( sum ( Weightedmatrix )/(Inhabitantsshare[i]) )
        else:
            ThisGrouplist.append ( 0 )
    return ThisGrouplist

for ds in daypart:
    Combinationdirectory = os.path.join ( Basedirectory, 'Weights', 'Combinations', ds )
    Singlemodalitydirectory = os.path.join ( Basedirectory, 'Weights', ds )
    TotalsdirectoryDestinationss = os.path.join ( Basedirectory, Project_filename, 'Results',
                                                  'Destinationss', ds )
    os.makedirs ( TotalsdirectoryDestinationss, exist_ok=True )
    print ("File with number of possible Laborplaces (Destinationss) are in file",TotalsdirectoryDestinationss)

    for incgr in incGroups:
        for mod in modalities:
            KeepTracklist = listofzeros ()
            for gr in Groups:
                inc = DefineIncomeGroup ( gr )
                if incgr == inc or incgr == 'alle':
                    pref = findpreference (gr, mod)
                    if mod == 'Bike' or mod == 'EBike':
                        if pref == 'Bike':
                            prefklad = 'Bike'
                        else:
                            prefklad = ''

                        Bikefilename = os.path.join (Singlemodalitydirectory, f'{mod}_pref{prefklad}')
                        Bikematrix = Routines.csvlezen (Bikefilename)
                        ThisGrouplist = calculate_potentials (Bikematrix, LaborPlacestrans, Distributiontransmatrix,
                                                            incomestransdistribution[incGroups.index(incgr)], incgr, gr)
                        for i in range(0, len(Bikematrix) ):
                            KeepTracklist[i]+= int(ThisGrouplist[i])
                    elif mod == 'Car' or mod == 'Transit':
                        String = singleGroup (mod,gr)
                        print (String)
                        CarTransitFilename = os.path.join(Singlemodalitydirectory, f'{String}_pref{pref}_{inc}')
                        print ('Filename is', CarTransitFilename)
                        Matrix = Routines.csvlezen(CarTransitFilename)
                        ThisGrouplist = calculate_potentials ( Matrix, LaborPlacestrans, Distributiontransmatrix,
                                                             incomestransdistribution[incGroups.index(incgr)], incgr, gr )
                        for i in range(0, len(Matrix) ):
                            KeepTracklist[i]+= int(ThisGrouplist[i])
                    else:
                        String = combiGroup (mod,gr)
                        print (String)
                        CombiFilename = os.path.join (Combinationdirectory, f'{String}_pref{pref}_{inc}')
                        print ('Filename is', CombiFilename)
                        Matrix = Routines.csvlezen ( CombiFilename )
                        ThisGrouplist = calculate_potentials ( Matrix, LaborPlacestrans, Distributiontransmatrix,
                                                             incomestransdistribution[incGroups.index(incgr)], incgr, gr )
                        for i in range ( 0, len ( Matrix ) ):
                            KeepTracklist[i] += int ( ThisGrouplist[i] )
            KeepTrackfilename = os.path.join(TotalsdirectoryDestinationss, f'total_{mod}_{incgr}')
            Routines.csvwegschrijven (KeepTracklist,KeepTrackfilename,soort='list')
        # En tot slot alles bij elkaar harken:
        Generaltotal_potentials = []
        for mod in modalities :
            totalmodfilename = os.path.join (TotalsdirectoryDestinationss, f'total_{mod}_{incgr}')
            totalrow = Routines.csvintlezen(totalmodfilename)
            Generaltotal_potentials.append(totalrow)
        Generaltotaltrans = Calculations.Transponeren(Generaltotal_potentials)
        Outputfilename = os.path.join(TotalsdirectoryDestinationss, f'Depl_total_{incgr}')
        Routines.csvwegschrijvenmetheader(Generaltotaltrans, Outputfilename, headstring)
        Routines.xlswegschrijven(Generaltotaltrans, Outputfilename, headstringExcel)

    header = ['Zone', 'low', 'middle low','middle high', 'high']
    for mod in modalities:
        Generalmatrixproduct = []
        Generalmatrix = []
        for incgr in incGroups:
            totalmodfilename = os.path.join (TotalsdirectoryDestinationss, f'total_{mod}_{incgr}')
            totalrow = Routines.csvintlezen(totalmodfilename)
            Generalmatrix.append(totalrow)
        Generaltotaltrans = Calculations.Transponeren(Generalmatrix)
        for i in range (len(Inhabitants_per_income_class)):
            Generalmatrixproduct.append([])
            for j in range (len(Inhabitants_per_income_class[0])):
                if Inhabitants_per_income_class[i][j]>0:
                    Generalmatrixproduct[i].append(int(Generaltotaltrans[i][j]*Inhabitants_per_income_class[i][j]))
                else:
                    Generalmatrixproduct[i].append(0)

        Outputfilename = os.path.join(TotalsdirectoryDestinationss, f'Depl_total_{mod}')
        Outputfilenameproduct = os.path.join(TotalsdirectoryDestinationss, f'Depl_totalproduct_{mod}')
        Routines.xlswegschrijven(Generaltotaltrans, Outputfilename, header)
        Routines.xlswegschrijven(Generalmatrixproduct,Outputfilenameproduct, header)