import csv
import Routines
import pathlib
import sys
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
    return uitvoerlijst


def stedelijkheid_to_parkeerzoektijden(infile: pathlib.Path, outfile: pathlib.Path):
    SGlijst = Routines.csvintlezen(infile)
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
    print(outfile)
    Routines.csvwegschrijven(Parkeerzoektijdenlijst, outfile)


# TODO: Remove script interface once conversion is embedded within GUI.
if __name__ == "__main__":
    if len(sys.argv) == 1:
        infile = filedialog.askopenfilename(title="Selecteer de Stedelijkheidsfile")
        infile = infile.replace(".csv", "")
    else:
        infile = sys.argv[1]

    infile = pathlib.Path(infile)
    outfile = pathlib.Path(infile.parent / "Parkeerzoektijd")
    stedelijkheid_to_parkeerzoektijden(infile, outfile)
