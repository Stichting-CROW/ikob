import os
import ikob.utils as utils

from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()
Projectbestandsnaam = config['__filename__']  # nieuw automatisch toegevoegd config item.

# Haal (voor het gemak) onderdelen voor dit script er uit.
project_config = config['project']
paden_config = config['project']['paden']
skims_config = config['skims']
tvom_config = config['TVOM']

# Ophalen van instellingen
jaar = project_config['jaar']
Basisdirectory = paden_config['skims_directory']
Skimsdirectory = os.path.join (Basisdirectory, 'skims')
os.makedirs ( Skimsdirectory, exist_ok=True )
motieven = project_config['motieven']
Ketens = project_config['ketens']['gebruiken']
Hubnaam = project_config['ketens']['naam hub']
aspect = skims_config['aspect']
TVOMwerk = tvom_config['werk']
TVOMoverig = tvom_config['overig']
varautotarief = skims_config['varautotarief']
kmheffing = skims_config['kmheffing']
varkostenga = skims_config['varkostenga']
tijdkostenga = skims_config['tijdkostenga']
dagsoort = skims_config['dagsoort']
soortgeenauto = skims_config['soortgeenauto']
#benader_kosten = skims_config['OV kosten']['benaderen']['gebruiken']
OVkmtarief = skims_config['OV kosten']['kmkosten']
starttarief = skims_config['OV kosten']['starttarief']
Parkeerzoektijdfile = skims_config['parkeerzoektijden_bestand']
Additionele_kosten = skims_config['additionele_kosten']['gebruiken']
Additionele_kostenfile = skims_config['additionele_kosten']['bestand']
Parkeerkosten = skims_config['parkeerkosten']['gebruiken']
Parkeerkostenfile = skims_config['parkeerkosten']['bestand']


if Additionele_kosten:
    Additionele_kostenfile=Additionele_kostenfile.replace('.csv','')
    Additionele_kostenmatrix = utils.csvintlezen(Additionele_kostenfile , aantal_lege_regels=0)

# Vaste waarden
inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']

OVkmtarief = float(OVkmtarief)/100
starttarief = float(starttarief)/100
varautotarief = float(varautotarief)/100
Parkeerzoektijdfile=Parkeerzoektijdfile.replace('.csv','')
Parkeertijdlijst = utils.csvlezen (Parkeerzoektijdfile, aantal_lege_regels=1)
print (Projectbestandsnaam)
Projectdirectory = os.path.join (Basisdirectory, Projectbestandsnaam)
print (Projectdirectory)
os.makedirs ( Projectdirectory, exist_ok=True)
Ervarenreistijddirectory = os.path.join (Projectdirectory, 'ervarenreistijd')
print (Ervarenreistijddirectory)
os.makedirs ( Ervarenreistijddirectory, exist_ok=True )

def KostenOV(afstand, OVkmtarief, starttarief):
    flaf = float(afstand)
    if flaf <= 0:
        return 0
    else :
        return flaf * OVkmtarief + starttarief
    return 0

