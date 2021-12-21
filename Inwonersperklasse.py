import Routines
import Berekeningen
import Constantengenerator
from tkinter import filedialog
from tkinter import *
import os

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'

Inkomensverdelingsfilenaam = os.path.join (Skimsdirectory, 'Inkomensverdeling_per_zone')
Inwonersaantalfilenaam = os.path.join (Skimsdirectory, 'Inwoners15plus')
Inkomensverdeling = Routines.csvintlezen(Inkomensverdelingsfilenaam,aantal_lege_regels=1)
Inwoners = Routines.csvintlezen(Inwonersaantalfilenaam)
Inwonersperzone = []
for i in range (len(Inwoners)):
    Inwonersperzone.append([])
    for j in range (len(Inkomensverdeling[0])):
        Inwonersperzone[i].append(int(Inwoners[i]*Inkomensverdeling[i][j]/100))
Echteinwoners_zone_klassefile = os.path.join (Skimsdirectory, 'Inwoners_per_klasse')
Routines.csvwegschrijven(Inwonersperzone,Echteinwoners_zone_klassefile)