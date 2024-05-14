import logging
import Routines

logger = logging.getLogger(__name__)


def ervaren_reistijd_berekenen(config, datasource):
    # Haal (voor het gemak) onderdelen voor dit script er uit.
    project_config = config['project']
    skims_config = config['skims']
    tvom_config = config['TVOM']
    verdeling_config = config['verdeling']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    scenario = project_config['verstedelijkingsscenario']
    motieven = project_config['motieven']
    Ketens = project_config['ketens']['gebruiken']
    Hubnaam = project_config['ketens']['naam hub']
    OV_Kostenbestand = skims_config ['OV kostenbestand']['gebruiken']
    logger.debug("OV_Kostenbestand: %s", OV_Kostenbestand)
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
    OVkmtarief = skims_config['OV kosten']['kmkosten']
    starttarief = skims_config['OV kosten']['starttarief']
    Additionele_kosten = verdeling_config['additionele_kosten']['gebruiken']
    Parkeerkosten = verdeling_config['parkeerkosten']['gebruiken']
    Parkeerkostenfile = verdeling_config['parkeerkosten']['bestand']
    Pricecap = skims_config['pricecap']['gebruiken']
    Pricecapgetal = skims_config['pricecap']['getal']

    if Additionele_kosten:
        Additionele_kostenmatrix = datasource.config_lezen('additionele_kosten')

    # Vaste waarden
    inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']

    OVkmtarief = float(OVkmtarief/100)
    starttarief = float(starttarief/100)
    varfossiel = float(varfossiel/100)
    varelektrisch = float(varelektrisch/100)
    kmheffingfossiel = float (kmheffingfossiel/100)
    kmheffingelektrisch = float (kmheffingelelektrisch/100)
    Parkeertijdlijst = datasource.config_lezen('parkeerzoektijden_bestand')
    soortbrandstof = ['fossiel', 'elektrisch']
    if 'orrectie' in regime:
        motief=motieven[0]
        if '65+' in regime:
            Correctiefactoren = datasource.segs_lezen(f"Correctiefactoren_{motief}_65plus", scenario=scenario)
        else:
            Correctiefactoren = datasource.segs_lezen(f"Correctiefactoren_{motief}", scenario=scenario)
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
        logger.debug("TVOM: %s", TVOM)
        for ds in dagsoort:
            Autotijdmatrix = datasource.skims_lezen('Auto_Tijd', ds)
            Autoafstandmatrix = datasource.skims_lezen('Auto_Afstand', ds)
            Fietstijdmatrix = datasource.skims_lezen('Fiets_Tijd', ds)
            OVtijdmatrix = datasource.skims_lezen('OV_Tijd', ds)
            OVafstandmatrix = datasource.skims_lezen('OV_Afstand', ds)
            if Parkeerkosten:
                raise NotImplementedError("Needs to be replaced with datasource reading...")
                Parkeerkostenfile = Parkeerkostenfile.replace ( '.csv', '' )
                Parkeerkostenlijst = Routines.csvintlezen ( Parkeerkostenfile, aantal_lege_regels=0 )
            else:
                Parkeerkostenlijst = Routines.lijstvolnullen ( len ( OVafstandmatrix ) )
            logger.debug("Parkeerkostenlijst = %s", Parkeerkostenlijst)

            if Ketens :
                Pplusfietstijdmatrix = datasource.skims_lezen(f'Pplusfiets_{Hubnaam}_Tijd', ds)
                Pplusfietsafstandmatrix = datasource.skims_lezen(f'Pplusfiets_{Hubnaam}_Afstand_Auto', ds)
                PplusRbestemmingstijdmatrix = datasource.skims_lezen(f'PplusR_{Hubnaam}_bestemmings_Tijd', ds)
                PplusRherkomsttijdmatrix = datasource.skims_lezen(f'PplusR_{Hubnaam}_herkomst_Tijd', ds)
                PplusRbestemmingsOVafstandmatrix = datasource.skims_lezen(f'PplusR_{Hubnaam}_bestemmings_Afstand_OV', ds)
                PplusRbestemmingsautoafstandmatrix = datasource.skims_lezen(f'PplusR_{Hubnaam}_bestemmings_Afstand_Auto', ds)
                PplusRherkomstOVafstandmatrix = datasource.skims_lezen(f'PplusR_{Hubnaam}_herkomst_Afstand_OV', ds)
                PplusRherkomstautoafstandmatrix = datasource.skims_lezen(f'PplusR_{Hubnaam}_herkomst_Afstand_Auto', ds)

            logger.debug("Parkeertijden bevat %d zones.", len(Parkeertijdlijst))
            aantal_zones_tijd = len(Autotijdmatrix)
            logger.debug("Autotijdmatrix bevat %d zones.", aantal_zones_tijd)
            aantal_zones_afstand = len(Autoafstandmatrix)
            logger.debug("Auto-afstandmatrix bevat %d zones.", aantal_zones_afstand)
            if aantal_zones_afstand != aantal_zones_tijd:
                logger.debug("FOUT: Aantal zones niet gelijk!?")
                quit()
            aantal_zones = aantal_zones_tijd

            #kostenmatrix
            if OV_Kostenbestand:
                KostenmatrixOV = datasource.skims_lezen("OV_Kosten", ds)
            else:
                logger.debug("Bezig kosten berekenen.")
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
                    logger.debug("KostenmatrixOV[%d][%d]=%f", i, j, KostenmatrixOV[i][j])
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

            datasource.write_csv(GGRskim, 'Ervarenreistijd', 'Fiets', ds, regime=regime, mot=mot, soort='matrix')

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
        
                    datasource.write_csv(GGRskim, 'Ervarenreistijd', f"Auto_{srtbr}", ds, ink=ink, regime=regime, mot=mot, soort='matrix')


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

                datasource.write_csv(GGRskim, 'Ervarenreistijd', 'OV', ds, ink=ink, regime=regime, mot=mot, soort='matrix')

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

                    datasource.write_csv(GGRskim, 'Ervarenreistijd', f'{sga}', ds, ink=ink, regime=regime, mot=mot, soort='matrix')

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
                    datasource.write_csv(GGRskim, 'Ervarenreistijd', 'GratisAuto', ds, ink=ink, regime=regime, mot=mot, soort='matrix')

                #Nu GratisOV
                GGRskim = []
                for i in range (0,aantal_zones):
                    GGRskim.append([])
                    for j in range (0,aantal_zones):
                        if OVtijdmatrix[i][j]>0.5:
                            GGRskim[i].append(int(OVtijdmatrix [i][j]))
                        else:
                            GGRskim[i].append(9999)

                datasource.write_csv(GGRskim, 'Ervarenreistijd', 'GratisOV', ds, regime=regime, mot=mot, soort='matrix')

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

                        datasource.write_csv(GGRskim, 'Ervarenreistijd', 'Pplusfiets', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot, soort='matrix')

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

                        datasource.write_csv(GGRskim, 'Ervarenreistijd', 'PplusRbestemmings', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot, soort='matrix')

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

                        datasource.write_csv(GGRskim, 'Ervarenreistijd', 'PplusRherkomst', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot, soort='matrix')
