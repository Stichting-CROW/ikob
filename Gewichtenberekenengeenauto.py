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
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
soortgeenauto = ['geenauto', 'geenrijbewijs']
voorkeuren = ['neutraal', 'OV', 'Fiets']
aantal_zones=5473
dagsoort = ['Avondspits', 'Ochtendspits','Restdag']

for ds in dagsoort:
#    for mot in motieven:
    mot = 'winkelnietdagelijksonderwijs'
    for sga in soortgeenauto:
        for ink in inkomen:
            for vk in voorkeuren:
                if mot != 'werk':
                    soort = 'overig'
                else:
                    soort = 'werk'
                Filenaam = Ervarenreistijddirectory + ds + '/Auto' + '_' + soort + '_' + ink
                GGRskim = Routines.csvlezen ( Filenaam )
                if mot == 'werk':
                    constanten = Constantengenerator.alomwerk ('Auto',vk)
                elif mot == 'winkeldagelijkszorg':
                    constanten = Constantengenerator.alomwinkeldagelijkszorg ('Auto', vk )
                else:
                    constanten = Constantengenerator.alomwinkelnietdagelijksonderwijs ('Auto', vk )
                Gewichten = Berekeningen.gewichten(GGRskim,constanten,aantal_rijen=5473)
                Gewichtendirectory = Skimsdirectory + 'Gewichten/' + ds + '/' + mot + '/'
                Uitvoerfilenaam = Gewichtendirectory + sga + 'Auto' + '_' + vk + '_' + ink
                Routines.csvwegschrijven(Gewichten,Uitvoerfilenaam)
