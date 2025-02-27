import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import Routines

stationsfilenaam = filedialog.askopenfilename(title='Selecteer de stationfile')

print(stationsfilenaam)
lijst = []
hblijst = []
aantal_lege_regels = 0
with open(stationsfilenaam, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for i in range(aantal_lege_regels):
        next(reader)
    teller = 0
    for row in reader:
        lijst.append(row)
        hblijst.append([])
        for i in range(0, 2):
            hblijst[teller].append(int(lijst[teller][i]))
        hblijst[teller].append(int(float(lijst[teller][11])))
        teller += 1
print(hblijst)

stationsmatrix = Routines.matrixvolnullen(812, 812)
for i in range(len(hblijst)):
    stationsmatrix[hblijst[i][0] - 1][hblijst[i][1] - 1] = hblijst[i][2]
print(stationsmatrix)

accessfilenaam = filedialog.askopenfilename(title='Selecteer de accessfile')

print(accessfilenaam)
lijst = []
acclijst = []
aantal_lege_regels = 0
with open(accessfilenaam, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for i in range(aantal_lege_regels):
        next(reader)
    teller = 0
    for row in reader:
        lijn = row[0]
        lijn2 = lijn.split()
        lijst.append(lijn2)
        acclijst.append([])
        for i in range(0, 2):
            acclijst[teller].append(int(lijst[teller][i]))
        if float(lijst[teller][8]) > 0:
            acclijst[teller].append(int(float(lijst[teller][8])))
        else:
            acclijst[teller].append(int(float(lijst[teller][17])))
        teller += 1
print(acclijst)

egressfilenaam = filedialog.askopenfilename(title='Selecteer de stationfile')

print(egressfilenaam)
lijst = []
egrlijst = []
aantal_lege_regels = 0
with open(egressfilenaam, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for i in range(aantal_lege_regels):
        next(reader)
    teller = 0
    for row in reader:
        lijn = row[0]
        lijn2 = lijn.split()
        lijst.append(lijn2)
        egrlijst.append([])
        for i in range(0, 2):
            egrlijst[teller].append(int(lijst[teller][i]))
        if float(lijst[teller][8]) > 0:
            egrlijst[teller].append(int(float(lijst[teller][8])))
        else:
            egrlijst[teller].append(int(float(lijst[teller][17])))
        teller += 1
print(egrlijst)

aanrijmatrix = Routines.matrixvol99999(2838, 812)
for i in range(len(hblijst)):
    aanrijmatrix[egrlijst[i][0] - 1][egrlijst[i][1] - 1] = egrlijst[i][2]
    print(egrlijst[i][2])


bereikbare_stations = []
for i in range(len(egrlijst)):
    bereikbare_stations.append([])
    for j in range(len(egrlijst[0])):
        if egrlijst[i][j] < 99999:
            bereikbare_stations[i].append(j)


afstandentabel = []
for i in range(len(egrlijst)):
    afstandentabel.append([])
    for j in range(len(egrlijst)):
        if j != i:
            minimum = 99999
            for vertrekstation in bereikbare_stations[i]:
                for aankomststation in bereikbare_stations[j]:
                    print('j is:', j, 'aankomstation is', aankomststation)
                    kladafstand = aanrijmatrix[i][aankomststation] + \
                        stationsmatrix[aankomststation][vertrekstation] + aanrijmatrix[j][vertrekstation]
                    if kladafstand < minimum:
                        minimum = kladafstand
            afstandentabel[i].append(minimum)
print(afstandentabel)