Jaardirectory = os.path.join (Ervarenreistijddirectory)
os.makedirs ( Jaardirectory, exist_ok=True )
print (Jaardirectory)
Jaarinvoerdirectory  = os.path.join (Skimsdirectory)
for ds in dagsoort:
    Invoerdirectory = os.path.join(Jaarinvoerdirectory, ds)
    Uitvoerdirectory = os.path.join (Jaardirectory, ds)
    os.makedirs(Uitvoerdirectory, exist_ok=True)
    print (Uitvoerdirectory)
    Autotijdfilenaam = os.path.join(Invoerdirectory, f'Auto_Tijd')
    Autotijdmatrix = utils.csvfloatlezen(Autotijdfilenaam, aantal_lege_regels=0)
    Autoafstandfilenaam = os.path.join(Invoerdirectory, f'Auto_Afstand')
    Autoafstandmatrix = utils.csvfloatlezen(Autoafstandfilenaam, aantal_lege_regels=0)
    Fietstijdfilenaam = os.path.join(Invoerdirectory, f'Fiets_Tijd')
    Fietstijdmatrix = utils.csvfloatlezen (Fietstijdfilenaam, aantal_lege_regels=0)
    OVtijdfilenaam = os.path.join(Invoerdirectory, f'OV_Tijd')
    OVtijdmatrix = utils.csvfloatlezen(OVtijdfilenaam, aantal_lege_regels=0)
    OVafstandfilenaam = os.path.join(Invoerdirectory, f'OV_Afstand')
    OVafstandmatrix = utils.csvfloatlezen(OVafstandfilenaam, aantal_lege_regels=0)
    if Parkeerkosten:
        Parkeerkostenfile = Parkeerkostenfile.replace ( '.csv', '' )
        Parkeerkostenlijst = utils.csvintlezen ( Parkeerkostenfile, aantal_lege_regels=0 )
    else:
        Parkeerkostenlijst = utils.lijstvolnullen ( len ( OVafstandmatrix ) )
    print ( Parkeerkostenlijst )

    if Ketens :
        Pplusfietstijdfilenaam = os.path.join(Invoerdirectory, f'Pplusfiets_{Hubnaam}_Tijd')
        Pplusfietstijdmatrix = utils.csvfloatlezen(Pplusfietstijdfilenaam, aantal_lege_regels=0)
        Pplusfietsafstandfilenaam = os.path.join(Invoerdirectory, f'Pplusfiets_{Hubnaam}_Afstand_Auto')
        Pplusfietsafstandmatrix = utils.csvfloatlezen(Pplusfietsafstandfilenaam, aantal_lege_regels=0)
        PplusRbestemmingstijdfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_bestemmings_Tijd')
        PplusRbestemmingstijdmatrix = utils.csvfloatlezen(PplusRbestemmingstijdfilenaam, aantal_lege_regels=0)
        PplusRherkomsttijdfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_herkomst_Tijd')
        PplusRherkomsttijdmatrix = utils.csvfloatlezen(PplusRherkomsttijdfilenaam, aantal_lege_regels=0)
        PplusRbestemmingsOVafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_bestemmings_Afstand_OV')
        PplusRbestemmingsOVafstandmatrix = utils.csvfloatlezen(PplusRbestemmingsOVafstandfilenaam, aantal_lege_regels=0)
        PplusRbestemmingsautoafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_bestemmings_Afstand_Auto')
        PplusRbestemmingsautoafstandmatrix = utils.csvfloatlezen(PplusRbestemmingsautoafstandfilenaam, aantal_lege_regels=0)
        PplusRherkomstOVafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_herkomst_Afstand_OV')
        PplusRherkomstOVafstandmatrix = utils.csvfloatlezen(PplusRherkomstOVafstandfilenaam, aantal_lege_regels=0)
        PplusRherkomstautoafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_herkomst_Afstand_Auto')
        PplusRherkomstautoafstandmatrix = utils.csvfloatlezen(PplusRherkomstautoafstandfilenaam, aantal_lege_regels=0)



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

    print("Bezig kosten berekenen.")
    afmeting = len (OVafstandmatrix)
    KostenmatrixOV =  [ [ KostenOV(OVafstandmatrix[i][j], OVkmtarief, starttarief,)
                            for j in range(afmeting) ]
                            for i in range(afmeting) ]
    if Ketens:
        KostenbestemmingsPplusROV = [ [ KostenOV(PplusRbestemmingsOVafstandmatrix[i][j], OVkmtarief, starttarief,)
                                for j in range(afmeting) ]
                                for i in range(afmeting) ]
        KostenherkomstPplusROV = [ [ KostenOV(PplusRherkomstOVafstandmatrix[i][j], OVkmtarief, starttarief,)
                                for j in range(afmeting) ]
                                for i in range(afmeting) ]

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
    utils.csvwegschrijven(GGRskim,Uitvoerfilenaam)

    for ink in inkomens:
        GGRskim = []
        Vermenigvuldigingsfactor = TVOMwerk.get(ink)
        for i in range (0,aantal_zones):
            GGRskim.append([])
            for j in range (0,aantal_zones):
                totaleTijd = Autotijdmatrix[i][j] + round(float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2]))
                if Additionele_kosten:
                    GGRskim[i].append ( int ( totaleTijd + Vermenigvuldigingsfactor * (Autoafstandmatrix[i][j] *
                                              (varautotarief + kmheffing) + Additionele_kostenmatrix[i][j]/100) +
                                              Parkeerkostenlijst[j]/100))
                else:
                    GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * (Autoafstandmatrix [i][j] *
                                      (varautotarief+kmheffing) + Parkeerkostenlijst[j]/100)))

        Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'Auto_{ink}')
        utils.csvwegschrijven(GGRskim, Uitvoerfilenaam)


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
        utils.csvwegschrijven(GGRskim,Uitvoerfilenaam)

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
                        totaleTijd = Autotijdmatrix[i][j] +round(float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2]))
                        totaleKosten = Autotijdmatrix[i][j] * tijdkostenga.get(sga) + \
                                       Autoafstandmatrix[i][j] * (varkostenga.get(sga) + kmheffing)
                        GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * totaleKosten))

            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'{sga}_{ink}')
            utils.csvwegschrijven(GGRskim, Uitvoerfilenaam)

        # Nu GratisAuto
        for ink in inkomens:
            GGRskim = []
            Vermenigvuldigingsfactor = TVOMwerk.get ( ink )
            for i in range ( 0, aantal_zones ):
                GGRskim.append ( [] )
                for j in range ( 0, aantal_zones ):
                    totaleTijd = Autotijdmatrix[i][j] + round(float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2]))
                    if Additionele_kosten:
                        GGRskim[i].append ( int ( totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] *
                                            kmheffing + Additionele_kostenmatrix[i][j]/100 +
                                              Parkeerkostenlijst[j]/100) )
                    else:
                        GGRskim[i].append ( int ( totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] *
                                                kmheffing + Parkeerkostenlijst[j]/100) )
            Uitvoerfilenaam = os.path.join ( Uitvoerdirectory, f'GratisAuto_{ink}' )
            utils.csvwegschrijven ( GGRskim, Uitvoerfilenaam )

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
        utils.csvwegschrijven(GGRskim,Uitvoerfilenaam)

        #Nu de ketens
        #Eerst P+Fiets
        if Ketens :
            for ink in inkomens:
                GGRskim = []
                Vermenigvuldigingsfactor = TVOMwerk.get ( ink )
                for i in range (0,aantal_zones):
                    GGRskim.append([])
                    for j in range (0,aantal_zones):
                        if Additionele_kosten:
                            GGRskim[i].append ( int ( Pplusfietstijdmatrix[i][j] + Vermenigvuldigingsfactor *
                                                      (Pplusfietsafstandmatrix[i][j] *
                                                      (varautotarief + kmheffing) + Additionele_kostenmatrix[i][j]/100)))
                        else:
                            GGRskim[i].append(int(Pplusfietstijdmatrix[i][j] + Vermenigvuldigingsfactor * Pplusfietsafstandmatrix [i][j] *
                                              varautotarief+kmheffing))

                Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f'Pplusfiets_{Hubnaam}_{ink}')
                utils.csvwegschrijven(GGRskim, Uitvoerfilenaam)

                # Dan P+R

                GGRskim = []

                for i in range ( 0, aantal_zones ):
                    GGRskim.append ( [] )
                    for j in range ( 0, aantal_zones ):
                        if Additionele_kosten:
                            GGRskim[i].append (
                                int ( PplusRbestemmingstijdmatrix[i][j] + Vermenigvuldigingsfactor *
                                      (PplusRbestemmingsautoafstandmatrix[i][j] * (varautotarief + kmheffing) +
                                         Additionele_kostenmatrix[i][j] / 100  + KostenbestemmingsPplusROV[i][j])))
                        else:
                            GGRskim[i].append (
                            int ( PplusRbestemmingstijdmatrix[i][j] + Vermenigvuldigingsfactor *
                                  (PplusRbestemmingsautoafstandmatrix[i][j] * (varautotarief + kmheffing) +
                                    KostenbestemmingsPplusROV[i][j] )))

                Uitvoerfilenaam = os.path.join ( Uitvoerdirectory, f'PplusRbestemmings_{Hubnaam}_{ink}' )
                utils.csvwegschrijven ( GGRskim, Uitvoerfilenaam )

                GGRskim = []

                for i in range ( 0, aantal_zones ):
                    GGRskim.append ( [] )
                    for j in range ( 0, aantal_zones ):
                        if Additionele_kosten:
                            GGRskim[i].append (
                                int ( PplusRherkomsttijdmatrix + Vermenigvuldigingsfactor *
                                      (PplusRherkomstautoafstandmatrix[i][j] * (varautotarief + kmheffing) +
                                         Additionele_kostenmatrix[i][j] / 100  + KostenherkomstPplusROV[i][j])))
                        else:
                            GGRskim[i].append (
                            int ( PplusRherkomsttijdmatrix[i][j] + Vermenigvuldigingsfactor *
                                  (PplusRherkomstautoafstandmatrix[i][j] * (varautotarief + kmheffing) +
                                    KostenherkomstPplusROV[i][j] )))

                Uitvoerfilenaam = os.path.join ( Uitvoerdirectory, f'PplusRherkomst_{Hubnaam}_{ink}' )
                utils.csvwegschrijven ( GGRskim, Uitvoerfilenaam )
