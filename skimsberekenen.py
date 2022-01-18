import os
import Routines
import Berekeningen
from tkinter import filedialog
from tkinter import *

skims = Tk()
skims.geometry = ("10x10")
skims.label = ("Voer de directory waar de pure reistijdskims en afstandskims staan in")
skims.directory =  filedialog.askdirectory (initialdir = os.getcwd(),title = "Selecteer de directory skimsdirectory",)
skims.destroy()
Skimsdirectory = skims.directory + '/'
Ervarenreistijddirectory = Skimsdirectory.replace ('skims', 'Ervarenreistijd')
os.makedirs ( Ervarenreistijddirectory, exist_ok=True )

parkeerzoektijd = Tk()
parkeerzoektijd.geometry = ("10x10")
parkeerzoektijd.label = ("Voer de invoerfile in")
parkeerzoektijd.file = filedialog.askopenfilename(initialdir=os.getcwd(),title="Selecteer de file met de parkeerzoektijdtabel",)
parkeerzoektijd.destroy()
Parkeerzoektijdfile = parkeerzoektijd.file
Parkeerzoektijdfile=Parkeerzoektijdfile.replace('.csv','')
Parkeertijdlijst = Routines.csvintlezen (Parkeerzoektijdfile, aantal_lege_regels=1)


#motieven = ['werk']
aspect = ['Tijd', 'Kosten']
inkomen = ['hoog', 'middelhoog', 'middellaag', 'laag']
TVOMwerk = {'hoog':4, 'middelhoog':6, 'middellaag':9, 'laag':12}
TVOMoverig = {'hoog':4.8 , 'middelhoog': 7.25, 'middellaag': 10.9, 'laag':15.5}
varkosten = 0.16
kmheffing = 0
varkostenga = {'GeenAuto' : 0.33, 'GeenRijbewijs' : 2.40}
tijdkostenga = {'GeenAuto' : 0.01, 'GeenRijbewijs' : 0.40}
dagsoort = ['Restdag']
soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
jaar = ['2040A2']

def KostenOV(afstand):
    """
    Kosten OV per KM:
       0 - 10 km = 0.30  Euro
      11 - 20 km = 0.25  Euro
      21 - 30 km = 0.225 Euro
      30+     km = 0.20  Euro
    """
    flaf = float(afstand)
    if flaf <= 0:
        return 0
    else :
        return flaf * 0.121 + 0.75
    return 0

