import Routines
import Calculations
import os
from ikobconfig import getConfigFromArgs


config = getConfigFromArgs()
Projectbestandsname = config['__filename__']  # new automatically added config item.
project_config=config['project']
paths_config = config['project']['paths']
skims_config = config['skims']
daypart = skims_config['part of the day']
distrinution_config = config['distribution']


# Get the values from the .json file
Basisdirectory = paths_config['base_directory']
SEGSdirectory = paths_config['segs_directory']
scenario = project_config['scenario']

# Fixed values
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
IncomeGroups = ['low', 'middle low', 'middle high', 'high']
Bike = ['Bike','EBike']
TransitCar = ['Transit', 'Car']
preferencesBike = ['', 'Bike']
headstring = ['Bike', 'EBike', 'Car', 'Transit', 'Car_Bike', 'Transit_Bike', 'Car_EBike', 'Transit_EBike', 'Car_Transit',
                  'Car_Transit_Bike', 'Car_Transit_EBike']
headstringExcel=['Zone', 'Bike', 'EBike', 'Car', 'Transit', 'Car_Bike', 'Transit_Bike', 'Car_EBike', 'Transit_EBike', 'Car_Transit',
                  'Car_Transit_Bike', 'Car_Transit_EBike']
Groupdistributionfile=os.path.join(SEGSdirectory, scenario, f'Distribution_Over_groups')
Distributionmatrix = Routines.csvlezen(Groupdistributionfile, aantal_lege_regels=1)
Distributiontransmatrix = Calculations.Transponeren (Distributionmatrix)
Inhabitants_per_Income_classname = os.path.join (SEGSdirectory, scenario, f'Inhabitants_per_Income_class')
Inhabitants_per_Income_class = Routines.csvintlezen(Inhabitants_per_Income_classname, aantal_lege_regels=1)
InhabitantsTotals = []
for i in range (len(Inhabitants_per_Income_class)):
    InhabitantsTotals.append(sum(Inhabitants_per_Income_class[i]))
print ('Length inhabitantsfile is', len(InhabitantsTotals))
LaborPlacesfilenaam = os.path.join (SEGSdirectory, scenario, f'Jobs_income_class')
LaborPlacesperclass = Routines.csvintlezen(LaborPlacesfilenaam, aantal_lege_regels=1)

def listofzeros(length=len(InhabitantsTotals)) :
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


def calculate_laborforce (Distributionmatrix, InhabitantsTotals):
    Inhabitantsfile = []
    for i in range (len(InhabitantsTotals)) :
        Inhabitantsfile.append([])
        for j in range (len(Distributionmatrix[0])) :
            Inhabitantsfile[i].append(round(InhabitantsTotals[i]*Distributionmatrix[i][j]))
    return Inhabitantsfile

def calculate_potencies (Matrix, Inhabitantstrans, gr):
    ThisGrouplist = []
    for i in range ( len ( Matrix ) ):
        Weightedmatrix = []
        for Getal1, Getal2 in zip ( Matrix[i], Inhabitantstrans[Groups.index ( gr )] ):
            Weightedmatrix.append ( Getal1 * Getal2 )
        ThisGrouplist.append ( sum ( Weightedmatrix ) )
    return ThisGrouplist

Inhabitants = calculate_laborforce (Distributionmatrix, InhabitantsTotals)
Inhabitantstransmatrix = Calculations.Transponeren(Inhabitants)

