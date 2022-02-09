import os
import Routines
import Berekeningen

from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()

# Haal (voor het gemak) onderdelen voor dit script er uit.
project_config = config['project']
paden_config = config['project']['paden']
skims_config = config['skims']
tvom_config = config['tvom']

# Ophalen van instellingen
jaar = project_config['jaar']
Skimsdirectory = paden_config['skims_directory']
motieven = skims_config['motieven']
aspect = skims_config['aspect']
TVOMwerk = tvom_config['TVOMwerk']
TVOMoverig = tvom_config['TVOMoverig']
varautotarief = skims_config['varautotarief']
kmheffing = skims_config['kmheffing']
varkostenga = skims_config['varkostenga']
tijdkostenga = skims_config['tijdkostenga']
dagsoort = skims_config['dagsoort']
soortgeenauto = skims_config['soortgeenauto']
benader_kosten = skims_config['OV Kosten']['benaderen']['gebruiken']
kmtarief = skims_config['OV Kosten']['benaderen']['kmkosten']
starttarief = skims_config['OV Kosten']['benaderen']['starttarief']
Parkeerzoektijdfile = skims_config['parkeerzoektijden_bestand']


# Vaste waarden
inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']

kmtarief = float(kmtarief)/100
starttarief = float(starttarief)/100
varautotarief = float(varautotarief)/100
Parkeerzoektijdfile=Parkeerzoektijdfile.replace('.csv','')
Parkeertijdlijst = Routines.csvintlezen (Parkeerzoektijdfile, aantal_lege_regels=1)
Ervarenreistijddirectory = Skimsdirectory.replace ('skims', 'Ervarenreistijd')
os.makedirs ( Ervarenreistijddirectory, exist_ok=True )

def KostenOV(afstand, kmtarief, starttarief):
    flaf = float(afstand)
    if flaf <= 0:
        return 0
    else :
        return flaf * kmtarief + starttarief
    return 0

Jaardirectory = os.path.join (Ervarenreistijddirectory, jaar)
os.makedirs ( Jaardirectory, exist_ok=True )
print (Jaardirectory)
Jaarinvoerdirectory  = os.path.join (Skimsdirectory, jaar)
for ds in dagsoort:
    Invoerdirectory = os.path.join(Jaarinvoerdirectory, ds)
    Uitvoerdirectory = os.path.join (Jaardirectory, ds)
    os.makedirs(Uitvoerdirectory, exist_ok=True)
    print (Uitvoerdirectory)
    Autotijdfilenaam = os.path.join(Invoerdirectory, f'Auto_Tijd')
    Autotijdmatrix = Routines.csvfloatlezen(Autotijdfilenaam, aantal_lege_regels=0)
    Autoafstandfilenaam = os.path.join(Invoerdirectory, f'Auto_Afstand')
    Autoafstandmatrix = Routines.csvfloatlezen(Autoafstandfilenaam, aantal_lege_regels=0)
    Fietstijdfilenaam = os.path.join(Invoerdirectory, f'Fiets_Tijd')
    Fietstijdmatrix = Routines.csvfloatlezen (Fietstijdfilenaam, aantal_lege_regels=0)
    OVtijdfilenaam = os.path.join(Invoerdirectory, f'OV_Tijd')
    OVtijdmatrix = Routines.csvfloatlezen(OVtijdfilenaam, aantal_lege_regels=0)
    OVafstandfilenaam = os.path.join(Invoerdirectory, f'OV_Afstand')
    OVafstandmatrix = Routines.csvfloatlezen(OVafstandfilenaam, aantal_lege_regels=0)

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

    if benader_kosten:
        print("Bezig kosten berekenen.")
        afmeting = len (OVafstandmatrix)
        KostenmatrixOV =  [ [ KostenOV(OVafstandmatrix[i][j], kmtarief, starttarief,)
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

    for ink in inkomens:
        GGRskim = []
        Vermenigvuldigingsfactor = TVOMwerk.get(ink)
        for i in range (0,aantal_zones):
            GGRskim.append([])
            for j in range (0,aantal_zones):
                totaleTijd = Autotijdmatrix[i][j] + Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2]
                GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix [i][j] *
                                      (varautotarief+kmheffing)))

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
        for ink in inkomens:
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
