import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import Routines


def inlezenfile(filenaam, aantal_lege_regels=0):
    uitvoerlijst = []
    with open(filenaam, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for i in range(aantal_lege_regels):
            next(reader)
        for row in reader:
            uitvoerlijst.append(row)
    for i in range(len(uitvoerlijst)):
        for j in range(len(uitvoerlijst[0])):
            Tussenstring = uitvoerlijst[i][j].replace(",", ".")
            uitvoerlijst[i][j] = int(float(Tussenstring))
    return uitvoerlijst


global _lastDir
_lastDir = os.getcwd()
initpath = _lastDir
Doeldirectory = filedialog.askdirectory(
    initialdir=initpath,
    title='Naar welke directory moet de uitvoer?')


print(Doeldirectory)

filelist = filedialog.askopenfilenames(title='Selecteer de HB_lijst')

for HBnaam in filelist:
    hblijst = inlezenfile(HBnaam)

    NRMmatrix = []
    herkomst = 1
    NRMmatrix.append([])
    counter = 1
    for i in range(len(hblijst)):
        if i == len(hblijst) - 1 and hblijst[i][0] != hblijst[i][1]:
            NRMmatrix[herkomst - 1].append(0)
        else:
            if hblijst[i][0] == herkomst:
                if hblijst[i][1] == counter:
                    NRMmatrix[herkomst - 1].append(hblijst[i][2])
                else:
                    while counter < hblijst[i][1]:
                        if counter == hblijst[i][0]:
                            NRMmatrix[herkomst - 1].append(0)
                        else:
                            NRMmatrix[herkomst - 1].append(999999)
                        # print (fn)
                        # print ('herkomst is', herkomst)
                        counter += 1
                    NRMmatrix[herkomst - 1].append(hblijst[i][2])
                counter += 1
            else:
                herkomst += 1
                NRMmatrix.append([])
                counter = 1
                if hblijst[i][1] == counter:
                    NRMmatrix[herkomst - 1].append(hblijst[i][2])
                else:
                    while counter < hblijst[i][1]:
                        if counter == hblijst[i][0]:
                            NRMmatrix[herkomst - 1].append(0)
                        else:
                            NRMmatrix[herkomst - 1].append(999999)
                        # print (fn)
                        # print ('herkomst is', herkomst)
                        counter += 1
                    NRMmatrix[herkomst - 1].append(hblijst[i][2])
                counter += 1

    matrix = []

    filename = HBnaam.replace('.csv', 'matrix')
    fileout = os.path.join(f'{filename}')
    Routines.csvwegschrijven(NRMmatrix, fileout)
