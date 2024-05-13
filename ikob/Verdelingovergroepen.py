import Routines
from tkinter import filedialog
from tkinter import *
import os
from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()
project_config = config['project']
paden_config = config['project']['paden']
skims_config = config['skims']
verdeling_config = config['verdeling']

# Ophalen van instellingen
Skimsdirectory = paden_config['skims_directory']
SEGSdirectory = paden_config['segs_directory']
scenario = project_config['verstedelijkingsscenario']
Kunst = verdeling_config['kunstmab']['gebruiken']
Kunstmautobezitfile = verdeling_config['kunstmab']['bestand']
GratisOVpercentage = verdeling_config['GratisOVpercentage']
motieven = project_config ['motieven']


# Vaste waarden
inkomens = ['laag', 'middellaag', 'middelhoog', 'hoog']

#Inkomensverdelingfilenaam = os.path.join ( SEGSdirectory, 'Inkomensverdeling_per_zone')
#Inkomensverdeling = Routines.csvintlezen (Inkomensverdelingfilenaam,aantal_lege_regels=1)
CBSAutobezitfilenaam = os.path.join ( SEGSdirectory, 'CBS_autos_per_huishouden')
CBSAutobezitegevens = Routines.csvintlezen (CBSAutobezitfilenaam)
#Inwoners18plusfilenaam = os.path.join(SEGSdirectory, f'Beroepsbevolking{scenario}')
#print (Inwoners18plusfilenaam)
#Inwoners18plus = Routines.csvintlezen (Inwoners18plusfilenaam)
Stedelijkheidsgraadfilenaam = os.path.join ( SEGSdirectory, 'Stedelijkheidsgraad')
Stedelijkheidsgraadgegevens = Routines.csvlezen (Stedelijkheidsgraadfilenaam)

#Stedelijkheidsgraadgegevens[0] = '1'
#Stedelijkheidsgraadgegevens[900] = '1'

Gratisautonaarinkomens = [0, 0.02, 0.175, 0.275]

if Kunst:
    Kunstmautobezitfile = Kunstmautobezitfile.replace ( '.csv', '' )
    Kunstmatigautobezit = Routines.csvintlezen ( Kunstmautobezitfile, aantal_lege_regels=0)

Sted = []

for i in range (0,len(Stedelijkheidsgraadgegevens)):
    Sted.append(int (Stedelijkheidsgraadgegevens[i]))
if Kunst:
    Minimumautobezit = []
    for i in range (0, len(CBSAutobezitegevens)):
        Minimumautobezit.append(min(CBSAutobezitegevens[i],Kunstmatigautobezit[i]))
else:
    Minimumautobezit = CBSAutobezitegevens

GeenRijbewijsfilenaam = os.path.join ( SEGSdirectory, 'GeenRijbewijs')
GRijbewijs = Routines.csvintlezen (GeenRijbewijsfilenaam,aantal_lege_regels=1)
GeenAutofilenaam = os.path.join ( SEGSdirectory, 'GeenAuto')
GAuto = Routines.csvintlezen (GeenAutofilenaam,aantal_lege_regels=1)
WelAutofilenaam = os.path.join ( SEGSdirectory, 'WelAuto')
WAuto = Routines.csvintlezen (WelAutofilenaam,aantal_lege_regels=1)
Voorkeurenfilenaam = os.path.join ( SEGSdirectory, 'Voorkeuren')
Voorkeuren = Routines.csvintlezen (Voorkeurenfilenaam,aantal_lege_regels=1)
VoorkeurenGeenAutofilenaam = os.path.join ( SEGSdirectory, 'VoorkeurenGeenAuto')
VoorkeurenGeenAuto = Routines.csvintlezen (VoorkeurenGeenAutofilenaam,aantal_lege_regels=1)

inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']
voorkeuren = ['Auto','Neutraal', 'Fiets', 'OV']
voorkeurengeenauto = ['Neutraal', 'Fiets', 'OV']
soorten = ['GratisAuto', 'WelAuto', 'GeenAuto', 'GeenRijbewijs' ]

