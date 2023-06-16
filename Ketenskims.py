import Routines
from tkinter import filedialog
from tkinter import *
import os
skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims in staan")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'5
Autotijdfilenaam = os.path.join ( Skimsdirectory, f'Auto_Tijd' )
Autotijdmatrix = Routines.csvlezen ( Autotijdfilenaam, aantal_lege_regels=0 )
Fietstijdfilenaam = os.path.join ( Skimsdirectory, f'Fiets_Tijd' )
Fietstijdmatrix = Routines.csvlezen ( Fietstijdfilenaam, aantal_lege_regels=0 )
OVtijdfilenaam = os.path.join ( Skimsdirectory, f'OV_Tijd' )
OVtijdmatrix = Routines.csvlezen ( OVtijdfilenaam, aantal_lege_regels=0 )
Autoafstandfilenaam = os.path.join ( Skimsdirectory, f'Auto_Afstand' )
Autoafstandmatrix = Routines.csvlezen ( Autoafstandfilenaam, aantal_lege_regels=0 )
OVafstandfilenaam = os.path.join ( Skimsdirectory, f'OV_Afstand' )
OVafstandmatrix = Routines.csvlezen ( OVafstandfilenaam, aantal_lege_regels=0 )

Hub = 0
Hubset = []
while Hub > -1 :
    Hub = int (input('Geef de zone(s) met hub(s) één voor één aan. Als je de laatste hebt gehad, typ dan -1'))
    if Hub > 0 :
        Hubset.append(Hub-1)   #De nummering van een vector of matrix begint in Python bij kolom of rij 0
Hubsetnaam = input ('Geef de hubset een naam')

PplusRherkomsttijdmatrix = []
PplusRbestemmingstijdmatrix = []
PplusFietstijdmatrix = []
PplusRherkomstafstandOVmatrix = []
PplusRherkomstafstandautomatrix = []
PplusRbestemmingsafstandOVmatrix = []
PplusRbestemmingsafstandautomatrix = []
PplusFietsautoafstandmatrix = []
OverstaptijdOV = int(input('Hoeveel overstaptijd is er op de hub tussen auto en OV?'))
Overstaptijdfiets = int(input('Hoeveel overstaptijd is er op de hub tussen auto en fiets?'))
Pplusfietshubplek = []
PplusRhubplek = []



for h in range (len(Hubset)) :
    PplusRherkomsttijdmatrix.append([])
    PplusRbestemmingstijdmatrix.append([])
    PplusFietstijdmatrix.append([])
    PplusRherkomstafstandOVmatrix.append([])
    PplusRherkomstafstandautomatrix.append([])
    PplusRbestemmingsafstandOVmatrix.append([])
    PplusRbestemmingsafstandautomatrix.append([])
    PplusFietsautoafstandmatrix.append([])
    for i in range (len(Autotijdmatrix)) :
        PplusRbestemmingstijdmatrix[h].append([])
        PplusRherkomsttijdmatrix[h].append([])
        PplusFietstijdmatrix[h].append([])
        PplusFietsautoafstandmatrix[h].append ([])
        PplusRherkomstafstandOVmatrix[h].append([])
        PplusRherkomstafstandautomatrix[h].append([])
        PplusRbestemmingsafstandOVmatrix[h].append([])
        PplusRbestemmingsafstandautomatrix[h].append([])
        for j in range (len(Autotijdmatrix)) :
            if OVtijdmatrix [i][Hubset[h]] <= Autotijdmatrix [Hubset[h]][j]:
                PplusRbestemmingstijdmatrix[h][i].append(round(OVtijdmatrix[i][Hubset[h]] + Autotijdmatrix[Hubset[h]][j]
                                                               + OverstaptijdOV))
                PplusRbestemmingsafstandautomatrix[h][i].append(round(Autoafstandmatrix [Hubset[h]][j]))
                PplusRbestemmingsafstandOVmatrix[h][i].append(round(OVafstandmatrix [i][Hubset[h]]))
                PplusRherkomsttijdmatrix[h][i].append (round(Autotijdmatrix[i][Hubset[h]] + OVtijdmatrix[Hubset[h]][j]
                                                             + OverstaptijdOV))
                PplusRherkomstafstandautomatrix[h][i].append(round(Autoafstandmatrix [i][Hubset[h]]))
                PplusRherkomstafstandOVmatrix[h][i].append(round(OVafstandmatrix [Hubset[h]][j]))
            else:
                PplusRbestemmingstijdmatrix[h][i].append(round(Autotijdmatrix[i][Hubset[h]] + OVtijdmatrix[Hubset[h]][j]
                                                               + OverstaptijdOV))
                PplusRbestemmingsafstandautomatrix[h][i].append(round(Autoafstandmatrix [i][Hubset[h]]))
                PplusRbestemmingsafstandOVmatrix[h][i].append(round(OVafstandmatrix [Hubset[h]][j]))
                PplusRherkomsttijdmatrix[h][i].append (round(OVtijdmatrix[i][Hubset[h]] + Autotijdmatrix[Hubset[h]][j]
                                                             + OverstaptijdOV))
                PplusRherkomstafstandautomatrix[h][i].append(round(Autoafstandmatrix [Hubset[h]][j]))
                PplusRherkomstafstandOVmatrix[h][i].append(round(OVafstandmatrix [i][Hubset[h]]))
            if Fietstijdmatrix [i][Hubset[h]] <= Fietstijdmatrix [Hubset[h]][j]:
                PplusFietstijdmatrix[h][i].append (round( Fietstijdmatrix[i][Hubset[h]] + Autotijdmatrix[Hubset[h]][j]
                                                          + Overstaptijdfiets))
                PplusFietsautoafstandmatrix[h][i].append(round( Autoafstandmatrix[Hubset[h]][j]))
            else:
                PplusFietstijdmatrix[h][i].append (round( Fietstijdmatrix[j][Hubset[h]] + Autotijdmatrix[Hubset[h]][i]
                                                          + Overstaptijdfiets))
                PplusFietsautoafstandmatrix[h][i].append(round( Autoafstandmatrix[Hubset[h]][i]))

