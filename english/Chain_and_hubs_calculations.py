import Routines
from tkinter import filedialog
from tkinter import *
import os
skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Choose the directory with the travel times and distances")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Select the skimsdirectory",)
Skimsdirectory = skims.directory + '/'
CarTimefilename = os.path.join ( Skimsdirectory, f'Car_Time' )
CarTimematrix = Routines.csvlezen ( CarTimefilename, aantal_lege_regels=0 )
BikeTimefilename = os.path.join ( Skimsdirectory, f'Bike_Time' )
BikeTimematrix = Routines.csvlezen ( BikeTimefilename, aantal_lege_regels=0 )
TransitTimefilename = os.path.join ( Skimsdirectory, f'Transit_Time' )
TransitTimematrix = Routines.csvlezen ( TransitTimefilename, aantal_lege_regels=0 )
CarDistancefilename = os.path.join ( Skimsdirectory, f'Car_Distance' )
CarDistancematrix = Routines.csvlezen ( CarDistancefilename, aantal_lege_regels=0 )
TransitDistancefilename = os.path.join ( Skimsdirectory, f'Transit_Distance' )
TransitDistancematrix = Routines.csvlezen ( TransitDistancefilename, aantal_lege_regels=0 )

Hub = 0
Hubset = []
while Hub > -1 :
    Hub = int (input('Enter the zone numbers one by one, finish with -1'))
    if Hub > 0 :
        Hubset.append(Hub-1)   #De nummering van een vector of matrix begint in Python bij kolom of rij 0
Hubsetname = input ('Enter de set of hubs a name')

PplusRoriginTimematrix = []
PplusRdestinationTimematrix = []
PplusBikeTimematrix = []
PplusRoriginDistanceTransitmatrix = []
PplusRoriginDistanceCarmatrix = []
PplusRdestinationDistanceTransitmatrix = []
PplusRdestinationDistanceCarmatrix = []
PplusBikeCarDistancematrix = []
TransiterstapTimeTransit = int(input('What is the time to switch from Car to Transit?'))
TransiterstapTimeBike = int(input('What is the time to switch from Car to Bike?'))
PplusBikehubspot = []
PplusRhubspot = []



for h in range (len(Hubset)) :
    PplusRoriginTimematrix.append([])
    PplusRdestinationTimematrix.append([])
    PplusBikeTimematrix.append([])
    PplusRoriginDistanceTransitmatrix.append([])
    PplusRoriginDistanceCarmatrix.append([])
    PplusRdestinationDistanceTransitmatrix.append([])
    PplusRdestinationDistanceCarmatrix.append([])
    PplusBikeCarDistancematrix.append([])
    for i in range (len(CarTimematrix)) :
        PplusRdestinationTimematrix[h].append([])
        PplusRoriginTimematrix[h].append([])
        PplusBikeTimematrix[h].append([])
        PplusBikeCarDistancematrix[h].append ([])
        PplusRoriginDistanceTransitmatrix[h].append([])
        PplusRoriginDistanceCarmatrix[h].append([])
        PplusRdestinationDistanceTransitmatrix[h].append([])
        PplusRdestinationDistanceCarmatrix[h].append([])
        for j in range (len(CarTimematrix)) :
            if TransitTimematrix [i][Hubset[h]] <= CarTimematrix [Hubset[h]][j]:
                PplusRdestinationTimematrix[h][i].append(round(TransitTimematrix[i][Hubset[h]] + CarTimematrix[Hubset[h]][j]
                                                               + TransiterstapTimeTransit))
                PplusRdestinationDistanceCarmatrix[h][i].append(round(CarDistancematrix [Hubset[h]][j]))
                PplusRdestinationDistanceTransitmatrix[h][i].append(round(TransitDistancematrix [i][Hubset[h]]))
                PplusRoriginTimematrix[h][i].append (round(CarTimematrix[i][Hubset[h]] + TransitTimematrix[Hubset[h]][j]
                                                             + TransiterstapTimeTransit))
                PplusRoriginDistanceCarmatrix[h][i].append(round(CarDistancematrix [i][Hubset[h]]))
                PplusRoriginDistanceTransitmatrix[h][i].append(round(TransitDistancematrix [Hubset[h]][j]))
            else:
                PplusRdestinationTimematrix[h][i].append(round(CarTimematrix[i][Hubset[h]] + TransitTimematrix[Hubset[h]][j]
                                                               + TransiterstapTimeTransit))
                PplusRdestinationDistanceCarmatrix[h][i].append(round(CarDistancematrix [i][Hubset[h]]))
                PplusRdestinationDistanceTransitmatrix[h][i].append(round(TransitDistancematrix [Hubset[h]][j]))
                PplusRoriginTimematrix[h][i].append (round(TransitTimematrix[i][Hubset[h]] + CarTimematrix[Hubset[h]][j]
                                                             + TransiterstapTimeTransit))
                PplusRoriginDistanceCarmatrix[h][i].append(round(CarDistancematrix [Hubset[h]][j]))
                PplusRoriginDistanceTransitmatrix[h][i].append(round(TransitDistancematrix [i][Hubset[h]]))
            if BikeTimematrix [i][Hubset[h]] <= BikeTimematrix [Hubset[h]][j]:
                PplusBikeTimematrix[h][i].append (round( BikeTimematrix[i][Hubset[h]] + CarTimematrix[Hubset[h]][j]
                                                          + TransiterstapTimeBike))
                PplusBikeCarDistancematrix[h][i].append(round( CarDistancematrix[Hubset[h]][j]))
            else:
                PplusBikeTimematrix[h][i].append (round( BikeTimematrix[j][Hubset[h]] + CarTimematrix[Hubset[h]][i]
                                                          + TransiterstapTimeBike))
                PplusBikeCarDistancematrix[h][i].append(round( CarDistancematrix[Hubset[h]][i]))