for ds in daypart:
    Combinationdirectory = os.path.join ( Basisdirectory, 'Weights', 'Combinations', ds )
    Singlemodalitydirectory = os.path.join ( Basisdirectory,  'Weights', ds )
    TotalsdirectoryOrigins = os.path.join ( Basisdirectory, Projectbestandsname, 'Results', 'Origins', ds )

    os.makedirs ( TotalsdirectoryOrigins, exist_ok=True )

    for incgr in IncomeGroups:
        #Eerst de Bike
        print('Calculations take place for Income Group IncomesGroup', incgr)
        for mod in modalities:
            KeepTracklist = listofzeros ()
            for gr in Groups:
                inc = DefineIncomeGroup ( gr )
                if incgr == inc or incgr == 'alle':
                    pref = findpreference (gr, mod)
                    if mod == 'Bike' or mod == 'EBike':
                        if pref == 'Bike':
                            prefdraft = 'Bike'
                        else:
                            prefdraft = ''

                        Bikefilename = os.path.join (Singlemodalitydirectory, f'{mod}_pref{prefdraft}')
                        Bikematrix = Routines.csvlezen (Bikefilename)
                        ThisGrouplist = calculate_potencies (Bikematrix, Inhabitantstransmatrix, gr)

                        for i in range(0, len(Bikematrix) ):
                            KeepTracklist[i]+= round(ThisGrouplist[i])
                    elif mod == 'Car' or mod == 'Transit':
                        String = singleGroup (mod,gr)
                        print (String)
                        Filename = os.path.join(Singlemodalitydirectory, f'{String}_pref{pref}_{inc}')
                        Matrix = Routines.csvlezen(Filename)
                        ThisGrouplist = calculate_potencies ( Matrix, Inhabitantstransmatrix, gr )
                        for i in range(0, len(Matrix) ):
                            KeepTracklist[i]+= round(ThisGrouplist[i])
                    else:
                        String = combiGroup (mod,gr)
                        print (String)
                        Filename = os.path.join (Combinationdirectory, f'{String}_pref{pref}_{inc}')
                        Matrix = Routines.csvlezen ( Filename )
                        ThisGrouplist = calculate_potencies ( Matrix, Inhabitantstransmatrix, gr )
                        for i in range ( 0, len ( Matrix ) ):
                            KeepTracklist[i] += round ( ThisGrouplist[i])
            KeepTrackfilename = os.path.join(TotalsdirectoryOrigins, f'Total_{mod}_{incgr}')
            Routines.csvwegschrijven (KeepTracklist,KeepTrackfilename,soort='list')
        # En tot slot alles bij elkaar harken:
        GeneralTotal_potenties = []
        for mod in modalities :
            Totalmodfilename = os.path.join (TotalsdirectoryOrigins, f'Total_{mod}_{incgr}')
            Totalrij = Routines.csvintlezen(Totalmodfilename)
            GeneralTotal_potenties.append(Totalrij)
        GeneralTotaltrans = Calculations.Transponeren(GeneralTotal_potenties)
        Outputfilename = os.path.join(TotalsdirectoryOrigins, f'Pot_Total_{incgr}')
        Routines.csvwegschrijvenmetheader(GeneralTotaltrans, Outputfilename, headstring)
        Routines.xlswegschrijven(GeneralTotaltrans, Outputfilename, headstringExcel)

    header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
    for mod in modalities:
        Generalmatrixproduct = []
        Generalmatrix = []
        for incgr in IncomeGroups:

            Totalmodfilename = os.path.join (TotalsdirectoryOrigins, f'Total_{mod}_{incgr}')
            Totalrij = Routines.csvintlezen(Totalmodfilename)
            Generalmatrix.append(Totalrij)
        GeneralTotaltrans = Calculations.Transponeren(Generalmatrix)
        for i in range (len(LaborPlacesperclass)):
            Generalmatrixproduct.append([])
            for j in range (len(LaborPlacesperclass[0])):
                if LaborPlacesperclass[i][j]>0:
                    Generalmatrixproduct[i].append(int(GeneralTotaltrans[i][j]*LaborPlacesperclass[i][j]))
                else:
                    Generalmatrixproduct[i].append(0)

        Outputfilename = os.path.join(TotalsdirectoryOrigins, f'Pot_Total_{mod}')
        Outputfilenameproduct = os.path.join(TotalsdirectoryOrigins, f'Pot_Totalproduct_{mod}')
        Routines.xlswegschrijven(GeneralTotaltrans, Outputfilename, header)
        Routines.xlswegschrijven(Generalmatrixproduct,Outputfilenameproduct, header)