PplusRherkomsttijdtotaal = []
PplusRbestemmingstijdtotaal = []
PplusFietstijdtotaal = []
PplusRherkomstafstandOVtotaal = []
PplusRherkomstafstandautototaal = []
PplusRbestemmingsafstandOVtotaal = []
PplusRbestemmingsafstandautototaal = []
PplusFietsautoafstandtotaal = []
for i in range (len(Autotijdmatrix)) :
    PplusRherkomsttijdtotaal.append([])
    PplusRbestemmingstijdtotaal.append([])
    PplusFietstijdtotaal.append([])
    PplusRherkomstafstandOVtotaal.append([])
    PplusRherkomstafstandautototaal.append([])
    PplusRbestemmingsafstandOVtotaal.append([])
    PplusRbestemmingsafstandautototaal.append([])
    PplusFietsautoafstandtotaal.append([])
    Pplusfietshubplek.append([])
    PplusRhubplek.append ( [] )
    for j in range (len(Autotijdmatrix)):
        minimum = 9999
        for h in range (len(Hubset)):
            minimum = min (minimum,PplusRherkomsttijdmatrix[h][i][j])
        PplusRherkomsttijdtotaal[i].append (minimum)
        minimum = 9999
        minimumoud = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRbestemmingstijdmatrix[h][i][j])
            if minimum < minimumoud :
                hbewaar = h
                minimumoud = minimum
        PplusRhubplek[i].append ( Hubset[hbewaar] + 1 )
        PplusRbestemmingstijdtotaal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusFietstijdmatrix[h][i][j])
        PplusFietstijdtotaal[i].append ( minimum )
        minimum = 9999
        minimoud = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRherkomstafstandautomatrix[h][i][j])
            if minimum < minimumoud :
                hbewaar = h
                minimumoud = minimum
        Pplusfietshubplek[i].append ( Hubset[hbewaar] + 1 )
        PplusRherkomstafstandautototaal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRherkomstafstandOVmatrix[h][i][j])
        PplusRherkomstafstandOVtotaal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRbestemmingsafstandautomatrix[h][i][j])
        PplusRbestemmingsafstandautototaal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRbestemmingsafstandOVmatrix[h][i][j])
        PplusRbestemmingsafstandOVtotaal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusFietsautoafstandmatrix[h][i][j])
        PplusFietsautoafstandtotaal[i].append ( minimum )

PplusRbestemmingstijdfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_bestemmings_Tijd')
Routines.csvwegschrijven(PplusRbestemmingstijdtotaal,PplusRbestemmingstijdfilenaam)
PplusRbestemmingsafstandautofilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_bestemmings_Afstand_Auto')
Routines.csvwegschrijven(PplusRbestemmingsafstandautototaal,PplusRbestemmingsafstandautofilenaam)
PplusRbestemmingsafstandOVfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_bestemmings_Afstand_OV')
Routines.csvwegschrijven(PplusRbestemmingsafstandOVtotaal,PplusRbestemmingsafstandOVfilenaam)
PplusRherkomsttijdfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_herkomst_Tijd')
Routines.csvwegschrijven(PplusRherkomsttijdtotaal,PplusRherkomsttijdfilenaam)
PplusRherkomstafstandautofilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_herkomst_Afstand_Auto')
Routines.csvwegschrijven(PplusRherkomstafstandautototaal,PplusRherkomstafstandautofilenaam)
PplusRherkomstafstandOVfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_herkomst_Afstand_OV')
Routines.csvwegschrijven(PplusRherkomstafstandOVtotaal,PplusRherkomstafstandOVfilenaam)
Pplusfietstijdfilenaam = os.path.join(Skimsdirectory,f'Pplusfiets_{Hubsetnaam}_Tijd')
Routines.csvwegschrijven(PplusFietstijdtotaal,Pplusfietstijdfilenaam)
Pplusfietsautoafstandfilenaam = os.path.join(Skimsdirectory,f'Pplusfiets_{Hubsetnaam}_Afstand_Auto')
Routines.csvwegschrijven(PplusFietsautoafstandtotaal,Pplusfietsautoafstandfilenaam)
Pplusfietshubplekfilenaam = os.path.join(Skimsdirectory,f'Pplusfiets_{Hubsetnaam}_bestehubs')
Routines.csvwegschrijven(Pplusfietshubplek,Pplusfietshubplekfilenaam)
PplusRhubplekfilenaam = os.path.join(Skimsdirectory,f'PplusR_{Hubsetnaam}_bestehubs')
Routines.csvwegschrijven(PplusRhubplek,PplusRhubplekfilenaam)

