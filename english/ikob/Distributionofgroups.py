import Routines
from tkinter import filedialog
from tkinter import *
import os
from ikobconfig import getConfigFromArgs

# This routine inspects the command line
# of the specified configuration file in a dictionary.
# if there is a problem the program finishes here.
config = getConfigFromArgs()
Project_filename = config['__filename__']  # nieuw carmatisch toegevoegd config item.

# Haal (voor het gemak) onderdelen voor dit script er uit.
project_config = config['project']
paths_config = config['project']['paths']
skims_config = config['skims']
distribution_config = config['distribution']

# Ophalen van instellingen
scenario = project_config['scenario']


# Ophalen van instellingen
SEGSdirectory = paths_config['segs_directory']
scenario = project_config['scenario']
EVpercentage = distribution_config['EV']
Artificial = distribution_config['artificialcarpossession']['use']
Artificialcarpossessionfile = distribution_config['artificialcarpossession']['data-file']
FreeTransitpercentage = distribution_config['Free Transit Forfait share']


# Vaste waarden
incomes = ['low', 'middle low', 'middle high', 'high']

Inhabitantsperincome_classname = os.path.join (SEGSdirectory, scenario, f'Inhabitants_per_income_class')
Inhabitantsperincome_class = Routines.csvintlezen(Inhabitantsperincome_classname, aantal_lege_regels=1)
Inhabitantstotals = []
for i in range (len(Inhabitantsperincome_class)):
    Inhabitantstotals.append(sum(Inhabitantsperincome_class[i]))
Income_distribution = []
for i in range (len(Inhabitantsperincome_class)):
    Income_distribution.append([])
    for j in range (len(Inhabitantsperincome_class[0])):
        if Inhabitantstotals[i]>0:
            Income_distribution[i].append(Inhabitantsperincome_class[i][j]/Inhabitantstotals[i])
        else:
            Income_distribution[i].append (0)
#Income_distributionfilename = os.path.join ( SEGSdirectory, 'Income_distribution_per_zone')
#Income_distribution = Routines.csvintlezen (Income_distributionfilename,aantal_lege_regels=1)
print ('Lengte Income_distributionsdata', len (Income_distribution), len (Income_distribution[0]))
CBScarpossessionfilename = os.path.join ( SEGSdirectory, 'CBS_cars_per_household')
CBScarpossessiondata = Routines.csvintlezen (CBScarpossessionfilename)
#Inhabitants18plusfilename = os.path.join(SEGSdirectory, f'Beroepsbevolking{scenario}')
#print (Inhabitants18plusfilename)
#Inhabitants18plus = Routines.csvintlezen (Inhabitants18plusfilename)
Urbanity_gradefilename = os.path.join ( SEGSdirectory, 'Urbanity_grade')
Urbanity = Routines.csvintlezen (Urbanity_gradefilename)

if EVpercentage == '40':
    Freecartoincomes = [0, 0.17, 0.58, 0.95]
elif EVpercentage == '20' :
    Freecartoincomes = [0, 0.05, 0.25, 0.5]
else :
    Freecartoincomes = [0, 0.02, 0.15, 0.275]

if Artificial:
    Artificialcarpossessionfile = Artificialcarpossessionfile.replace ( '.csv', '' )
    Artificialcarpossession = Routines.csvintlezen ( Artificialcarpossessionfile, aantal_lege_regels=0)


print (Urbanity)
if Artificial:
    Minimumcarpossession = []
    for i in range (0, len(CBScarpossessiondata)):
        Minimumcarpossession.append(min(CBScarpossessiondata[i],Artificialcarpossession[i]))
else:
    Minimumcarpossession = CBScarpossessiondata

NoLicensefilename = os.path.join ( SEGSdirectory, 'NoLicense')
GLicense = Routines.csvintlezen (NoLicensefilename,aantal_lege_regels=1)
NoCarfilename = os.path.join ( SEGSdirectory, 'NoCar')
Gcar = Routines.csvintlezen (NoCarfilename,aantal_lege_regels=1)
Welcarfilename = os.path.join ( SEGSdirectory, 'WelCar')
Wcar = Routines.csvintlezen (Welcarfilename,aantal_lege_regels=1)
Preferencesfilename = os.path.join ( SEGSdirectory, 'Preferences')
Preferences = Routines.csvintlezen (Preferencesfilename,aantal_lege_regels=1)
PreferencesNoCarfilename = os.path.join ( SEGSdirectory, 'PreferencesNoCar')
PreferencesNoCar = Routines.csvintlezen (PreferencesNoCarfilename,aantal_lege_regels=1)

incomes =  ['laag', 'middellaag', 'middelhoog', 'hoog']
ModalityPreferences = ['Car','Neutral', 'Bike', 'Transit']
ModalityPreferencesNoCar = ['Neutral', 'Bike', 'Transit']
categories = ['Freecar', 'Welcar', 'NoCar', 'NoLicense' ]

def Correct (Matrix, Lijst) :
    Matrix2 =[]
    for i in range ( len ( Matrix ) ):
        Matrix2.append([])
        Som = sum(Matrix[i])
        if Som > 0:
            Correctiefactor = Lijst[i] / Som
        else:
            Correctiefactor = 1
        for j in range ( len ( Matrix[0] ) ):
            Correctie = Matrix[i][j]*Correctiefactor
            Matrix2[i].append(round(Correctie,4))
    return Matrix2

print ('de lengte is', len(Income_distribution))


TotalOverview = []
Header = []
Welcar = []
Freecar = []
FreecarenTransit = []
NietFreecar = []
NoCarWelLicense = []
NoLicense = []

