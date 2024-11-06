import csv
import os
from tkinter import *
from tkinter import filedialog

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

Omnummernaam = filedialog.askopenfilename(title='Selecteer de omnummer file')
Omnummernoncsv = Omnummernaam.replace('.csv', '')
Omnummertabel = Routines.csvintlezen(Omnummernoncsv, aantal_lege_regels=1)
print(Omnummernaam)
filelist = filedialog.askopenfilenames(
    title='Selecteer de lijst om te zetten matrices')
Jaren = ['2018', '2030H', '2040H', '2040L']
jr = '2018'
Doorgaan = True
while Doorgaan:
    for Matrixnaam in filelist:
        if 'ov_afstand' not in Matrixnaam:
            Matrixnaam = Matrixnaam.replace('2018', jr)
        print(Matrixnaam)
        Matrixnoncsv = Matrixnaam.replace('.csv', '')
        Matrixgewoon = Routines.csvintlezen(Matrixnoncsv)
        omnummermatrix = []
        print('lengte omnummertabel is', len(Omnummertabel))

        for i in range(len(Omnummertabel)):
            omnummermatrix.append([])
            for j in range(len(Omnummertabel)):
                if Omnummertabel[i][1] > len(
                        Matrixgewoon) or Omnummertabel[j][1] > len(Matrixgewoon):
                    omnummermatrix[i].append(9999)
                else:
                    omnummermatrix[i].append(
                        Matrixgewoon[Omnummertabel[i][1] - 1][Omnummertabel[j][1] - 1])

        if 'afstand' in Matrixnaam:
            aspect = 'Afstand'
            if 'auto' in Matrixnaam:
                Vwijze = 'Auto'
                for i in range(len(omnummermatrix)):
                    for j in range(len(omnummermatrix)):
                        omnummermatrix[i][j] = int(
                            round(omnummermatrix[i][j] / 1000, 0))
            elif 'ov' in Matrixnaam:
                Vwijze = 'OV'
            dagsoorten = {'Ochtendspits', 'Avondspits', 'Restdag'}
            for ds in dagsoorten:
                Bestemmingsdirectory = os.path.join(
                    Doeldirectory, jr, 'skims', ds)
                os.makedirs(Bestemmingsdirectory, exist_ok=True)
                fileout = os.path.join(
                    Bestemmingsdirectory, f'{Vwijze}_{aspect}')
                Routines.csvwegschrijven(omnummermatrix, fileout)
        else:
            aspect = 'Tijd'
            if 'auto' in Matrixnaam:
                Vwijze = 'Auto'
                if 'ochtendspits' in Matrixnaam:
                    Bestemmingsdirectory = os.path.join(
                        Doeldirectory, jr, 'skims', 'Ochtendspits')
                    os.makedirs(Bestemmingsdirectory, exist_ok=True)
                    fileout = os.path.join(
                        Bestemmingsdirectory, f'{Vwijze}_Tijd')
                    Routines.csvwegschrijven(omnummermatrix, fileout)

            elif 'fiets' in Matrixnaam:
                Vwijze = 'Fiets'
                if 'ochtendspits' in Matrixnaam:
                    dagsoorten = {'Ochtendspits', 'Restdag'}
                    for ds in dagsoorten:
                        Bestemmingsdirectory = os.path.join(
                            Doeldirectory, jr, 'skims', ds)
                        os.makedirs(Bestemmingsdirectory, exist_ok=True)
                        fileout = os.path.join(
                            Bestemmingsdirectory, f'{Vwijze}_Tijd')
                        Routines.csvwegschrijven(omnummermatrix, fileout)
            elif 'ov' in Matrixnaam:
                Vwijze = 'OV'
                if 'ochtendspits' in Matrixnaam:
                    dagsoorten = {'Ochtendspits', 'Restdag'}
                    for ds in dagsoorten:
                        Bestemmingsdirectory = os.path.join(
                            Doeldirectory, jr, 'skims', ds)
                        os.makedirs(Bestemmingsdirectory, exist_ok=True)
                        fileout = os.path.join(
                            Bestemmingsdirectory, f'{Vwijze}_Tijd')
                        Routines.csvwegschrijven(omnummermatrix, fileout)
            if 'avondspits' in Matrixnaam:
                ds = 'Avondspits'
                Bestemmingsdirectory = os.path.join(
                    Doeldirectory, jr, 'skims', ds)
                os.makedirs(Bestemmingsdirectory, exist_ok=True)
            elif 'freeflow' in Matrixnaam:
                ds = 'Restdag'
                Bestemmingsdirectory = os.path.join(
                    Doeldirectory, jr, 'skims', ds)
                os.makedirs(Bestemmingsdirectory, exist_ok=True)
            fileout = os.path.join(Bestemmingsdirectory, f'{Vwijze}_Tijd')
        Routines.csvwegschrijven(omnummermatrix, fileout)
    if jr != '2040L':
        jr = Jaren[Jaren.index(jr) + 1]
    else:
        Doorgaan = False
