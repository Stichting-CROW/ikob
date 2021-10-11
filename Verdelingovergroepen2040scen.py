import Routines
from tkinter import filedialog
from tkinter import *
import os
import Berekeningen

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'
SEGSdirectory = os.path.join(Skimsdirectory, 'SEGS')
Inkomensverdelingfilenaam = os.path.join ( SEGSdirectory, 'Inkomensverdeling_per_zone')
Inkomensverdelinggegevens = Routines.csvintlezen (Inkomensverdelingfilenaam,aantal_lege_regels=1)
CBSAutobezitfilenaam = os.path.join ( SEGSdirectory, 'CBS_autos_per_huishouden')
CBSAutobezitgegevens = Routines.csvintlezen (CBSAutobezitfilenaam)
Kunstmatigautobezitfile = os.path.join ( SEGSdirectory, 'Kunstmatig_autobezit')
Kunstmatigautobezit = Routines.csvintlezen (Kunstmatigautobezitfile)
Inwoners18plusfilenaam = os.path.join(SEGSdirectory, 'Inwoners18plus')
Inwoners18plus = Routines.csvintlezen (Inwoners18plusfilenaam)
Stedelijkheidsgraadfilenaam = os.path.join ( SEGSdirectory, 'Stedelijkheidsgraad')
Stedelijkheidsgraadgegevens = Routines.csvlezen (Stedelijkheidsgraadfilenaam)
Stedelijkheidsgraadgegevens[0] = '1'
inkomens = ['laag', 'middellaag', 'middelhoog', 'hoog']
Gratisautonaarinkomens = [0, 0.17, 0.60, 0.95]
Gratisautopercentage = {'laag':0, 'middellaag':0.1, 'middelhoog':0.35, 'hoog':0.55}

Sted = []
for i in range (0,len(Stedelijkheidsgraadgegevens)):
    Sted.append(int (Stedelijkheidsgraadgegevens[i]))
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


print ('de lengte is', len(Inkomensverdelinggegevens))

GratisAuto = []
GratisAutoGratisOV = []
NietGratisAuto = []
GeenAuto=[]
GeenRijbewijs=[]
Autobezit = []
Totaaloverzicht = []
Headstring = []
GratisAutoMatrix = []
GratisAutoenOVMatrix = []
for i in range ( len ( Inkomensverdelinggegevens ) ):
    Gratisautobezitpercentage = []
    Autobezitpercentage = []
    GeenAutopercentage = []
    GeenRijbewijspercentage = []

    for Getal1,Getal2 in zip (Inkomensverdelinggegevens[i], WAuto[Sted[i]-1]) :
        Autobezitpercentage.append ( Getal1/100 * Getal2/100)
    Autobezitpercentages = sum (Autobezitpercentage)
    for Getal1,Getal2 in zip (Inkomensverdelinggegevens[i] , GAuto[Sted[i]-1]) :
        GeenAutopercentage.append (Getal1/100 * Getal2/100)
    GeenAutopercentages = sum (GeenAutopercentage)
    for Getal1,Getal2 in zip (Inkomensverdelinggegevens[i] , GRijbewijs[Sted[i]-1]) :
        GeenRijbewijspercentage.append(Getal1/100 * Getal2/100)
    GeenRijbewijspercentages = sum (GeenRijbewijspercentage)
    minimumautobezit = min(CBSAutobezitgegevens[i], Kunstmatigautobezit[i])
#    minimumautobezit = 0

    if minimumautobezit/100 < Autobezitpercentages :
        Autobezitcorrectiefactor = (1-minimumautobezit/100) / (1-Autobezitpercentages)
        Autobezitpercentages = minimumautobezit/100
    else :
        Autobezitcorrectiefactor = 1
    vermenigvuldiging = []
    for Getal1,Getal2 in zip (Gratisautonaarinkomens,Inkomensverdelinggegevens[i]):
        vermenigvuldiging.append(Getal1 * Getal2 * float(Autobezitpercentages))

    Gratisautobezit = sum (vermenigvuldiging)/100
    GratisAutoMatrix.append([])
    GratisAutoenOVMatrix.append([])
    for ink in inkomens:
        Waarde=Gratisautonaarinkomens[inkomens.index(ink)]*Inkomensverdelinggegevens[i][inkomens.index(ink)]/100*float(Autobezitpercentages)
        GratisAutoMatrix[i].append(int(Waarde *9700))
        GratisAutoenOVMatrix[i].append(int(Waarde*300))

    OverigWAuto = float(Autobezitpercentages - Gratisautobezit)
    NietGratisAuto.append(OverigWAuto)
    Autobezit.append(Autobezitpercentages)

    GeenAuto.append(GeenAutopercentages * Autobezitcorrectiefactor)
    GeenRijbewijs.append (GeenRijbewijspercentages * Autobezitcorrectiefactor)
    GratisAuto.append ( float(Gratisautobezit))

