import os
import Routines


def ervaren_reistijd_berekenen(config):
    Projectbestandsnaam = config['__filename__']  # nieuw automatisch toegevoegd config item.

    # Haal (voor het gemak) onderdelen voor dit script er uit.
    project_config = config['project']
    paden_config = config['project']['paden']
    skims_config = config['skims']
    tvom_config = config['TVOM']
    verdeling_config = config['verdeling']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    Basisdirectory = paden_config['skims_directory']
    Skimsdirectory = os.path.join (Basisdirectory, 'skims')
    os.makedirs ( Skimsdirectory, exist_ok=True )
    SEGSdirectory = paden_config['segs_directory']
    print (Skimsdirectory)
    scenario = project_config['verstedelijkingsscenario']
    motieven = project_config['motieven']
    Ketens = project_config['ketens']['gebruiken']
    Hubnaam = project_config['ketens']['naam hub']
    OV_Kostenbestand = skims_config ['OV kostenbestand']['gebruiken']
    print(OV_Kostenbestand)
    TVOMwerk = tvom_config['werk']
    TVOMoverig = tvom_config['overig']
    varfossiel = skims_config['Kosten auto fossiele brandstof']['variabele kosten']
    kmheffingfossiel = skims_config['Kosten auto fossiele brandstof']['kmheffing']
    varelektrisch = skims_config['Kosten elektrische auto']['variabele kosten']
    kmheffingelelektrisch = skims_config['Kosten elektrische auto']['kmheffing']
    varkostenga = skims_config['varkostenga']
    tijdkostenga = skims_config['tijdkostenga']
    dagsoort = skims_config['dagsoort']
    soortgeenauto = ['GeenAuto','GeenRijbewijs']
    #benader_kosten = skims_config['OV kosten']['benaderen']['gebruiken']
    OVkmtarief = skims_config['OV kosten']['kmkosten']
    starttarief = skims_config['OV kosten']['starttarief']
    Parkeerzoektijdfile = skims_config['parkeerzoektijden_bestand']
    Additionele_kosten = verdeling_config['additionele_kosten']['gebruiken']
    Additionele_kostenfile = verdeling_config['additionele_kosten']['bestand']
    Parkeerkosten = verdeling_config['parkeerkosten']['gebruiken']
    Parkeerkostenfile = verdeling_config['parkeerkosten']['bestand']
    Pricecap = skims_config['pricecap']['gebruiken']
    Pricecapgetal = skims_config['pricecap']['getal']

    if Additionele_kosten:
        Additionele_kostenfile=Additionele_kostenfile.replace('.csv','')
        Additionele_kostenmatrix = Routines.csvintlezen(Additionele_kostenfile , aantal_lege_regels=0)

    # Vaste waarden
    inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']

    OVkmtarief = float(OVkmtarief/100)
    starttarief = float(starttarief/100)
    varfossiel = float(varfossiel/100)
    varelektrisch = float(varelektrisch/100)
    kmheffingfossiel = float (kmheffingfossiel/100)
    kmheffingelektrisch = float (kmheffingelelektrisch/100)
    Parkeerzoektijdfile=Parkeerzoektijdfile.replace('.csv','')
    Parkeertijdlijst = Routines.csvlezen (Parkeerzoektijdfile, aantal_lege_regels=1)
    print (Projectbestandsnaam)
    Projectdirectory = os.path.join (Basisdirectory, Projectbestandsnaam)
    print (Projectdirectory)
    os.makedirs ( Projectdirectory, exist_ok=True)
    soortbrandstof = ['fossiel', 'elektrisch']
    if 'orrectie' in regime:
        motief=motieven[0]
        if '65+' in regime:
            Correctiefile=os.path.join(SEGSdirectory, scenario, f'Correctiefactoren_{motief}_65plus')
        else:
            Correctiefile=os.path.join(SEGSdirectory, scenario, f'Correctiefactoren_{motief}')
        Correctiefactoren = Routines.csvlezen(Correctiefile, aantal_lege_regels=1)
    else:
        Correctiefactoren = []
        for i in range(len(Parkeertijdlijst)):
            Correctiefactoren.append([1,1,1,1])
    def KostenOV(afstand, OVkmtarief, starttarief, Pricecap, Pricecapgetal):
        flaf = float(afstand)
        if flaf < 0:
            return 0
        else :
            if Pricecap:
                 if flaf * OVkmtarief + starttarief > Pricecapgetal:
                     return Pricecapgetal
            return flaf * OVkmtarief + starttarief
        return 0

    for mot in motieven:
        TVOM = TVOMwerk if mot == 'werk' else TVOMoverig
        print (TVOM)
        for ds in dagsoort:
            Invoerdirectory = os.path.join(Skimsdirectory, ds)
            Ervarenreistijddirectory = os.path.join(Basisdirectory, regime, mot, 'Ervarenreistijd', ds)
            print(Ervarenreistijddirectory)
            os.makedirs(Ervarenreistijddirectory, exist_ok=True)
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
            if Parkeerkosten:
                Parkeerkostenfile = Parkeerkostenfile.replace ( '.csv', '' )
                Parkeerkostenlijst = Routines.csvintlezen ( Parkeerkostenfile, aantal_lege_regels=0 )
            else:
                Parkeerkostenlijst = Routines.lijstvolnullen ( len ( OVafstandmatrix ) )
            print ( Parkeerkostenlijst )

            if Ketens :
                Pplusfietstijdfilenaam = os.path.join(Invoerdirectory, f'Pplusfiets_{Hubnaam}_Tijd')
                Pplusfietstijdmatrix = Routines.csvfloatlezen(Pplusfietstijdfilenaam, aantal_lege_regels=0)
                Pplusfietsafstandfilenaam = os.path.join(Invoerdirectory, f'Pplusfiets_{Hubnaam}_Afstand_Auto')
                Pplusfietsafstandmatrix = Routines.csvfloatlezen(Pplusfietsafstandfilenaam, aantal_lege_regels=0)
                PplusRbestemmingstijdfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_bestemmings_Tijd')
                PplusRbestemmingstijdmatrix = Routines.csvfloatlezen(PplusRbestemmingstijdfilenaam, aantal_lege_regels=0)
                PplusRherkomsttijdfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_herkomst_Tijd')
                PplusRherkomsttijdmatrix = Routines.csvfloatlezen(PplusRherkomsttijdfilenaam, aantal_lege_regels=0)
                PplusRbestemmingsOVafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_bestemmings_Afstand_OV')
                PplusRbestemmingsOVafstandmatrix = Routines.csvfloatlezen(PplusRbestemmingsOVafstandfilenaam, aantal_lege_regels=0)
                PplusRbestemmingsautoafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_bestemmings_Afstand_Auto')
                PplusRbestemmingsautoafstandmatrix = Routines.csvfloatlezen(PplusRbestemmingsautoafstandfilenaam, aantal_lege_regels=0)
                PplusRherkomstOVafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_herkomst_Afstand_OV')
                PplusRherkomstOVafstandmatrix = Routines.csvfloatlezen(PplusRherkomstOVafstandfilenaam, aantal_lege_regels=0)
                PplusRherkomstautoafstandfilenaam = os.path.join(Invoerdirectory, f'PplusR_{Hubnaam}_herkomst_Afstand_Auto')
                PplusRherkomstautoafstandmatrix = Routines.csvfloatlezen(PplusRherkomstautoafstandfilenaam, aantal_lege_regels=0)



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
            if OV_Kostenbestand:
                OVKostenbestandsnaam=os.path.join(Skimsdirectory,ds, f'OV_Kosten')
                print (OVKostenbestandsnaam)
                KostenmatrixOV=Routines.csvlezen(OVKostenbestandsnaam)
            else:
                print("Bezig kosten berekenen.")
                afmeting = len (OVafstandmatrix)
                KostenmatrixOV =  [ [ KostenOV(OVafstandmatrix[i][j], OVkmtarief, starttarief,Pricecap,Pricecapgetal,)
                                        for j in range(afmeting) ]
                                        for i in range(afmeting) ]
            if Ketens:
                KostenbestemmingsPplusROV = [ [ KostenOV(PplusRbestemmingsOVafstandmatrix[i][j], OVkmtarief, starttarief,Pricecap,Pricecapgetal,)
                                        for j in range(afmeting) ]
                                        for i in range(afmeting) ]
                KostenherkomstPplusROV = [ [ KostenOV(PplusRherkomstOVafstandmatrix[i][j], OVkmtarief, starttarief,)
                                        for j in range(afmeting) ]
                                        for i in range(afmeting) ]
            for i in range (0,10):
                for j in range (0,10):
                    print(KostenmatrixOV[i][j])
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


            Uitvoerfilenaam = os.path.join(Ervarenreistijddirectory, 'Fiets')
            Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)
            for ink in inkomens:
                for srtbr in soortbrandstof:
                    if srtbr == 'fossiel':
                        varautotarief = varfossiel
                        kmheffing = kmheffingfossiel
                    else:
                        varautotarief = varelektrisch
                        kmheffing = kmheffingelektrisch
                    GGRskim = []
                    Vermenigvuldigingsfactor = TVOM.get(ink)
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
                                                  Correctiefactoren[i][inkomens.index(ink)] *
                                                   (varautotarief+kmheffing) + Parkeerkostenlijst[j]/100)))
        
                    Uitvoerfilenaam = os.path.join(Ervarenreistijddirectory, f'Auto_{srtbr}_{ink}')
                    Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)


                #Dan het OV
                GGRskim = []
                Vermenigvuldigingsfactor = TVOM.get (ink)
                for i in range (0, aantal_zones):
                    GGRskim.append([])
                    for j in range (0, aantal_zones):
                        if float(OVtijdmatrix[i][j])>0.5:
                            Resultaat = float(OVtijdmatrix [i][j]) + Vermenigvuldigingsfactor * float(KostenmatrixOV [i][j])
                            Resultaatint = int (Resultaat)
                            GGRskim[i].append(Resultaatint)
                        else:
                            GGRskim[i].append(9999)

                Uitvoerfilenaam = os.path.join(Ervarenreistijddirectory, f'OV_{ink}')
                Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)

                #Dan geen auto (rijbewijs)
                for sga in soortgeenauto :
                    GGRskim = []
                    Vermenigvuldigingsfactor = TVOM.get(ink)
                    for i in range (0,aantal_zones):
                        GGRskim.append([])
                        for j in range (0,aantal_zones):
                            if Autotijdmatrix[i][j] < 7:
                                GGRskim[i].append(99999)
                            else:
                                totaleTijd = Autotijdmatrix[i][j] +round(float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2]))
                                totaleKosten = Autotijdmatrix[i][j] * tijdkostenga.get(sga) + \
                                               Correctiefactoren[i][inkomens.index(ink)] * Autoafstandmatrix[i][j] * (varkostenga.get(sga) + kmheffing)
                                GGRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * totaleKosten))

                    Uitvoerfilenaam = os.path.join(Ervarenreistijddirectory, f'{sga}_{ink}')
                    Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)

                # Nu GratisAuto
                for ink in inkomens:
                    GGRskim = []
                    Vermenigvuldigingsfactor = TVOM.get ( ink )
                    for i in range ( 0, aantal_zones ):
                        GGRskim.append ( [] )
                        for j in range ( 0, aantal_zones ):
                            totaleTijd = Autotijdmatrix[i][j] + round(float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2]))
                            if Additionele_kosten:
                                GGRskim[i].append ( int ( totaleTijd + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] *
                                                    kmheffing + Additionele_kostenmatrix[i][j]/100 +
                                                      Parkeerkostenlijst[j]/100) )
                            else:
                                GGRskim[i].append ( int ( totaleTijd + Correctiefactoren[i][inkomens.index(ink)] *
                                                          Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] *
                                                        kmheffing + Parkeerkostenlijst[j]/100) )
                    Uitvoerfilenaam = os.path.join ( Ervarenreistijddirectory, f'GratisAuto_{ink}' )
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

                Uitvoerfilenaam = os.path.join(Ervarenreistijddirectory, 'GratisOV')
                Routines.csvwegschrijven(GGRskim,Uitvoerfilenaam)

                #Nu de ketens
                #Eerst P+Fiets
                if Ketens :
                    for ink in inkomens:
                        GGRskim = []
                        Vermenigvuldigingsfactor = TVOM.get ( ink )
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

                        Uitvoerfilenaam = os.path.join(Ervarenreistijddirectory, f'Pplusfiets_{Hubnaam}_{ink}')
                        Routines.csvwegschrijven(GGRskim, Uitvoerfilenaam)

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

                        Uitvoerfilenaam = os.path.join ( Ervarenreistijddirectory, f'PplusRbestemmings_{Hubnaam}_{ink}' )
                        Routines.csvwegschrijven ( GGRskim, Uitvoerfilenaam )

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

                        Uitvoerfilenaam = os.path.join ( Ervarenreistijddirectory, f'PplusRherkomst_{Hubnaam}_{ink}' )
                        Routines.csvwegschrijven ( GGRskim, Uitvoerfilenaam )
