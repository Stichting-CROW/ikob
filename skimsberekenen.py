import os
import Routines
import Berekeningen

from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()

# Haal (voor het gemak) de twee onderdelen voor dit script er uit.
paden_config = config['project']['paden']
skims_config = config['skims']

# Ophalen van instellingen
Skimsdirectory = paden_config['invoer_skims_directory']
motieven = skims_config['motieven']
aspect = skims_config['aspect']
inkomen = skims_config['inkomen']
TVOMwerk = skims_config['TVOMwerk']
TVOMoverig = skims_config['TVOMoverig']
varkosten = skims_config['varkosten']
kmheffing = skims_config['kmheffing']
varkostenga = skims_config['varkostenga']
tijdkostenga = skims_config['tijdkostenga']
dagsoort = skims_config['dagsoort']
soortgeenauto = skims_config['soortgeenauto']


def KostenOV(afstand):
    """
    Kosten OV per KM:
       0 - 10 km = 0.30  Euro
      11 - 20 km = 0.25  Euro
      21 - 30 km = 0.225 Euro
      30+     km = 0.20  Euro
    """
    # EM: ^^^ Deze info klopt niet met de formule?
    flaf = float(afstand)
    if flaf > 0:
        return flaf * 0.121 + 0.75
    return 0


for ds in dagsoort:
    Autotijdfilenaam = os.path.join(Skimsdirectory, 'skims', ds, 'Auto_Tijd')
    Autotijdmatrix = Routines.csvfloatlezen(Autotijdfilenaam, aantal_lege_regels=4)
    Autoafstandfilenaam = os.path.join(Skimsdirectory, 'skims', ds, 'Auto_Afstand')
    Autoafstandmatrix = Routines.csvfloatlezen(Autoafstandfilenaam, aantal_lege_regels=4)
    Fietstijdfilenaam = os.path.join(Skimsdirectory, 'skims', ds, 'Fiets_Tijd')
    Fietstijdmatrix = Routines.csvfloatlezen (Fietstijdfilenaam, aantal_lege_regels=4)
    OVtijdfilenaam = os.path.join(Skimsdirectory, 'skims', ds, 'OV_Tijd')
    OVtijdmatrix = Routines.csvfloatlezen(OVtijdfilenaam, aantal_lege_regels=4)
    OVafstandfilenaam = os.path.join(Skimsdirectory, 'skims', ds, 'OV_Afstand')
    OVafstandmatrix = Routines.csvfloatlezen(OVafstandfilenaam, aantal_lege_regels=4)
    
    Parkeertijdfilenaam = os.path.join(Skimsdirectory, 'skims', ds, 'Parkeerzoektijd')
    ParkeertijdLijst = Routines.csvfloatlezen(Parkeertijdfilenaam, aantal_lege_regels=1)
    print("Parkeertijden bevat {} zones.".format(len(ParkeertijdLijst)))
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

    Uitvoerdirectory = os.path.join(Skimsdirectory, 'Ervarenreistijd', ds)
    os.makedirs(Uitvoerdirectory, exist_ok=True)
    Uitvoerfilenaam = os.path.join(Uitvoerdirectory, 'Fiets')
    Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)

    # Nu de rest
    # Eerst de auto
    for motief in motieven:
        for ink in inkomen:
            GGRskim = []
            if motief == 'werk':
                Vermenigvuldigingsfactor = TVOMwerk.get(ink)
            if motief == 'overig':
                Vermenigvuldigingsfactor = TVOMoverig.get(ink)
            for i in range (0,aantal_zones):
                GGRskim.append([])
                for j in range (0,aantal_zones):
                    totaleTijd = Autotijdmatrix[i][j] + ParkeertijdLijst[i][1] + ParkeertijdLijst[j][2]
                    GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix [i][j] *
                                          (varkosten+kmheffing)))

            Uitvoerdirectory = os.path.join(Skimsdirectory, 'Ervarenreistijd', ds)
            os.makedirs(Uitvoerdirectory, exist_ok=True)
            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'Auto_{motief}_{ink}')
            Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)
            

            #Dan het OV
            GGRskim = []
            if motief == 'werk':
                Vermenigvuldigingsfactor = TVOMwerk.get (ink)
            if motief == 'overig':
                Vermenigvuldigingsfactor = TVOMoverig.get (ink)
            for i in range (0, aantal_zones):
                GGRskim.append([])
                for j in range (0, aantal_zones):
                    if float(OVtijdmatrix[i][j])>0.5:
                        Resultaat = float(OVtijdmatrix [i][j]) + Vermenigvuldigingsfactor * float(KostenmatrixOV [i][j])
                        Resultaatint = int (Resultaat)
                        GGRskim[i].append(Resultaatint)
                    else:
                        GGRskim[i].append(9999)

            Uitvoerdirectory = os.path.join(Skimsdirectory, 'Ervarenreistijd', ds)
            os.makedirs(Uitvoerdirectory, exist_ok=True)
            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'OV_{motief}_{ink}')
            Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)

            #Dan geen auto (rijbewijs)
            for sga in soortgeenauto :
                GGRskim = []
                if motief == 'werk':
                    Vermenigvuldigingsfactor = TVOMwerk.get(ink)
                if motief == 'overig':
                    Vermenigvuldigingsfactor = TVOMoverig.get(ink)
                for i in range (0,aantal_zones):
                    GGRskim.append([])
                    for j in range (0,aantal_zones):
                        if Autotijdmatrix[i][j] < 7:
                            GGRskim[i].append(99999)
                        else:
                            totaleTijd = Autotijdmatrix[i][j] + ParkeertijdLijst[i][1] + ParkeertijdLijst[j][2]
                            totaleKosten = Autotijdmatrix[i][j] * tijdkostenga.get(sga) + \
                                           Autoafstandmatrix[i][j] * (varkostenga.get(sga) + kmheffing)
                            GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * totaleKosten))

                Uitvoerdirectory = os.path.join(Skimsdirectory, 'Ervarenreistijd', ds)
                os.makedirs(Uitvoerdirectory, exist_ok=True)
                Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'{sga}_{motief}_{ink}')
                Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)

    # Nu GratisAuto
    for motief in motieven:
        for ink in inkomen:
            GGRskim = []
            if motief == 'werk':
                Vermenigvuldigingsfactor = TVOMwerk.get ( ink )
            if motief == 'overig':
                Vermenigvuldigingsfactor = TVOMoverig.get ( ink )
            for i in range ( 0, aantal_zones ):
                GGRskim.append ( [] )
                for j in range ( 0, aantal_zones ):
                    totaleTijd = Autotijdmatrix[i][j] + ParkeertijdLijst[i][1] + ParkeertijdLijst[j][2]
                    GGRskim[i].append ( int ( totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] *
                                              (kmheffing) ) )

            Uitvoerdirectory = os.path.join ( Skimsdirectory, 'Ervarenreistijd', ds )
            os.makedirs ( Uitvoerdirectory, exist_ok=True )
            Uitvoerfilenaam = os.path.join ( Uitvoerdirectory, f'GratisAuto_{motief}_{ink}' )
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

    Uitvoerdirectory = os.path.join(Skimsdirectory, 'Ervarenreistijd', ds)
    os.makedirs(Uitvoerdirectory, exist_ok=True)
    Uitvoerfilenaam = os.path.join(Uitvoerdirectory, 'GratisOV')
    Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)
