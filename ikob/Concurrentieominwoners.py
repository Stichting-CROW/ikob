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
#verdeling_config = config['verdeling']
skims_config = config ['skims']
dagsoort = skims_config['dagsoort']

# Ophalen van instellingen
Basisdirectory = paden_config['skims_directory']
Skimsdirectory = os.path.join (Basisdirectory, 'skims')
SEGSdirectory = paden_config['segs_directory']
scenario = project_config['verstedelijkingsscenario']
regime = project_config['beprijzingsregime']
motieven = project_config ['motieven']
autobezitgroepen = project_config ['welke_groepen']
conc_afstand = project_config ['conc_afstand']
#Naamuitvoer = conc_config['uitvoer_directory_naam']
#Grverdelingfile = verdeling_config['uitvoernaam']


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
headstringkort = ['Auto', 'Auto_OV', 'Auto_OV_Fiets']
headstringkortExcel = ['Zone','Auto', 'Auto_OV', 'Auto_OV_Fiets']

#Grverdelingfile=Grverdelingfile.replace('.csv','')

#Inkomensverdelingsfilenaam = os.path.join (SEGSdirectory, 'Inkomensverdeling_per_zone')
#Inkomensverdeling = Routines.csvintlezen (Inkomensverdelingsfilenaam, aantal_lege_regels=1)

Inwonersperklassenaam = os.path.join (SEGSdirectory, scenario, f'Inwoners_inkomensklasse')
Inwonersperklasse = Routines.csvintlezen(Inwonersperklassenaam, aantal_lege_regels=1)
Inwonerstotalen = []

Beroepsbevolkingperklassenaam = os.path.join (SEGSdirectory, scenario, f'Beroepsbevolking_inkomensklasse')
Beroepsbevolkingperklasse = Routines.csvintlezen(Beroepsbevolkingperklassenaam, aantal_lege_regels=1)
Beroepsbevolkingtotalen = []

for i in range (len(Inwonersperklasse)):
    Inwonerstotalen.append(sum(Inwonersperklasse[i]))
for i in range(len(Beroepsbevolkingperklasse)):
    Beroepsbevolkingtotalen.append(sum(Beroepsbevolkingperklasse[i]))

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



def bereken_concurrentie (Matrix, Inwoners, Bereik, inkgr):
    Dezegroeplijst = []
    Inwonerstrans = Berekeningen.Transponeren ( Inwoners )
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2, Getal3 in zip ( Matrix[i], Bereik, Inwonerstrans[inkgroepen.index ( inkgr )] ):
            if Getal2 > 0:
                Gewogenmatrix.append ( Getal1 * Getal3 / Getal2 )
            else :
                Gewogenmatrix.append (0)
        Dezegroeplijst.append ( sum ( Gewogenmatrix ) )
    return Dezegroeplijst

def bereken_afstanden_werk (Matrix, Bestemmingen, Afstanden, Bereik, inkgr):
    Dezegroeplijst = []
    Bestemmingentrans = Berekeningen.Transponeren ( Bestemmingen )
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        Noemer = []
        for Getal1, Getal2, Getal3 in zip ( Matrix[i], Afstanden[i], Bestemmingentrans[inkgroepen.index ( inkgr )] ):
            Gewogenmatrix.append ( Getal1 * Getal2 * Getal3 )
            Noemer.append (Getal1*Getal3)
        if sum(Noemer)> 0:
            Dezegroeplijst.append ( sum ( Gewogenmatrix ) / sum (Noemer))
        else:
            Dezegroeplijst.append (0)
    return Dezegroeplijst

def bereken_afstanden_nietwerk (Matrix, Bestemmingentotaal, Afstanden, Bereik, inkgr):
    Dezegroeplijst = []
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        Noemer = []
        for Getal1, Getal2, Getal3 in zip ( Matrix[i], Afstanden[i], Bestemmingentotaal ):
            Gewogenmatrix.append ( Getal1 * Getal2 * Getal3 )
            Noemer.append (Getal1*Getal3)
        if sum(Noemer) > 0:
            Dezegroeplijst.append ( sum ( Gewogenmatrix ) / sum (Noemer))
        else:
            Dezegroeplijst.append (0)
    return Dezegroeplijst

