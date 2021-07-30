import Routines
import Berekeningen
from tkinter import filedialog
from tkinter import *

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = "/",title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'

modaliteiten = ['Fiets', 'Auto', 'OV']
motieven = ['werk','overig']
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
specialegroep = [ 'geenauto', 'geenrijbewijs']
Specialevermenigvuldigingsfactoren_Auto = {'geenauto':3.5, 'geenrijbewijs':15}
TVOMwerk = {'hoog':4, 'middelhoog':6, 'middellaag':9, 'laag':12}
TVOMoverig = {'hoog':4.8 , 'middelhoog': 7.25, 'middellaag': 10.9, 'laag':15.5}
varkosten = 0.12
aantal_zones=5473
dagsoort = ['Avondspits', 'Ochtendspits','Restdag']

for ds in dagsoort:
    Tijdfilenaam = Skimsdirectory + 'skims/' + ds + '/Auto_Tijd'
    Tijdmatrix = Routines.csvlezen(Tijdfilenaam, aantal_lege_regels=4)
    Afstandfilenaam = Skimsdirectory + 'skims/' + ds + '/Auto_Afstand'
    Afstandmatrix = Routines.csvlezen(Afstandfilenaam, aantal_lege_regels=4)

    for motief in motieven:
        for ink in inkomen:
            for sg in specialegroep:
                GGRskim = []
                if motief == 'werk':
                    Vermenigvuldigingsfactor = TVOMwerk.get (ink) * Specialevermenigvuldigingsfactoren_Auto.get(sg)
                if motief == 'overig':
                    Vermenigvuldigingsfactor = TVOMoverig.get (ink) * Specialevermenigvuldigingsfactoren_Auto.get(sg)
                for i in range (0,aantal_zones):
                    GGRskim.append([])
                    for j in range (0,aantal_zones):
                        if i == j:
                            GGRskim[i].append(9999)
                        else:
                            GGRskim[i].append(Tijdmatrix [i][j] + Vermenigvuldigingsfactor * Afstandmatrix [i][j]*varkosten)

                Uitvoerfilenaam = Skimsdirectory + 'Ervarenreistijd/' + ds + '/' + sg + '_Auto_' + motief + '_' + ink
                Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)
