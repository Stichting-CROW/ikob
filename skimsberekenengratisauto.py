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

motieven = ['werk','overig']
aspect = ['Tijd', 'Kosten']
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
TVOMwerk = {'hoog':4, 'middelhoog':6, 'middellaag':9, 'laag':12}
TVOMoverig = {'hoog':4.8 , 'middelhoog': 7.25, 'middellaag': 10.9, 'laag':15.5}
varkosten = 0
aantal_zones=5473
dagsoort = ['Avondspits', 'Ochtendspits','Restdag']


for ds in dagsoort:
    Tijdfilenaam = Skimsdirectory + 'skims/' + ds + '/Auto_Tijd'
    Tijdmatrix = Routines.csvlezen(Tijdfilenaam, aantal_lege_regels=4)
    Afstandfilenaam = Skimsdirectory + 'skims/' + ds + '/Auto_Afstand'
    Afstandmatrix = Routines.csvlezen(Afstandfilenaam, aantal_lege_regels=4)
    GGRskim=[]

    for i in range (0,aantal_zones):
        GGRskim.append([])
        for j in range (0,aantal_zones):
            GGRskim[i].append(Tijdmatrix [i][j])

    Uitvoerfilenaam = Skimsdirectory + 'Ervarenreistijd/' + ds + '/GratisAuto'
    Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)



