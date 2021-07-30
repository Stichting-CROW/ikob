import Routines
import Berekeningen
import Constantengenerator
from tkinter import filedialog
from tkinter import *

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = "/",title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'
Ervarenreistijddirectory = Skimsdirectory + 'Ervarenreistijd/'

motieven = ['werk','winkeldagelijkszorg', 'winkelnietdagelijksonderwijs']
aantal_zones=5473
dagsoort = ['Avondspits', 'Ochtendspits','Restdag']

for ds in dagsoort:
    for mot in motieven:
        Filenaam = Ervarenreistijddirectory + ds + '/Gratisauto'
        GGRskim = Routines.csvlezen(Filenaam)
        if mot == 'werk':
            constanten = Constantengenerator.alomwerk ('Auto','Auto')
        elif mot == 'winkeldagelijkszorg':
            constanten = Constantengenerator.alomwinkeldagelijkszorg ( 'Auto', 'Auto' )
        else:
            constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( 'Auto', 'Auto' )
        Gewichten = Berekeningen.gewichten(GGRskim,constanten,aantal_rijen=5473)
        Gewichtendirectory = Skimsdirectory + 'Gewichten/' + ds + '/' + mot + '/'
        Uitvoerfilenaam = Gewichtendirectory + 'Gratisauto'
        Routines.csvwegschrijven(Gewichten,Uitvoerfilenaam)