soortgratisauto = ['GratisAuto','GratisAuto_GratisOV']
for sga in soortgratisauto:
    for ink in inkomens:
        rij = inkomens.index(ink)
        if 'OV' in sga:
            GratisAutoKolom=[row[rij] for row in GratisAutoenOVMatrix]
        else:
            GratisAutokolom=[row[rij] for row in GratisAutoMatrix]
        print (sga,ink)
        Totaaloverzicht.append(GratisAutokolom)
        GratisAutofilenaam = os.path.join ( SEGSdirectory, f'{sga}_{ink}' )
        Routines.csvwegschrijven ( GratisAutokolom, GratisAutofilenaam, soort='lijst' )
        Headstring.append (sga+'_'+ink)

Overzicht = []
Overzichtheader = []
Overzicht.append(GratisAuto)
Overzichtheader.append('GratisAuto')


"""""
    else:
        GeenAuto.append(0)
        GeenRijbewijs.append(0)
        OverigWelAuto.append(0)
        GratisAuto.append(0)
        GratisAutoGratisOV.append(0)
"""


NietGratisAutooverzicht = []
NGAGrOVOverzicht = []
OverigWelAuto = []

for i in range(len (Autobezit)):
    NietGratisAutooverzicht.append([])
    NGAGrOVOverzicht.append([])
    OverigWelAuto.append([])
    for ink in inkomens:
        NGAandeel = Autobezit[i] * Inkomensverdelinggegevens[i][inkomens.index(ink)]/100 * (1-Gratisautonaarinkomens[inkomens.index(ink)])
        NietGratisAutooverzicht[i].append (NGAandeel)
        NGAGrOVOverzicht[i].append (0.03 * NGAandeel)
        OverigWelAuto[i].append (0.97 * NGAandeel)
for ink in inkomens:
    rij = inkomens.index(ink)
    NGAGrOVkolom = [row[rij] for row in NGAGrOVOverzicht]
    for i in range(len (NGAGrOVkolom)):
        NGAGrOVkolom[i] = int (NGAGrOVkolom[i]*10000)
    Totaaloverzicht.append(NGAGrOVkolom)
    Overzicht2filenaam = os.path.join ( SEGSdirectory, f'WelAuto_GratisOV_{ink}' )
    Routines.csvwegschrijven ( NGAGrOVkolom, Overzicht2filenaam,soort='lijst')
    Headstring.append ('WelAuto_GratisOV_'+ink)

Overzicht.append(NietGratisAuto)
Overzichtheader.append('NietGratisAuto')
Overzicht.append(GeenAuto)
Overzichtheader.append('GeenAuto')
Overzicht.append(GeenRijbewijs)
Overzichtheader.append('GeenRijbewijs')
OverzichtheadstringExcel=Overzichtheader
OverzichtheadstringExcel.insert(0,'Zone')
Overzichtfilenaam = os.path.join ( SEGSdirectory, f'Overzicht' )
Routines.csvwegschrijvenmetheader ( Overzicht, Overzichtfilenaam, Overzichtheader )
Routines.xlswegschrijven ( Overzicht, Overzichtfilenaam, OverzichtheadstringExcel )


groepenindeling = ['WelAuto', 'GeenAuto', 'GeenRijbewijs']
voorkeuren = ['Auto','Neutraal', 'Fiets', 'OV']
voorkeurengeenauto = ['Neutraal', 'Fiets', 'OV']