for inc in incomes:
    for cat in categories :
        if cat== 'Freecar' :
            Header.append (f'{cat}_{inc}')
            Header.append (f'{cat}_FreeTransit_{inc}')
        elif cat== 'Welcar' :
            Header.append (f'{cat}_FreeTransit_{inc}')
            for pr in Preferences :
                Header.append (f'{cat}_pr{pr}_{inc}')
        else :
            Header.append ( f'{cat}_FreeTransit_{inc}' )
            for prnc in PreferencesNoCar:
                Header.append ( f'{cat}_pr{prnc}_{inc}' )

            # Eerst "theoretosch car- en Licensepossession" vaststellen

for i in range ( len ( Income_distribution ) ):
    Welcar.append([])
    NoCarWelLicense.append([])
    NoLicense.append([])
    TotalOverview.append([])
    carpossessionpercentage = []
    for Getal1,Getal2 in zip (Income_distribution[i], Wcar[Urbanity[i]-1]) :
        carpossessionpercentage.append ( Getal1 * Getal2/100)
    carpossessionpercentages = sum (carpossessionpercentage)

    #Kijken of het werkelijke carpossession lager is:
    if Minimumcarpossession[i] > 0 :
        if Minimumcarpossession[i]/100 < carpossessionpercentages :
            carpossessioncorrectiefactor = (Minimumcarpossession[i]/100) / carpossessionpercentages
            carpossessionpercentages = Minimumcarpossession [i]/100
        else :
            carpossessioncorrectiefactor = 1
    else :
        carpossessioncorrectiefactor = 1

    # Nu carpossession, Licensepossession per income_class bepalen

    for inc in incomes :
        WcarSharetheor = Wcar[Urbanity[i]-1][incomes.index(inc)]/100
        WcarShare = WcarSharetheor * carpossessioncorrectiefactor
        if carpossessioncorrectiefactor!=1 :
            NoCarpossessioncorrectiefactor = (1 - WcarShare)/ (1-WcarSharetheor)
        else:
            NoCarpossessioncorrectiefactor = 1
        Welcar[i].append (WcarShare)
        NoCarverhouding = Gcar[Urbanity[i]-1][incomes.index(inc)]
        NoCarWelLicense[i].append (Gcar[Urbanity[i] - 1][incomes.index(inc)]/100 * NoCarpossessioncorrectiefactor )
        NoLicense[i].append (GLicense[Urbanity[i] - 1][incomes.index(inc)]/100 * NoCarpossessioncorrectiefactor)


    for inc in incomes :
        #Van de car's de Freecar's en Freecar en Transit-bepalen en de rest Transiterhouden
        incomesShare = Income_distribution [i][incomes.index(inc)]
        Freecar = Welcar[i][incomes.index(inc)] * Freecartoincomes [incomes.index(inc)]
        NietFreecar= Welcar[i][incomes.index(inc)] - Freecar
        FreecarShare = Freecar * (1-FreeTransitpercentage) * incomesShare
        TotalOverview[i].append( round(FreecarShare,4)) # Eerst Freecar
        FreecarenTransitShare = Freecar * FreeTransitpercentage * incomesShare
        TotalOverview[i].append( round (FreecarenTransitShare,4)) # Dan FreeTransit
        FreeTransitShare = NietFreecar * FreeTransitpercentage * incomesShare
        TotalOverview[i].append( round (FreeTransitShare,4)) # Welcar, maar FreeTransit
        for pr in ModalityPreferences :
            Sharepref = NietFreecar * (1-FreeTransitpercentage) * Preferences[Urbanity[i] - 1][ModalityPreferences.index ( pr )] / 100
            PreferenceShare = Sharepref * incomesShare
            TotalOverview[i].append ( round (PreferenceShare,4)) # Dan de diverse Preferences
        NoCar = NoCarWelLicense[i][incomes.index(inc)]
        NoCarFreeTransitShare = NoCar * FreeTransitpercentage * incomesShare
        TotalOverview[i].append ( round(NoCarFreeTransitShare,4)) # Free Transit voor Geen car

        for prnc in ModalityPreferencesNoCar:
            Sharepref = NoCar * (1 - FreeTransitpercentage) * PreferencesNoCar[Urbanity[i] - 1][ModalityPreferencesNoCar.index ( prnc )] / 100
            PreferenceShare = Sharepref * incomesShare
            TotalOverview[i].append ( round (PreferenceShare,4)) # Dan de diverse Preferences
        GeenRB = NoLicense[i][incomes.index(inc)]
        GeenRBFreeTransitShare = GeenRB * FreeTransitpercentage * incomesShare
        TotalOverview[i].append ( round(GeenRBFreeTransitShare,4)) # Free Transit voor Geen License
        for prnc in ModalityPreferencesNoCar:
            Sharepref = GeenRB * (1 - FreeTransitpercentage) * PreferencesNoCar[Urbanity[i] - 1][ModalityPreferencesNoCar.index ( prnc )] / 100
            PreferenceShare = Sharepref * incomesShare
            TotalOverview[i].append ( round (PreferenceShare,4)) # Dan de diverse Preferences

TotalOverviewfilename = os.path.join ( SEGSdirectory,scenario, f'Distribution_Over_groups' )
Routines.csvwegschrijvenmetheader ( TotalOverview, TotalOverviewfilename, Header )
Header.insert(0, 'Zone')
Routines.xlswegschrijven ( TotalOverview, TotalOverviewfilename, Header )
