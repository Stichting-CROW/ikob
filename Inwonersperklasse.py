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
paden_config = config['project']['paden']

# Ophalen van instellingen
Skimsdirectory = paden_config['invoer_skims_directory']
segs = Tk()
segs.geometry = ("10x10")
segs.label = ("Voer de directory waar de pure reistijdsegs en afstandsegs staan in")
segs.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de directory segsdirectory",)
segs.destroy()
SEGSdirectory = segs.directory + '/'

Jaar=input ('Welk jaar gaat het om?')
Inkomensverdelingsfilenaam = os.path.join (SEGSdirectory, 'Inkomensverdeling_per_zone')
Inwonersaantalfilenaam = os.path.join (SEGSdirectory, f'Beroepsbevolking{Jaar}')
Inkomensverdeling = Routines.csvintlezen(Inkomensverdelingsfilenaam,aantal_lege_regels=1)
Inwoners = Routines.csvintlezen(Inwonersaantalfilenaam)
Inwonersperzone = []
for i in range (len(Inwoners)):
    Inwonersperzone.append([])
    for j in range (len(Inkomensverdeling[0])):
        Inwonersperzone[i].append(int(Inwoners[i]*Inkomensverdeling[i][j]/100))
Echteinwoners_zone_klassefile = os.path.join (SEGSdirectory, f'Inwoners_per_klasse{Jaar}')
Routines.csvwegschrijven(Inwonersperzone,Echteinwoners_zone_klassefile)