for gr in groepenindeling:
    if gr == 'WelAuto' :
        for vk in voorkeuren :
            for ink in inkomens :
                print ('Bezig met',gr,vk,ink)
                Autolijst = []
                for i in range (0, len (OverigWelAuto)) :
                    Aandeelvk = OverigWelAuto[i][inkomens.index(ink)] * Voorkeuren[Sted[i]-1][voorkeuren.index(vk)]/100
                    Autolijst.append (int(Aandeelvk*10000))
                Headstring.append ( 'WelAuto_vk' + vk + '_' + ink)
                Totaaloverzicht.append (Autolijst)
                WelAutofilenaam = os.path.join ( SEGSdirectory, f'{gr}_vk{vk}_{ink}' )
                Routines.csvwegschrijven ( Autolijst, WelAutofilenaam, soort='lijst' )
    else :
        if gr == 'GeenAuto' :
            Hfdindeling = GeenAuto
            HfdSted = GAuto
        if gr == 'GeenRijbewijs' :
            Hfdindeling = GeenRijbewijs
            HfdSted = GRijbewijs
        GratisOV = []
        OverigGeen = []
        for i in range ( len (GeenAuto) ):
            GratisOV.append ( 0.03 * Hfdindeling[i] )
            OverigGeen.append (0.97 * Hfdindeling[i] )

        for ink in inkomens :
            GratisOVlijst = []
            for i in range (len (GeenAuto)) :
                Aandeel = GratisOV[i] * Inkomensverdelinggegevens[i][inkomens.index(ink)]/100
                GratisOVlijst.append (int(Aandeel * 10000))
            Headstring.append ( gr + '_GratisOV' + '_' + ink)
            Totaaloverzicht.append ( GratisOVlijst )
            GratisOVfilenaam = os.path.join ( SEGSdirectory, f'{gr}_GratisOV_{ink}' )
            Routines.csvwegschrijven ( GratisOVlijst, GratisOVfilenaam, soort='lijst' )

        for vk in voorkeurengeenauto :
            for ink in inkomens :
                print ( 'Bezig met', gr, vk, ink )
                GeenLijst = []
                for i in range (len(GeenAuto)) :
                    Aandeel = OverigGeen[i] * Inkomensverdelinggegevens[i][inkomens.index(ink)]/100
                    Aandeelvk = Aandeel * VoorkeurenGeenAuto[Sted[i]-1][voorkeurengeenauto.index(vk)]/100
                    GeenLijst.append (int (Aandeelvk*10000))
                Headstring.append ( gr + '_vk' + vk + '_' + ink)
                Totaaloverzicht.append ( GeenLijst )
                Geenfilenaam = os.path.join ( SEGSdirectory, f'{gr}_vk{vk}_{ink}' )
                Routines.csvwegschrijven ( GeenLijst, Geenfilenaam, soort='lijst' )

HeadstringExcel = Headstring
HeadstringExcel.insert(0, 'Zone')
print (Totaaloverzicht[1])
Totaaloverzichtinwoners = []
for i in range (len(Totaaloverzicht)):
    Totaaloverzichtinwoners.append ([])
    for j in range (len(Totaaloverzicht[0])):
        Totaaloverzichtinwoners[i].append(int(Totaaloverzicht[i][j]*Inwoners18plus[j]/10000))

Totaaloverzichttrans = Berekeningen.Transponeren ( Totaaloverzicht )
Totaaloverzichtinwonerstrans = Berekeningen.Transponeren(Totaaloverzichtinwoners)
Totaaloverzichtfilenaam = os.path.join ( SEGSdirectory, f'Verdelingbuurten' )
Totaaloverzichtinwonersfilenaam = os.path.join ( SEGSdirectory, f'Verdelingbuurten_echteinwoners' )
Routines.csvwegschrijvenmetheader ( Totaaloverzichttrans, Totaaloverzichtfilenaam, Headstring )
Routines.csvwegschrijvenmetheader ( Totaaloverzichtinwonerstrans, Totaaloverzichtinwonersfilenaam, Headstring )
Routines.xlswegschrijven ( Totaaloverzichttrans, Totaaloverzichtfilenaam, HeadstringExcel )
Routines.xlswegschrijven ( Totaaloverzichtinwonerstrans, Totaaloverzichtinwonersfilenaam, HeadstringExcel )
