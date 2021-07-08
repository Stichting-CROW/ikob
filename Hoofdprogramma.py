import Invoer
import Stappen
from tkinter import filedialog
from tkinter import *
from PIL import Image
#Open image using Image module
im = Image.open("C:/Users/hansv/OneDrive/Pictures/ENKOB.png")
#Show actual Image
im.show()
import Routines



Invoer.Welkomstscherm()
motief = Invoer.haal_motief_op()
basis = Tk()
basis.geometry = ("10x10")
basis.label = ("Voer de basis_directory in")
basis.directory =  filedialog.askdirectory (initialdir = "/",title = "Selecteer de Basisdirectory",)
basis.destroy()
segs = Tk()
segs.directory =  filedialog.askdirectory (initialdir = "/",title = "Selecteer de SEGSdirectory",)
segs.destroy()
parkeer = Tk()
parkeer.directory =  filedialog.askdirectory (initialdir = "/",title = "Selecteer de parkeerdirectory",)
parkeer.destroy()
rtconstanten = Tk()
rtconstanten.directory = filedialog.askdirectory (initialdir = "/",title = "Selecteer de directory met de reistijdconstanten",)
rtconstanten.destroy()

Basisdirectory = basis.directory + '/'
SEGSdirectory = segs.directory +'/'
Parkeerdirectory = parkeer.directory + '/'
Vervalcurvedirectory = rtconstanten.directory + '/'
Motievendirectory = basis.directory + '/'+motief +'/'
keuze = 'Doorgaan'
while keuze != 'Stoppen':
    keuze = Invoer.haal_keuze_op()
    if keuze == 'Stap1':
        Stappen.Stap1 (Basisdirectory, Parkeerdirectory, motief)
        Invoer.Klaar()
    elif keuze == 'Stap2':
        Stappen.Stap2 (Basisdirectory, motief)
        Invoer.Klaar()
    elif keuze == 'Stap3':
        Stappen.Stap3 (Basisdirectory, SEGSdirectory, motief)
        Invoer.Klaar()
    elif keuze == 'Stap4' :
        Stappen.Stap4 (Basisdirectory, motief)
        Invoer.Klaar()
    elif keuze == 'Stap5' :
        Stappen.Stap5 (Basisdirectory, motief)
        Invoer.Klaar()
    elif keuze == 'Stap6':
        Stappen.Stap6 (Basisdirectory, motief)
        Invoer.Klaar()
    elif keuze == 'Stap7' :
        Stappen.Stap7 ( Basisdirectory, motief )
        Invoer.Klaar ( )
    elif keuze == 'Stap8':
        Stappen.Stap8 ( Basisdirectory, motief )
        Invoer.HelemaalKlaar ( )
        keuze = 'Stoppen'