for ca in conc_afstand:
    if ca == 'Concurrentie':
        for abg in autobezitgroepen:
            if abg == 'alle groepen':
                Groepverdelingfile = os.path.join(SEGSdirectory, scenario, f'Verdeling_over_groepen')
            else:
                Groepverdelingfile = os.path.join(SEGSdirectory, scenario, f'Verdeling_over_groepen_alleen_autobezit')
            Verdelingsmatrix = Routines.csvlezen(Groepverdelingfile, aantal_lege_regels=1)
            Verdelingstransmatrix = Berekeningen.Transponeren(Verdelingsmatrix)
            for mot in motieven:
                if mot == 'werk':
                    Bestemmingen = Arbeidsplaatsen
                else:
                    Bestemmingen = Inwonersperklasse

                for ds in dagsoort:
                    Afstandenfile = os.path.join(Skimsdirectory, ds, 'Auto_Afstandhm')
                    Afstanden = Routines.csvintlezen (Afstandenfile)
                    Combinatiedirectory = os.path.join ( Basisdirectory, regime,  'Gewichten', 'Combinaties', ds)
                    Enkelemodaliteitdirectory = os.path.join ( Basisdirectory, regime, 'Gewichten', ds)
                    Concurrentiedirectory = os.path.join (Basisdirectory, Projectbestandsnaam, 'Resultaten', mot, abg,
                                                          'Concurrentie', 'inwoners', ds)

                    Bestemmingendirectory = os.path.join ( Basisdirectory, Projectbestandsnaam, 'Resultaten', mot, abg,
                                                                  'Bestemmingen', ds )
                    os.makedirs (Concurrentiedirectory, exist_ok=True)
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
                                        Fietsmatrix = Routines.csvlezen ( Fietsfilenaam )
                                        print ( 'Lengte Fietsmatrix is', len ( Fietsmatrix ) )
                                        Bereikfilenaam = os.path.join(Bestemmingendirectory,f'Totaal_{mod}_{inkgr}')
                                        Bereik = Routines.csvintlezen (Bereikfilenaam)
                                        Dezegroeplijst = bereken_concurrentie ( Fietsmatrix, Inwonersperklasse, Bereik, inkgr)

                                        for i in range ( 0, len ( Fietsmatrix ) ):
                                            if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                                Bijhoudlijst[i] += Dezegroeplijst[i]

                                    elif mod == 'Auto' or mod == 'OV':
                                        String = enkelegroep(mod, gr)
                                        print ( String )
                                        Filenaam = os.path.join ( Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}' )
                                        Matrix = Routines.csvlezen ( Filenaam )
                                        Bereikfilenaam = os.path.join(Bestemmingendirectory,f'Totaal_{mod}_{inkgr}')
                                        Bereik = Routines.csvintlezen (Bereikfilenaam)
                                        Dezegroeplijst = bereken_concurrentie ( Matrix, Inwonersperklasse, Bereik, inkgr)
                                        for i in range ( 0, len ( Matrix ) ):
                                            if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                                Bijhoudlijst[i] += Dezegroeplijst[i]
                                    else:
                                        String = combigroep ( mod, gr )
                                        print ( String )
                                        Filenaam = os.path.join ( Combinatiedirectory, f'{String}_vk{vk}_{ink}' )
                                        Matrix = Routines.csvlezen ( Filenaam )
                                        Bereikfilenaam = os.path.join ( Bestemmingendirectory, f'Totaal_{mod}_{inkgr}' )
                                        Bereik = Routines.csvintlezen ( Bereikfilenaam )
                                        Dezegroeplijst = bereken_concurrentie ( Matrix, Inwonersperklasse, Bereik, inkgr)
                                        for i in range ( 0, len ( Matrix ) ):
                                            if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                                Bijhoudlijst[i] += Dezegroeplijst[i]
                                Bijhoudfilenaam = os.path.join ( Concurrentiedirectory, f'Totaal_{mod}_{inkgr}' )
                                Routines.csvwegschrijven ( Bijhoudlijst, Bijhoudfilenaam, soort='lijst' )
                        # En tot slot alles bij elkaar harken:
                        Generaaltotaal_potenties = []
                        for mod in modaliteiten:
                            Totaalmodfilenaam = os.path.join ( Concurrentiedirectory, f'Totaal_{mod}_{inkgr}' )
                            Totaalrij = Routines.csvlezen ( Totaalmodfilenaam )
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
                            Totaalrij = Routines.csvlezen(Totaalmodfilenaam)
                            Generaalmatrix.append(Totaalrij)
                            Generaaltotaaltrans = Berekeningen.Transponeren(Generaalmatrix)
                        for i in range (len(Inwonersperklasse)):
                            Generaalmatrixproduct.append([])
                            for j in range (len(Inwonersperklasse[0])):
                                if Inwonersperklasse[i][j]>0:
                                    Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Arbeidsplaatsen[i][j]))
                                else:
                                    Generaalmatrixproduct[i].append(0)
                        Uitvoerfilenaam = os.path.join(Concurrentiedirectory, f'Pot_conc_{mod}')
                        Uitvoerfilenaamproduct = os.path.join(Concurrentiedirectory, f'Pot_concproduct_{mod}')
                        Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, header)
                        Routines.xlswegschrijven(Generaalmatrixproduct,Uitvoerfilenaamproduct, header)
    else:
        Stedelijkheidsgraadfilenaam = os.path.join(SEGSdirectory, 'Stedelijkheidsgraad')
        Stedelijkheidsgraad = Routines.csvintlezen(Stedelijkheidsgraadfilenaam)
        Sted = []
        for i in range(0, len(Stedelijkheidsgraad)):
            Sted.append(int(Stedelijkheidsgraad[i]))
        Voorkeurenfilenaam = os.path.join(SEGSdirectory, 'Voorkeuren')
        Voorkeuren = Routines.csvintlezen(Voorkeurenfilenaam, aantal_lege_regels=1)
        Afstandssoorten = ['Auto', 'Auto_OV', 'Auto_OV_Fiets']
        voorkeuren = ['Auto', 'Neutraal', 'Fiets', 'OV']
        Afstandenfile = os.path.join(Skimsdirectory, 'Restdag', 'Auto_Afstandhm')
        Afstanden = Routines.csvintlezen(Afstandenfile)
        for abg in autobezitgroepen:
            for mot in motieven:
                Bestemmingendirectory = os.path.join(Basisdirectory, Projectbestandsnaam, 'Resultaten', mot, abg,
                                                     'Bestemmingen', 'Restdag')
                Combinatiedirectory = os.path.join(Basisdirectory, regime, mot, 'Gewichten', 'Combinaties', 'Restdag')
                Enkelemodaliteitdirectory = os.path.join(Basisdirectory, regime, mot, 'Gewichten', 'Restdag')
                Afstandsdirectory = os.path.join(Basisdirectory, Projectbestandsnaam, 'Afstanden', mot, abg)
                os.makedirs (Afstandsdirectory, exist_ok=True)
                for inkgr in inkgroepen:
                    for afstsrt in Afstandssoorten:
                        print (afstsrt, inkgr)
                        Bereikfilenaam = os.path.join(Bestemmingendirectory, f'Totaal_{afstsrt}_{inkgr}')
                        Bereik = Routines.csvintlezen(Bereikfilenaam)
                        Bijhoudlijst = Lijstvolnullen()
                        for vk in voorkeuren:
                            if afstsrt == 'Auto':
                                Filenaam = os.path.join(Enkelemodaliteitdirectory, f'{afstsrt}_vk{vk}_{inkgr}')
                                Matrix = Routines.csvlezen(Filenaam)
                            else:
                                Filenaam = os.path.join(Combinatiedirectory, f'{afstsrt}_vk{vk}_{inkgr}')
                                Matrix = Routines.csvlezen(Filenaam)
                            if mot == 'werk':
                                Dezegroeplijst = bereken_afstanden_werk(Matrix, Beroepsbevolkingperklasse, Afstanden, Bereik,inkgr)
                            else:
                                Dezegroeplijst = bereken_afstanden_nietwerk(Matrix, Inwonerstotalen, Afstanden,
                                                                        Bereik, inkgr)

                            for i in range(0, len(Matrix)):
                                Vkeursaandeel = Voorkeuren[Sted[i] - 1][voorkeuren.index ( vk )] / 100
                                Bijhoudlijst[i]+= round(Dezegroeplijst[i] * Vkeursaandeel/1000,3)
                        print ('Opnieuw ', afstsrt, inkgr)
                        print (Bijhoudlijst)
                        Bijhoudfilenaam = os.path.join(Afstandsdirectory, f'Totaal_{afstsrt}_{inkgr}')
                        Routines.csvwegschrijven(Bijhoudlijst, Bijhoudfilenaam, soort='lijst')
                    Generaaltotaal_potenties = []
                    for afstsrt in Afstandssoorten:
                        Totaalmodfilenaam = os.path.join ( Afstandsdirectory, f'Totaal_{afstsrt}_{inkgr}' )
                        Totaalrij = Routines.csvlezen ( Totaalmodfilenaam )
                        Generaaltotaal_potenties.append ( Totaalrij )
                        Generaaltotaaltrans = Berekeningen.Transponeren ( Generaaltotaal_potenties )
                        Uitvoerfilenaam = os.path.join ( Afstandsdirectory, f'Afstanden_{inkgr}' )
                        Routines.csvwegschrijvenmetheader ( Generaaltotaaltrans, Uitvoerfilenaam, headstringkort )
                        Routines.xlswegschrijven ( Generaaltotaaltrans, Uitvoerfilenaam, headstringkortExcel )


                header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
                for afstsrt in Afstandssoorten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:

                        Totaalmodfilenaam = os.path.join (Afstandsdirectory, f'Totaal_{afstsrt}_{inkgr}')
                        Totaalrij = Routines.csvlezen(Totaalmodfilenaam)
                        Generaalmatrix.append(Totaalrij)
                        Generaaltotaaltrans = Berekeningen.Transponeren(Generaalmatrix)
                    for i in range (len(Inwonersperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range (len(Inwonersperklasse[0])):
                            if Inwonersperklasse[i][j]>0:
                                Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)
                    Uitvoerfilenaam = os.path.join(Afstandsdirectory, f'Afstanden_{afstsrt}')
                    Uitvoerfilenaamproduct = os.path.join(Afstandsdirectory, f'Afstandenproduct_{afstsrt}')
                    Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, header)
                    Routines.xlswegschrijven(Generaalmatrixproduct,Uitvoerfilenaamproduct, header)