PplusRoriginTimetotal = []
PplusRdestinationTimetotal = []
PplusBikeTimetotal = []
PplusRoriginDistanceTransittotal = []
PplusRoriginDistanceCartotal = []
PplusRdestinationDistanceTransittotal = []
PplusRdestinationDistanceCartotal = []
PplusBikeCarDistancetotal = []
for i in range (len(CarTimematrix)) :
    PplusRoriginTimetotal.append([])
    PplusRdestinationTimetotal.append([])
    PplusBikeTimetotal.append([])
    PplusRoriginDistanceTransittotal.append([])
    PplusRoriginDistanceCartotal.append([])
    PplusRdestinationDistanceTransittotal.append([])
    PplusRdestinationDistanceCartotal.append([])
    PplusBikeCarDistancetotal.append([])
    PplusBikehubspot.append([])
    PplusRhubspot.append ( [] )
    for j in range (len(CarTimematrix)):
        minimum = 9999
        for h in range (len(Hubset)):
            minimum = min (minimum,PplusRoriginTimematrix[h][i][j])
        PplusRoriginTimetotal[i].append (minimum)
        minimum = 9999
        minimumoud = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRdestinationTimematrix[h][i][j])
            if minimum < minimumoud :
                hbewaar = h
                minimumoud = minimum
        PplusRhubspot[i].append ( Hubset[hbewaar] + 1 )
        PplusRdestinationTimetotal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusBikeTimematrix[h][i][j])
        PplusBikeTimetotal[i].append ( minimum )
        minimum =9999
        minimoud = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRoriginDistanceCarmatrix[h][i][j])
            if minimum < minimumoud :
                hbewaar = h
                minimumoud = minimum
        PplusBikehubspot[i].append ( Hubset[hbewaar] + 1 )
        PplusRoriginDistanceCartotal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRoriginDistanceTransitmatrix[h][i][j])
        PplusRoriginDistanceTransittotal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRdestinationDistanceCarmatrix[h][i][j])
        PplusRdestinationDistanceCartotal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusRdestinationDistanceTransitmatrix[h][i][j])
        PplusRdestinationDistanceTransittotal[i].append ( minimum )
        minimum = 9999
        for h in range ( len ( Hubset ) ):
            minimum = min ( minimum, PplusBikeCarDistancematrix[h][i][j])
        PplusBikeCarDistancetotal[i].append ( minimum )

Hubsdirectory = os.path.join ( Skimsdirectory, Hubsetname )
os.makedirs ( Hubsdirectory, exist_ok=True )
PplusRdestinationTimefilename = os.path.join(Hubsdirectory, f'PlusR_dest_Time')
Routines.csvwegschrijven(PplusRdestinationTimetotal,PplusRdestinationTimefilename)
PplusRdestinationDistanceCarfilename = os.path.join(Hubsdirectory, f'PlusR_dest_Distance_Car')
Routines.csvwegschrijven(PplusRdestinationDistanceCartotal,PplusRdestinationDistanceCarfilename)
PplusRdestinationDistanceTransitfilename = os.path.join(Hubsdirectory, f'PlusR_dest_Distance_Transit')
Routines.csvwegschrijven(PplusRdestinationDistanceTransittotal,PplusRdestinationDistanceTransitfilename)
PplusRoriginTimefilename = os.path.join(Hubsdirectory, f'PlusR_origin_Time')
Routines.csvwegschrijven(PplusRoriginTimetotal,PplusRoriginTimefilename)
PplusRoriginDistanceCarfilename = os.path.join(Hubsdirectory, f'PlusR_origin_Distance_Car')
Routines.csvwegschrijven(PplusRoriginDistanceCartotal,PplusRoriginDistanceCarfilename)
PplusRoriginDistanceTransitfilename = os.path.join(Hubsdirectory, f'PlusR_origin_Distance_Transit')
Routines.csvwegschrijven(PplusRoriginDistanceTransittotal,PplusRoriginDistanceTransitfilename)
PplusBikeTimefilename = os.path.join(Skimsdirectory,Hubsetname, f'PlusBike_Time')
Routines.csvwegschrijven(PplusBikeTimetotal,PplusBikeTimefilename)
PplusBikeCarDistancefilename = os.path.join(Skimsdirectory,Hubsetname, f'PlusBike_Distance_Car')
Routines.csvwegschrijven(PplusBikeCarDistancetotal,PplusBikeCarDistancefilename)
PplusBikehubspotfilename = os.path.join(Skimsdirectory,Hubsetname, f'PlusBike_besthubs')
Routines.csvwegschrijven(PplusBikehubspot,PplusBikehubspotfilename)
PplusRhubspotfilename = os.path.join(Skimsdirectory,Hubsetname, f'PlusR_besthubs')
Routines.csvwegschrijven(PplusRhubspot,PplusRhubspotfilename)
skims.destroy()