def Corrigeren (Matrix, Lijst) :
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

Totaaloverzicht = []
Overzichttotaalautobezit = []
Header = []
WelAuto = []
GratisAuto = []
GratisAutoenOV = []
NietGratisAuto = []
GeenAutoWelRijbewijs = []
GeenRijbewijs = []

for mot in motieven:
    if mot == 'werk':
        Bevolkingsdeel = 'Beroepsbevolking'
        Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'{Bevolkingsdeel}_inkomensklasse')
    elif mot == 'winkelnietdagelijksonderwijs':
        Bevolkingsdeel = 'Leerlingen'
        Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'{Bevolkingsdeel}')
    else:
        Bevolkingsdeel = 'Inwoners'
        Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'{Bevolkingsdeel}_inkomensklasse')
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
    print('Lengte Inkomensverdelingsgegevens', len(Inkomensverdeling), len(Inkomensverdeling[0]))

    for ink in inkomens:
        for srt in soorten :
            if srt== 'GratisAuto' :
                Header.append (f'{srt}_{ink}')
                Header.append (f'{srt}_GratisOV_{ink}')
            elif srt== 'WelAuto' :
                Header.append (f'{srt}_GratisOV_{ink}')
                for vk in voorkeuren :
                    Header.append (f'{srt}_vk{vk}_{ink}')
            else :
                Header.append ( f'{srt}_GratisOV_{ink}' )
                for vkg in voorkeurengeenauto:
                    Header.append ( f'{srt}_vk{vkg}_{ink}' )

                # Eerst "theoretosch auto- en rijbewijsbezit" vaststellen

    for i in range ( len ( Inkomensverdeling ) ):
        WelAuto.append([])
        GeenAutoWelRijbewijs.append([])
        GeenRijbewijs.append([])
        Totaaloverzicht.append([])
        Overzichttotaalautobezit.append([])
        Autobezitpercentage = []
        for Getal1,Getal2 in zip (Inkomensverdeling[i], WAuto[Sted[i]-1]) :
            Autobezitpercentage.append ( Getal1 * Getal2/100)
        Autobezitpercentages = sum (Autobezitpercentage)

        #Kijken of het werkelijke autobezit lager is:
        if Minimumautobezit[i] > 0 :
            if Minimumautobezit[i]/100 < Autobezitpercentages :
                Autobezitcorrectiefactor = (Minimumautobezit[i]/100) / Autobezitpercentages
                Autobezitpercentages = Minimumautobezit [i]/100
            else :
                Autobezitcorrectiefactor = 1
        else :
            Autobezitcorrectiefactor = 1

        # Nu autobezit, rijbewijsbezit per inkomensklasse bepalen

        for ink in inkomens :
            WAutoaandeeltheor = WAuto[Sted[i]-1][inkomens.index(ink)]/100
            WAutoaandeel = WAutoaandeeltheor * Autobezitcorrectiefactor
            if Autobezitcorrectiefactor!=1 :
                Geenautobezitcorrectiefactor = (1 - WAutoaandeel)/ (1-WAutoaandeeltheor)
            else:
                Geenautobezitcorrectiefactor = 1
            WelAuto[i].append (WAutoaandeel)
            GeenAutoverhouding = GAuto[Sted[i]-1][inkomens.index(ink)]
            GeenAutoWelRijbewijs[i].append (GAuto[Sted[i] - 1][inkomens.index(ink)]/100 * Geenautobezitcorrectiefactor )
            GeenRijbewijs[i].append (GRijbewijs[Sted[i] - 1][inkomens.index(ink)]/100 * Geenautobezitcorrectiefactor)


        for ink in inkomens :
            #Van de auto's de gratisauto's en gratisauto en OV-bepalen en de rest overhouden
            Overzichtperinkomensgroep = []
            Inkomensaandeel = Inkomensverdeling [i][inkomens.index(ink)]
            GratisAuto = WelAuto[i][inkomens.index(ink)] * Gratisautonaarinkomens [inkomens.index(ink)]
            NietGratisAuto= WelAuto[i][inkomens.index(ink)] - GratisAuto
            GratisAutoaandeel = GratisAuto * (1-GratisOVpercentage) * Inkomensaandeel
            Totaaloverzicht[i].append( round(GratisAutoaandeel,4)) # Eerst GratisAuto
            Overzichtperinkomensgroep.append( round(GratisAutoaandeel,4)) # Eerst GratisAuto
            GratisAutoenOVaandeel = GratisAuto * GratisOVpercentage * Inkomensaandeel
            Totaaloverzicht[i].append( round (GratisAutoenOVaandeel,4)) # Dan GratisOV
            Overzichtperinkomensgroep.append( round (GratisAutoenOVaandeel,4)) # Dan GratisOV
            GratisOVaandeel = NietGratisAuto * GratisOVpercentage * Inkomensaandeel
            Totaaloverzicht[i].append( round (GratisOVaandeel,4)) # WelAuto, maar gratisOV
            Overzichtperinkomensgroep.append( round (GratisOVaandeel,4)) # WelAuto, maar gratisOV
            for vk in voorkeuren :
                Aandeelvk = NietGratisAuto * (1-GratisOVpercentage) * Voorkeuren[Sted[i] - 1][voorkeuren.index ( vk )] / 100
                Voorkeursaandeel = Aandeelvk * Inkomensaandeel
                Totaaloverzicht[i].append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren
                Overzichtperinkomensgroep.append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren

            GeenAuto = GeenAutoWelRijbewijs[i][inkomens.index(ink)]
            GeenAutoGratisOVaandeel = GeenAuto * GratisOVpercentage * Inkomensaandeel
            Totaaloverzicht[i].append ( round(GeenAutoGratisOVaandeel,4)) # Gratis OV voor Geen Auto
            Overzichtperinkomensgroep.append(0)
            for vkg in voorkeurengeenauto:
                Aandeelvk = GeenAuto * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i] - 1][voorkeurengeenauto.index ( vkg )] / 100
                Voorkeursaandeel = Aandeelvk * Inkomensaandeel
                Totaaloverzicht[i].append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren
                Overzichtperinkomensgroep.append(0)
            GeenRB = GeenRijbewijs[i][inkomens.index(ink)]
            GeenRBGratisOVaandeel = GeenRB * GratisOVpercentage * Inkomensaandeel
            Totaaloverzicht[i].append ( round(GeenRBGratisOVaandeel,4)) # Gratis OV voor Geen Rijbewijs
            Overzichtperinkomensgroep.append(0)
            for vkg in voorkeurengeenauto:
                Aandeelvk = GeenRB * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i] - 1][voorkeurengeenauto.index ( vkg )] / 100
                Voorkeursaandeel = Aandeelvk * Inkomensaandeel
                Totaaloverzicht[i].append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren
                Overzichtperinkomensgroep.append(0)
            for j in range (len(Overzichtperinkomensgroep)):
                if sum (Overzichtperinkomensgroep)>0:
                    Overzichttotaalautobezit[i].append(round(Overzichtperinkomensgroep[j]/sum (Overzichtperinkomensgroep) *
                                                             Inkomensaandeel,4))
                else:
                    Overzichttotaalautobezit[i].append(0)


    print (Overzichttotaalautobezit)
    Totaaloverzichtfilenaam = os.path.join ( SEGSdirectory, scenario, f'Verdeling_over_groepen_{Bevolkingsdeel}' )
    Overzichttotaalautofilenaam = os.path.join ( SEGSdirectory, scenario, f'Verdeling_over_groepen_{Bevolkingsdeel}_alleen_autobezit' )
    Routines.csvwegschrijvenmetheader ( Totaaloverzicht, Totaaloverzichtfilenaam, Header )
    Routines.csvwegschrijvenmetheader ( Overzichttotaalautobezit, Overzichttotaalautofilenaam, Header )
    Header.insert(0, 'Zone')
    Routines.xlswegschrijven ( Totaaloverzicht, Totaaloverzichtfilenaam, Header )
    Routines.xlswegschrijven ( Overzichttotaalautobezit, Overzichttotaalautofilenaam, Header )
