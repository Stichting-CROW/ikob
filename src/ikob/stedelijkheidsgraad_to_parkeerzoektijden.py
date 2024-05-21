import csv
import os
import Routines
from tkinter import filedialog


def inlezenfile(filenaam, aantal_lege_regels=0):
    uitvoerlijst = []
    with open(filenaam, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for i in range(aantal_lege_regels):
            next(reader)
        for row in reader:
            uitvoerlijst.append(row)
    for i in range(len(uitvoerlijst)):
        for j in range(len(uitvoerlijst[0])):
            Tussenstring = uitvoerlijst[i][j].replace(",", ".")
            Tussenstring = Tussenstring.replace("ï»¿", "")
            uitvoerlijst[i][j] = int(float(Tussenstring))
    print(uitvoerlijst)
    return uitvoerlijst


SGfile = filedialog.askopenfilename(title="Selecteer de Stedelijkheidsfile")
SGfile = SGfile.replace(".csv", "")
SGlijst = Routines.csvintlezen(SGfile)
header = ["Zone", "AankomstZT", "VertrekZT"]
Parkeerzoektijdenlijst = []
Parkeerzoektijdenlijst.append(header)
for i in range(len(SGlijst)):
    Omzetting = {1: 12, 2: 8, 3: 4, 4: 0, 5: 0}
    Aankomsttijd = Omzetting.get(SGlijst[i])
    print(Aankomsttijd)
    Parkeerzoektijdenlijst.append(
        [i + 1, Omzetting.get(SGlijst[i]), int(round(Aankomsttijd / 4))]
    )
Parkeeruitvoerfile = SGfile.replace("Stedelijkheidsgraad", "Parkeerzoektijd")
print(Parkeeruitvoerfile)
fileout = os.path.join(f"{Parkeeruitvoerfile}")
Routines.csvwegschrijven(Parkeerzoektijdenlijst, fileout)
