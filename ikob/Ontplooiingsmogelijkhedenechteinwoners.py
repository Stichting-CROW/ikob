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
verdeling_config = config['verdeling']
skims_config = config ['skims']
dagsoort = skims_config['dagsoort']
#ontpl_config = config['ontplooiing']

# Ophalen van instellingen
Basisdirectory = paden_config['skims_directory']
SEGSdirectory = paden_config['segs_directory']
scenario = project_config['scenario']
#Scenario = project_config['scenario']
Grverdelingfile = verdeling_config['uitvoernaam']


Groepen = ['GratisAuto_laag', 'GratisAuto_GratisOV_laag','WelAuto_GratisOV_laag','WelAuto_vkAuto_laag',
           'WelAuto_vkNeutraal_laag', 'WelAuto_vkFiets_laag','WelAuto_vkOV_laag','GeenAuto_GratisOV_laag',
           'GeenAuto_vkNeutraal_laag','GeenAuto_vkFiets_laag', 'GeenAuto_vkOV_laag','GeenRijbewijs_GratisOV_laag',
           'GeenRijbewijs_vkNeutraal_laag', 'GeenRijbewijs_vkFiets_laag', 'GeenRijbewijs_vkOV_laag', 
           'GratisAuto_middellaag', 'GratisAuto_GratisOV_middellaag','WelAuto_GratisOV_middellaag',
           'WelAuto_vkAuto_middellaag','WelAuto_vkNeutraal_middellaag','WelAuto_vkFiets_middellaag',
           'WelAuto_vkOV_middellaag','GeenAuto_GratisOV_middellaag','GeenAuto_vkNeutraal_middellaag',
           'GeenAuto_vkFiets_middellaag', 'GeenAuto_vkOV_middellaag','GeenRijbewijs_GratisOV_middellaag',
           'GeenRijbewijs_vkNeutraal_middellaag','GeenRijbewijs_vkFiets_middellaag', 'GeenRijbewijs_vkOV_middellaag',
           'GratisAuto_middelhoog', 'GratisAuto_GratisOV_middelhoog','WelAuto_GratisOV_middelhoog',
           'WelAuto_vkAuto_middelhoog','WelAuto_vkNeutraal_middelhoog','WelAuto_vkFiets_middelhoog',
           'WelAuto_vkOV_middelhoog','GeenAuto_GratisOV_middelhoog','GeenAuto_vkNeutraal_middelhoog',
           'GeenAuto_vkFiets_middelhoog', 'GeenAuto_vkOV_middelhoog','GeenRijbewijs_GratisOV_middelhoog',
           'GeenRijbewijs_vkNeutraal_middelhoog', 'GeenRijbewijs_vkFiets_middelhoog', 'GeenRijbewijs_vkOV_middelhoog',
           'GratisAuto_hoog', 'GratisAuto_GratisOV_hoog', 'WelAuto_GratisOV_hoog','WelAuto_vkAuto_hoog',
           'WelAuto_vkNeutraal_hoog','WelAuto_vkFiets_hoog','WelAuto_vkOV_hoog','GeenAuto_GratisOV_hoog',
           'GeenAuto_vkNeutraal_hoog','GeenAuto_vkFiets_hoog', 'GeenAuto_vkOV_hoog','GeenRijbewijs_GratisOV_hoog',
           'GeenRijbewijs_vkNeutraal_hoog','GeenRijbewijs_vkFiets_hoog', 'GeenRijbewijs_vkOV_hoog']

