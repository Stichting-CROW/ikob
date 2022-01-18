import Routines
import Berekeningen
import Constantengenerator
from tkinter import filedialog
from tkinter import *
import os

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de hoofddirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'
SEGSdirectory = os.path.join (Skimsdirectory, 'SEGS')

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
hrkomsten = Tk()
hrkomsten.geometry = ("10x10")
hrkomsten.label = ("Voer de directory waar de pure herkomsten in staan")
hrkomsten.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de herkomstendirectory",)
hrkomsten.destroy()
Herkomstendirectory = hrkomsten.directory + '/'
Jaar = input ('Welk jaar gaat het om?')
Scenario = input ('Welk scenario gaat het om?')
Combinatiedirectory = os.path.join ( Skimsdirectory, 'Gewichten', 'Combinaties', Scenario, 'Restdag')
Enkelemodaliteitdirectory = os.path.join ( Skimsdirectory, 'Gewichten', Scenario, 'Restdag')
Naamuitvoer = input ('Geef de naam van de directory waar de uitvoer heen moet')
Concurrentiedirectory = os.path.join (Skimsdirectory, 'Concurrrentie', 'arbeidsplaatsen', Naamuitvoer)
os.makedirs (Concurrentiedirectory, exist_ok=True)
verdeling = Tk()
verdeling.geometry = ("10x10")
verdeling.label = ("Voer de invoerfile in")
verdeling.file = filedialog.askopenfilename(initialdir=os.getcwd(),title="Selecteer de file met de verdeling over de buurten",)
verdeling.destroy()

Groepverdelingfile=verdeling.file
Groepverdelingfile=Groepverdelingfile.replace('.csv','')
Verdelingsmatrix = Routines.csvintlezen(Groepverdelingfile, aantal_lege_regels=1)
Verdelingstransmatrix = Berekeningen.Transponeren (Verdelingsmatrix)
Inkomensverdelingsfilenaam = os.path.join (Skimsdirectory, 'SEGS', 'Inkomensverdeling_per_zone')
Inkomensverdeling = Routines.csvintlezen (Inkomensverdelingsfilenaam, aantal_lege_regels=1)
Inwonersperklassenaam = os.path.join (Skimsdirectory, 'SEGS', f'Inwoners_per_klasse{Jaar}')
Inwonersperklasse = Routines.csvintlezen(Inwonersperklassenaam,aantal_lege_regels=1)
Arbeidsplaatsenfilenaam = os.path.join (SEGSdirectory, f'Arbeidsplaatsen_inkomensklasse{Jaar}')
Arbeidsplaatsen = Routines.csvintlezen(Arbeidsplaatsenfilenaam, aantal_lege_regels=1)


def Lijstvolnullen(lengte=len(Arbeidsplaatsen)) :
    print ('Lengtelijstvolnullen is ', lengte)
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



def bereken_concurrentie (Matrix, Arbeidsplaatsen, Bereik, inkgr):
    Dezegroeplijst = []
    Arbeidsplaatsentrans = Berekeningen.Transponeren ( Arbeidsplaatsen )
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2, Getal3 in zip ( Matrix[i], Bereik, Arbeidsplaatsentrans[inkgroepen.index ( inkgr )] ):
            if Getal2 > 0:
                Gewogenmatrix.append ( Getal1 * Getal3 / Getal2 )
            else :
                Gewogenmatrix.append (0)
        Dezegroeplijst.append ( sum ( Gewogenmatrix ) )
    return Dezegroeplijst


