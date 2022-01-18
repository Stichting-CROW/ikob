import Routines
from tkinter import filedialog
from tkinter import *
import os
import Berekeningen

segs = Tk()
segs.geometry = ("10x10")
segs.label = ("Voer de directory waar de pure reistijdsegs en afstandsegs staan in")
segs.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de segsdirectory",)
segs.destroy()
Jaar = input ('Welk jaar gaat het om?')
SEGSdirectory = segs.directory + '/'
#SEGSdirectory = os.path.join(Skimsdirectory, 'SEGS')
Inkomensverdelingfilenaam = os.path.join ( SEGSdirectory, 'Inkomensverdeling_per_zone')
Inkomensverdelinggegevens = Routines.csvintlezen (Inkomensverdelingfilenaam,aantal_lege_regels=1)
print ('Lengte Inkomensverdelingsgegevens', len (Inkomensverdelinggegevens), len (Inkomensverdelinggegevens[0]))
CBSAutobezitfilenaam = os.path.join ( SEGSdirectory, 'CBS_autos_per_huishouden')
CBSAutobezitegevens = Routines.csvintlezen (CBSAutobezitfilenaam)
Inwoners18plusfilenaam = os.path.join(SEGSdirectory, f'Beroepsbevolking{Jaar}')
print (Inwoners18plusfilenaam)
Inwoners18plus = Routines.csvintlezen (Inwoners18plusfilenaam)
Stedelijkheidsgraadfilenaam = os.path.join ( SEGSdirectory, 'Stedelijkheidsgraad')
Stedelijkheidsgraadgegevens = Routines.csvlezen (Stedelijkheidsgraadfilenaam)
print ('Lengte Stedelijkheidsgraadgegevens', len (Stedelijkheidsgraadgegevens), len (Stedelijkheidsgraadgegevens[0]))

#Stedelijkheidsgraadgegevens[0] = '1'
#Stedelijkheidsgraadgegevens[900] = '1'
inkomens = ['laag', 'middellaag', 'middelhoog', 'hoog']
Elektrischeautos = input ('Toename elektrische autos (J/N)?')
if 'J' in Elektrischeautos:
    Elektrischpercentage = input('Welk percentage elektrische autos (20% of 40%)')
    if Elektrischpercentage == '40':
        Gratisautonaarinkomens = [0, 0.17, 0.58, 0.95]
    elif Elektrischpercentage == '20' :
        Gratisautonaarinkomens = [0, 0.05, 0.25, 0.5]
    else:
        print ('Wel een percentage noemen...')
else :
    Gratisautonaarinkomens = [0, 0.02, 0.175, 0.275]
GratisOVpercentage = 0.03

Kunstmatig = input ('Is er een file met kunstmatig autobezit?')
Kunst = False
if 'J' in Kunstmatig:
    Kunst = True
    kunstmautobezit = Tk ( )
    kunstmautobezit.geometry = ("10x10")
    kunstmautobezit.label = ("Voer de invoerfile in")
    kunstmautobezit.file = filedialog.askopenfilename ( initialdir=os.getcwd ( ),
                                                        title="Selecteer de file met de kunstmatige autobezittabel", )
    kunstmautobezit.destroy ( )
    Kunstmautobezitfile = kunstmautobezit.file
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
            Matrix2[i].append(round(Matrix[i][j]*Correctiefactor))
    return Matrix2

print ('de lengte is', len(Inkomensverdelinggegevens))


Totaaloverzicht = []
Header = []
WelAuto = []
GratisAuto = []
GratisAutoenOV = []
NietGratisAuto = []
GeenAutoWelRijbewijs = []
GeenRijbewijs = []

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

for i in range ( len ( Inkomensverdelinggegevens ) ):
    WelAuto.append([])
    GeenAutoWelRijbewijs.append([])
    GeenRijbewijs.append([])
    Totaaloverzicht.append([])
    Autobezitpercentage = []
    for Getal1,Getal2 in zip (Inkomensverdelinggegevens[i], WAuto[Sted[i]-1]) :
        Autobezitpercentage.append ( Getal1/100 * Getal2/100)
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
        Inkomensaandeel = Inkomensverdelinggegevens [i][inkomens.index(ink)]/100
        GratisAuto = WelAuto[i][inkomens.index(ink)] * Gratisautonaarinkomens [inkomens.index(ink)]
        NietGratisAuto= WelAuto[i][inkomens.index(ink)] - GratisAuto
        Totaaloverzicht[i].append( round(GratisAuto * (1-GratisOVpercentage)*10000 * Inkomensaandeel)) # Eerst GratisAuto
        Totaaloverzicht[i].append( round (GratisAuto * GratisOVpercentage*10000 * Inkomensaandeel)) # Dan GratisOV
        Totaaloverzicht[i].append( round (NietGratisAuto * GratisOVpercentage *10000 * Inkomensaandeel)) # WelAuto, maar gratisOV
        for vk in voorkeuren :
            Aandeelvk = NietGratisAuto * (1-GratisOVpercentage) * Voorkeuren[Sted[i] - 1][voorkeuren.index ( vk )] / 100
            Totaaloverzicht[i].append ( round (Aandeelvk * 10000 * Inkomensaandeel)) # Dan de diverse voorkeuren
        GeenAuto = GeenAutoWelRijbewijs[i][inkomens.index(ink)]
        Totaaloverzicht[i].append ( round(GeenAuto * GratisOVpercentage * 10000 * Inkomensaandeel)) # Gratis OV voor Geen Auto

        for vkg in voorkeurengeenauto:
            Aandeelvk = GeenAuto * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i] - 1][voorkeurengeenauto.index ( vkg )] / 100
            Totaaloverzicht[i].append ( round (Aandeelvk * 10000 * Inkomensaandeel)) # Dan de diverse voorkeuren
        GeenRB = GeenRijbewijs[i][inkomens.index(ink)]
        Totaaloverzicht[i].append ( round(GeenRB * GratisOVpercentage * 10000 * Inkomensaandeel)) # Gratis OV voor Geen Rijbewijs
        for vkg in voorkeurengeenauto:
            Aandeelvk = GeenRB * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i] - 1][voorkeurengeenauto.index ( vkg )] / 100
            Totaaloverzicht[i].append ( round (Aandeelvk * 10000 * Inkomensaandeel)) # Dan de diverse voorkeuren

Uitvoernaam = input ('Wat moet de naam van de uitvoerfile zijn?')
Totaaloverzichtfilenaam = os.path.join ( SEGSdirectory, f'{Uitvoernaam}' )
Routines.csvwegschrijvenmetheader ( Totaaloverzicht, Totaaloverzichtfilenaam, Header )
Header.insert(0, 'Zone')
Routines.xlswegschrijven ( Totaaloverzicht, Totaaloverzichtfilenaam, Header )