modaliteiten = ['Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                  'Auto_OV_Fiets', 'Auto_OV_EFiets']
enkelemodaliteiten = ['Fiets','Efiets', 'Auto', 'OV']
inkgroepen = ['laag', 'middellaag', 'middelhoog', 'hoog']
fiets = ['Fiets','EFiets']
OVauto = ['OV', 'Auto']
voorkeurenfiets = ['', 'Fiets']
headstring = ['Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                  'Auto_OV_Fiets', 'Auto_OV_EFiets']
headstringExcel=['Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                  'Auto_OV_Fiets', 'Auto_OV_EFiets']

Vermenigvuldig = []

Grverdelingfile=Grverdelingfile.replace('.csv','')
Groepverdelingfile=os.path.join(SEGSdirectory,Grverdelingfile)
Verdelingsmatrix = Routines.csvlezen(Groepverdelingfile, aantal_lege_regels=1)
Verdelingstransmatrix = Berekeningen.Transponeren (Verdelingsmatrix)
#Inkomensverdelingsfilenaam = os.path.join (SEGSdirectory, 'Inkomensverdeling_per_zone')
#Inkomensverdeling = Routines.csvintlezen (Inkomensverdelingsfilenaam, aantal_lege_regels=1)
Inwonersperklassenaam = os.path.join (SEGSdirectory, scenario, f'Inwoners_per_klasse')
Inwonersperklasse = Routines.csvintlezen(Inwonersperklassenaam, aantal_lege_regels=1)
Inwonerstotalen = []
for i in range (len(Inwonersperklasse)):
    Inwonerstotalen.append(sum(Inwonersperklasse[i]))
Inkomensverdeling = []
for i in range (len(Inwonersperklasse)):
    Inkomensverdeling.append([])
    for j in range (len(Inwonersperklasse[0])):
        if Inwonerstotalen[i]>0:
            Inkomensverdeling[i].append(Inwonersperklasse[i][j]/Inwonerstotalen[i])
        else:
            Inkomensverdeling[i].append (0)
Inkomenstransverdeling = Berekeningen.Transponeren (Inkomensverdeling)

Arbeidsplaatsenfilenaam = os.path.join (SEGSdirectory, scenario, f'Arbeidsplaatsen_inkomensklasse')
print (Arbeidsplaatsenfilenaam)
Arbeidsplaats = Routines.csvintlezen(Arbeidsplaatsenfilenaam, aantal_lege_regels=1)
Arbeidsplaatsen = Berekeningen.Transponeren(Arbeidsplaats)
print ('Lengte arbeidsplaatsen is', len(Arbeidsplaats))

def Lijstvolnullen(lengte=len(Arbeidsplaats)) :
    Lijst = [] 
    for i in range (lengte) :
        Lijst.append(0)
    return Lijst

def inkomensgroepbepalen(naam):
    if naam[-4:] == 'hoog':
        if naam[-10:] == 'middelhoog':
            return 'middelhoog'
        else:
            return 'hoog'
    elif naam[-4:] == 'laag':
        if naam[-10:] == 'middellaag':
            return 'middellaag'
        else:
            return 'laag'
    else:
        return ''

def vindvoorkeur(naam, mod):
    if 'vk' in naam:
        Beginvk = naam.find ('vk')
        if naam[Beginvk + 2] == "A":
            return 'Auto'
        elif naam[Beginvk + 2] == "N":
            return 'Neutraal'
        elif naam[Beginvk + 2] == "O":
            return 'OV'
        elif naam[Beginvk + 2] == "F":
            return 'Fiets'
        else:
            return ''
    elif 'GratisAuto' in naam:
        if 'GratisAuto_GratisOV' in naam and 'OV' in mod and 'Auto' in mod:
            return 'Neutraal'
        else:
            if 'Auto' in mod:
                return 'Auto'
            else:
                return 'OV'
    elif 'GratisOV' in naam:
        return 'OV'
    else:
        return ''

def enkelegroep(mod, gr) :
    if mod == 'Auto':
        if 'GratisAuto' in gr:
            return 'GratisAuto'
        elif 'Wel' in gr:
            return 'Auto'
        if 'GeenAuto' in gr:
            return 'GeenAuto'
        if 'GeenRijbewijs' in gr:
            return 'GeenRijbewijs'
    if mod == 'OV':
        if 'GratisOV' in gr:
            return 'GratisOV'
        else:
            return 'OV'

def combigroep(mod, gr) :
    string = ''
    if 'Auto' in mod:
        if 'GratisAuto' in gr:
            string = 'GratisAuto'
        elif 'Wel' in gr:
            string = 'Auto'
        if 'GeenAuto' in gr:
            string = 'GeenAuto'
        if 'GeenRijbewijs' in gr:
            string = 'GeenRijbewijs'
    if 'OV' in mod:
        if 'GratisOV' in gr:
            if string == '':
                string = string + 'GratisOV'
            else:
                string = string + '_GratisOV'
        else:
            if string == '':
                string = string + 'OV'
            else:
                string = string + '_OV'
    if 'EFiets' in mod:
        string = string + '_EFiets'
    elif 'Fiets' in mod:
        string = string + '_Fiets'
    return string



def bereken_potenties (Matrix, Arbeidsplaatsen, Inwoners, Inwonersaandeel, inkgr, gr):
    Dezegroeplijst = []
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2 in zip ( Matrix[i], Arbeidsplaatsen[inkgroepen.index ( inkgr )] ):
            Gewogenmatrix.append ( Getal1 * Getal2 * Inwoners[Groepen.index ( gr )][i] )
        if Inwonersaandeel[i]>0:
            Dezegroeplijst.append ( sum ( Gewogenmatrix )/(Inwonersaandeel[i]) )
        else:
            Dezegroeplijst.append ( 0 )
    return Dezegroeplijst

for ds in dagsoort:
    Combinatiedirectory = os.path.join ( Basisdirectory, 'Gewichten', 'Combinaties', ds )
    Enkelemodaliteitdirectory = os.path.join ( Basisdirectory, 'Gewichten', ds )
    Totalendirectorybestemmingen = os.path.join ( Basisdirectory, Projectbestandsnaam, 'Resultaten',
                                                  'Bestemmingen', ds )
    os.makedirs ( Totalendirectorybestemmingen, exist_ok=True )
    print ("De bestemmingen komen in",Totalendirectorybestemmingen)
    # Combinatiedirectory = os.path.join ( Skimsdirectory, 'Gewichten', 'Combinaties', Scenario, 'Restdag')
    # Enkelemodaliteitdirectory = os.path.join ( Skimsdirectory, 'Gewichten', Scenario, 'Restdag')
    # Totalendirectorybestemmingen = os.path.join ( Skimsdirectory, 'Bestemmingen', Scenario, 'Restdag', Naamuitvoer)

    for inkgr in inkgroepen:


        #Eerst de fiets
        print('We zijn het nu aan het uitrekenen voor de inkomensgroep', inkgr)
        for mod in modaliteiten:
            Bijhoudlijst = Lijstvolnullen ()
            for gr in Groepen:
                ink = inkomensgroepbepalen ( gr )
                if inkgr == ink or inkgr == 'alle':
                    vk = vindvoorkeur (gr, mod)
                    if mod == 'Fiets' or mod == 'EFiets':
                        if vk == 'Fiets':
                            vkklad = 'Fiets'
                        else:
                            vkklad = ''

                        Fietsfilenaam = os.path.join (Enkelemodaliteitdirectory, f'{mod}_vk{vkklad}')
                        Fietsmatrix = Routines.csvlezen (Fietsfilenaam)
                        Dezegroeplijst = bereken_potenties (Fietsmatrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                            Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr)
                        for i in range(0, len(Fietsmatrix) ):
                            Bijhoudlijst[i]+= int(Dezegroeplijst[i])
                    elif mod == 'Auto' or mod == 'OV':
                        String = enkelegroep (mod,gr)
                        print (String)
                        AutoOVFilenaam = os.path.join(Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}')
                        print ('Filenaam is', AutoOVFilenaam)
                        Matrix = Routines.csvlezen(AutoOVFilenaam)
                        Dezegroeplijst = bereken_potenties ( Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                             Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr )
                        for i in range(0, len(Matrix) ):
                            Bijhoudlijst[i]+= int(Dezegroeplijst[i])
                    else:
                        String = combigroep (mod,gr)
                        print (String)
                        CombiFilenaam = os.path.join (Combinatiedirectory, f'{String}_vk{vk}_{ink}')
                        print ('Filenaam is', CombiFilenaam)
                        Matrix = Routines.csvlezen ( CombiFilenaam )
                        Dezegroeplijst = bereken_potenties ( Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                             Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr )
                        for i in range ( 0, len ( Matrix ) ):
                            Bijhoudlijst[i] += int ( Dezegroeplijst[i] )
            Bijhoudfilenaam = os.path.join(Totalendirectorybestemmingen, f'Totaal_{mod}_{inkgr}')
            Routines.csvwegschrijven (Bijhoudlijst,Bijhoudfilenaam,soort='lijst')
        # En tot slot alles bij elkaar harken:
        Generaaltotaal_potenties = []
        for mod in modaliteiten :
            Totaalmodfilenaam = os.path.join (Totalendirectorybestemmingen, f'Totaal_{mod}_{inkgr}')
            Totaalrij = Routines.csvintlezen(Totaalmodfilenaam)
            Generaaltotaal_potenties.append(Totaalrij)
        Generaaltotaaltrans = Berekeningen.Transponeren(Generaaltotaal_potenties)
        Uitvoerfilenaam = os.path.join(Totalendirectorybestemmingen, f'Ontpl_totaal_{inkgr}')
        Routines.csvwegschrijvenmetheader(Generaaltotaaltrans, Uitvoerfilenaam, headstring)
        Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, headstringExcel)

    header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
    for mod in modaliteiten:
        Generaalmatrixproduct = []
        Generaalmatrix = []
        for inkgr in inkgroepen:
            Totaalmodfilenaam = os.path.join (Totalendirectorybestemmingen, f'Totaal_{mod}_{inkgr}')
            Totaalrij = Routines.csvintlezen(Totaalmodfilenaam)
            Generaalmatrix.append(Totaalrij)
        Generaaltotaaltrans = Berekeningen.Transponeren(Generaalmatrix)
        for i in range (len(Inwonersperklasse)):
            Generaalmatrixproduct.append([])
            for j in range (len(Inwonersperklasse[0])):
                if Inwonersperklasse[i][j]>0:
                    Generaalmatrixproduct[i].append(int(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                else:
                    Generaalmatrixproduct[i].append(0)

        Uitvoerfilenaam = os.path.join(Totalendirectorybestemmingen, f'Ontpl_totaal_{mod}')
        Uitvoerfilenaamproduct = os.path.join(Totalendirectorybestemmingen, f'Ontpl_totaalproduct_{mod}')
        Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, header)
        Routines.xlswegschrijven(Generaalmatrixproduct,Uitvoerfilenaamproduct, header)