for inkgr in inkgroepen:

    # Eerst de fiets
    print ( 'We zijn het nu aan het uitrekenen voor de inkomensgroep', inkgr )
    for mod in modaliteiten:
        Bijhoudlijst = Lijstvolnullen ( )
        for gr in Groepen:
            print ( 'Bezig met Groep ', gr )
            ink = inkomensgroepbepalen ( gr )
            if inkgr == ink or inkgr == 'alle':
                vk = vindvoorkeur ( gr, mod )
                if mod == 'Fiets' or mod == 'EFiets':
                    if vk == 'Fiets':
                        vkklad = 'Fiets'
                    else:
                        vkklad = ''

                    Fietsfilenaam = os.path.join ( Enkelemodaliteitdirectory, f'{mod}_vk{vkklad}' )
                    Fietsmatrix = Routines.csvintlezen ( Fietsfilenaam )
                    print ( 'Lengte Fietsmatrix is', len ( Fietsmatrix ) )
                    Bereikfilenaam = os.path.join(Herkomstendirectory,f'Totaal_{mod}_{inkgr}')
                    Bereik = Routines.csvintlezen (Bereikfilenaam)
                    Dezegroeplijst = bereken_concurrentie ( Fietsmatrix, Arbeidsplaatsen, Bereik, inkgr)

                    for i in range ( 0, len ( Fietsmatrix ) ):
                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                            Bijhoudlijst[i] += int ( Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/
                                                 (100*(Inkomensverdeling[i][inkgroepen.index(inkgr)])))

                elif mod == 'Auto' or mod == 'OV':
                    String = enkelegroep ( mod, gr )
                    print ( String )
                    Filenaam = os.path.join ( Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}' )
                    Matrix = Routines.csvintlezen ( Filenaam )
                    Bereikfilenaam = os.path.join(Herkomstendirectory,f'Totaal_{mod}_{inkgr}')
                    Bereik = Routines.csvintlezen (Bereikfilenaam)
                    Dezegroeplijst = bereken_concurrentie ( Matrix, Arbeidsplaatsen, Bereik, inkgr)
                    for i in range ( 0, len ( Matrix ) ):
                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                            Bijhoudlijst[i] += int ( Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/
                                                 (100*Inkomensverdeling[i][inkgroepen.index(inkgr)]))
                else:
                    String = combigroep ( mod, gr )
                    print ( String )
                    Filenaam = os.path.join ( Combinatiedirectory, f'{String}_vk{vk}_{ink}' )
                    Matrix = Routines.csvintlezen ( Filenaam )
                    Bereikfilenaam = os.path.join ( Herkomstendirectory, f'Totaal_{mod}_{inkgr}' )
                    Bereik = Routines.csvintlezen ( Bereikfilenaam )
                    Dezegroeplijst = bereken_concurrentie ( Matrix, Arbeidsplaatsen, Bereik, inkgr)
                    for i in range ( 0, len ( Matrix ) ):
                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                            Bijhoudlijst[i] += int ( Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/
                                                 (100*Inkomensverdeling[i][inkgroepen.index(inkgr)]))
        Bijhoudfilenaam = os.path.join ( Concurrentiedirectory, f'Totaal_{mod}_{inkgr}' )
        Routines.csvwegschrijven ( Bijhoudlijst, Bijhoudfilenaam, soort='lijst' )
    # En tot slot alles bij elkaar harken:
    Generaaltotaal_potenties = []
    for mod in modaliteiten:
        Totaalmodfilenaam = os.path.join ( Concurrentiedirectory, f'Totaal_{mod}_{inkgr}' )
        Totaalrij = Routines.csvintlezen ( Totaalmodfilenaam )
        Generaaltotaal_potenties.append ( Totaalrij )
        Generaaltotaaltrans = Berekeningen.Transponeren ( Generaaltotaal_potenties )
        Uitvoerfilenaam = os.path.join ( Concurrentiedirectory, f'Ontpl_conc_{inkgr}' )
        Routines.csvwegschrijvenmetheader ( Generaaltotaaltrans, Uitvoerfilenaam, headstring )
        Routines.xlswegschrijven ( Generaaltotaaltrans, Uitvoerfilenaam, headstringExcel )


header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
for mod in modaliteiten:
    Generaalmatrixproduct = []
    Generaalmatrix = []
    for inkgr in inkgroepen:

        Totaalmodfilenaam = os.path.join (Concurrentiedirectory, f'Totaal_{mod}_{inkgr}')
        Totaalrij = Routines.csvintlezen(Totaalmodfilenaam)
        Generaalmatrix.append(Totaalrij)
        Generaaltotaaltrans = Berekeningen.Transponeren(Generaalmatrix)
    for i in range (len(Inwonersperklasse)):
        Generaalmatrixproduct.append([])
        for j in range (len(Inwonersperklasse[0])):
            if Inwonersperklasse[i][j]>0:
                Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
            else:
                Generaalmatrixproduct[i].append(0)

    Uitvoerfilenaam = os.path.join(Concurrentiedirectory, f'Ontpl_conc_{mod}')
    Uitvoerfilenaamproduct = os.path.join(Concurrentiedirectory, f'Ontpl_concproduct_{mod}')
    Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, header)
    Routines.xlswegschrijven(Generaalmatrixproduct,Uitvoerfilenaamproduct, header)