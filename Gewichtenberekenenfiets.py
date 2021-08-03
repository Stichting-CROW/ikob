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

modaliteiten = ['Fiets','Efiets']
motieven = ['werk','winkeldagelijkszorg', 'winkelnietdagelijksonderwijs']
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
voorkeuren = ['', 'Fiets', 'Efiets']

aantal_zones=5473
dagsoort = ['Avondspits', 'Ochtendspits','Restdag']

for ds in dagsoort:
    for mot in motieven:
        for mod in modaliteiten:
            for vk in voorkeuren:
                Filenaam = Ervarenreistijddirectory + ds + '/Fiets'
                GGRskim = Routines.csvlezen(Filenaam)
                if mot == 'werk':
                    constanten = Constantengenerator.alomwerk (mod,vk)
                elif mot == 'winkeldagelijkszorg':
                    constanten = Constantengenerator.alomwinkeldagelijkszorg ( mod, vk )
                else:
                    constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ( mod, vk )
                Gewichten = Berekeningen.gewichten(GGRskim,constanten,aantal_rijen=5473)
                Gewichtendirectory = Skimsdirectory + 'Gewichten/' + ds + '/' + mot + '/'
                Uitvoerfilenaam = Gewichtendirectory + mod + '_' + vk
                Routines.csvwegschrijven(Gewichten,Uitvoerfilenaam)