for jr in jaar:
    Jaardirectory = os.path.join (Ervarenreistijddirectory, jr)
    os.makedirs ( Jaardirectory, exist_ok=True )
    print (Jaardirectory)
    Jaarinvoerdirectory  = os.path.join (Skimsdirectory, jr)
    for ds in dagsoort:
        Invoerdirectory = os.path.join(Jaarinvoerdirectory, ds)
        Uitvoerdirectory = os.path.join (Jaardirectory, ds)
        os.makedirs(Uitvoerdirectory, exist_ok=True)
        print (Uitvoerdirectory)
        Autotijdfilenaam = os.path.join(Invoerdirectory, f'Auto_Tijd')
        Autotijdmatrix = Routines.csvfloatlezen(Autotijdfilenaam, aantal_lege_regels=4)
        Autoafstandfilenaam = os.path.join(Invoerdirectory, f'Auto_Afstand')
        Autoafstandmatrix = Routines.csvfloatlezen(Autoafstandfilenaam, aantal_lege_regels=4)
        Fietstijdfilenaam = os.path.join(Invoerdirectory, f'Fiets_Tijd')
        Fietstijdmatrix = Routines.csvfloatlezen (Fietstijdfilenaam, aantal_lege_regels=4)
        OVtijdfilenaam = os.path.join(Invoerdirectory, f'OV_Tijd')
        OVtijdmatrix = Routines.csvfloatlezen(OVtijdfilenaam, aantal_lege_regels=4)
        OVafstandfilenaam = os.path.join(Invoerdirectory, f'OV_Afstand')
        OVafstandmatrix = Routines.csvfloatlezen(OVafstandfilenaam, aantal_lege_regels=4)

        print("Parkeertijden bevat {} zones.".format(len(Parkeertijdlijst)))
        aantal_zones_tijd = len(Autotijdmatrix)
        print("Autotijdmatrix bevat {} zones.".format(aantal_zones_tijd))
        aantal_zones_afstand = len(Autoafstandmatrix)
        print("Auto-afstandmatrix bevat {} zones.".format(aantal_zones_afstand))
        if aantal_zones_afstand != aantal_zones_tijd:
            print("FOUT: Aantal zones niet gelijk!?")
            quit()
        aantal_zones = aantal_zones_tijd

        #kostenmatrix
        benader_kosten = True

        if benader_kosten:
            print("Bezig kosten berekenen.")
            afmeting = len (OVafstandmatrix)
            KostenmatrixOV =  [ [ KostenOV(OVafstandmatrix[i][j])
                                for j in range(afmeting) ]
                                for i in range(afmeting) ]
        else:
            KostenfilenaamOV = os.path.join(Skimsdirectory, 'skims', ds, 'OV_Kosten')
            print("Bezig lezen '{}'.".format(KostenfilenaamOV))
            KostenmatrixOV = Routines.csvfloatlezen(KostenfilenaamOV, aantal_lege_regels=4)

        # Eerst de fiets:

        GGRskim = []
        aantal_zones_fiets = len (Fietstijdmatrix)
        for i in range (0,aantal_zones_fiets):
            GGRskim.append([])
            for j in range (0,aantal_zones_fiets):
                if Fietstijdmatrix[i][j]<180:
                    GGRskim[i].append(int(Fietstijdmatrix [i][j]))
                else:
                    GGRskim[i].append(9999)
            for j in range (aantal_zones_fiets, aantal_zones) :
                GGRskim[i].append ( 9999 )
        for i in range (aantal_zones_fiets, aantal_zones):
            GGRskim.append([])
            for j in range (0,aantal_zones) :
                GGRskim[i].append(9999)


        Uitvoerfilenaam = os.path.join(Uitvoerdirectory, 'Fiets')
        Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)

        for ink in inkomen:
            GGRskim = []
            Vermenigvuldigingsfactor = TVOMwerk.get(ink)
            for i in range (0,aantal_zones):
                GGRskim.append([])
                for j in range (0,aantal_zones):
                    totaleTijd = Autotijdmatrix[i][j] + Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2]
                    GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix [i][j] *
                                          (varkosten+kmheffing)))

            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'Auto_{ink}')
            Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)


            #Dan het OV
            GGRskim = []
            Vermenigvuldigingsfactor = TVOMwerk.get (ink)
            for i in range (0, aantal_zones):
                GGRskim.append([])
                for j in range (0, aantal_zones):
                    if float(OVtijdmatrix[i][j])>0.5:
                        Resultaat = float(OVtijdmatrix [i][j]) + Vermenigvuldigingsfactor * float(KostenmatrixOV [i][j])
                        Resultaatint = int (Resultaat)
                        GGRskim[i].append(Resultaatint)
                    else:
                        GGRskim[i].append(9999)

            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'OV_{ink}')
            Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)

            #Dan geen auto (rijbewijs)
            for sga in soortgeenauto :
                GGRskim = []
                Vermenigvuldigingsfactor = TVOMwerk.get(ink)
                for i in range (0,aantal_zones):
                    GGRskim.append([])
                    for j in range (0,aantal_zones):
                        if Autotijdmatrix[i][j] < 7:
                            GGRskim[i].append(99999)
                        else:
                            totaleTijd = Autotijdmatrix[i][j] + Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2]
                            totaleKosten = Autotijdmatrix[i][j] * tijdkostenga.get(sga) + \
                                           Autoafstandmatrix[i][j] * (varkostenga.get(sga) + kmheffing)
                            GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * totaleKosten))

                Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'{sga}_{ink}')
                Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)

            # Nu GratisAuto
            for ink in inkomen:
                GGRskim = []
                Vermenigvuldigingsfactor = TVOMwerk.get ( ink )
                for i in range ( 0, aantal_zones ):
                    GGRskim.append ( [] )
                    for j in range ( 0, aantal_zones ):
                        totaleTijd = Autotijdmatrix[i][j] + Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2]
                        GGRskim[i].append ( int ( totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] *
                                                  (kmheffing) ) )

                Uitvoerfilenaam = os.path.join ( Uitvoerdirectory, f'GratisAuto_{ink}' )
                Routines.csvwegschrijven ( GGRskim, Uitvoerfilenaam )

            #Nu GratisOV
            GGRskim = []
            for i in range (0,aantal_zones):
                GGRskim.append([])
                for j in range (0,aantal_zones):
                    if OVtijdmatrix[i][j]>0.5:
                        GGRskim[i].append(int(OVtijdmatrix [i][j]))
                    else:
                        GGRskim[i].append(9999)

            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, 'GratisOV')
            Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)
