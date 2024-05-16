import logging
import ikob.Routines as Routines
import numpy as np
from ikob.datasource import DataSource

logger = logging.getLogger(__name__)


def KostenOV(afstand, OVkmtarief, starttarief, Pricecap, Pricecapgetal):
    if afstand < 0:
        return 0

    if Pricecap:
        if afstand * OVkmtarief + starttarief > Pricecapgetal:
            return Pricecapgetal

    return afstand * OVkmtarief + starttarief


def ervaren_reistijd_berekenen(config, datasource: DataSource):
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
        Additionele_kostenmatrix = datasource.read_config('skims', 'additionele_kosten')

    # Vaste waarden
    inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']

    OVkmtarief = float(OVkmtarief/100)
    starttarief = float(starttarief/100)
    varfossiel = float(varfossiel/100)
    varelektrisch = float(varelektrisch/100)
    kmheffingfossiel = float (kmheffingfossiel/100)
    kmheffingelektrisch = float (kmheffingelelektrisch/100)
    Parkeertijdlijst = datasource.read_config('skims', 'parkeerzoektijden_bestand')
    soortbrandstof = ['fossiel', 'elektrisch']
    if 'orrectie' in regime:
        motief=motieven[0]
        if '65+' in regime:
            Correctiefactoren = datasource.read_segs(f"Correctiefactoren_{motief}_65plus", scenario=scenario)
        else:
            Correctiefactoren = datasource.read_segs(f"Correctiefactoren_{motief}", scenario=scenario)
    else:
        Correctiefactoren = []
        for i in range(len(Parkeertijdlijst)):
            Correctiefactoren.append([1,1,1,1])

    for mot in motieven:
        TVOM = TVOMwerk if mot == 'werk' else TVOMoverig
        logger.debug("TVOM: %s", TVOM)
        for ds in dagsoort:
            Autotijdmatrix = datasource.read_skims('Auto_Tijd', ds)
            Autoafstandmatrix = datasource.read_skims('Auto_Afstand', ds)
            Fietstijdmatrix = datasource.read_skims('Fiets_Tijd', ds)
            OVtijdmatrix = datasource.read_skims('OV_Tijd', ds)
            OVafstandmatrix = datasource.read_skims('OV_Afstand', ds)
            if Parkeerkosten:
                raise NotImplementedError("Needs to be replaced with datasource reading...")
                Parkeerkostenfile = Parkeerkostenfile.replace ( '.csv', '' )
                Parkeerkostenlijst = Routines.csvintlezen ( Parkeerkostenfile, aantal_lege_regels=0 )
            else:
                Parkeerkostenlijst = Routines.lijstvolnullen ( len ( OVafstandmatrix ) )
            logger.debug("Parkeerkostenlijst = %s", Parkeerkostenlijst)

            if Ketens :
                Pplusfietstijdmatrix = datasource.read_skims(f'Pplusfiets_{Hubnaam}_Tijd', ds)
                Pplusfietsafstandmatrix = datasource.read_skims(f'Pplusfiets_{Hubnaam}_Afstand_Auto', ds)
                PplusRbestemmingstijdmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_bestemmings_Tijd', ds)
                PplusRherkomsttijdmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_herkomst_Tijd', ds)
                PplusRbestemmingsOVafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_bestemmings_Afstand_OV', ds)
                PplusRbestemmingsautoafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_bestemmings_Afstand_Auto', ds)
                PplusRherkomstOVafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_herkomst_Afstand_OV', ds)
                PplusRherkomstautoafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_herkomst_Afstand_Auto', ds)

            logger.debug("Parkeertijden bevat %d zones.", len(Parkeertijdlijst))
            aantal_zones_tijd = len(Autotijdmatrix)
            logger.debug("Autotijdmatrix bevat %d zones.", aantal_zones_tijd)
            aantal_zones_afstand = len(Autoafstandmatrix)
            logger.debug("Auto-afstandmatrix bevat %d zones.", aantal_zones_afstand)
            if aantal_zones_afstand != aantal_zones_tijd:
                logger.debug("FOUT: Aantal zones niet gelijk!?")
                quit()
            aantal_zones = aantal_zones_tijd

            afmeting = len(OVafstandmatrix)

            # kostenmatrix
            if OV_Kostenbestand:
                KostenmatrixOV = datasource.read_skims("OV_Kosten", ds)
            else:
                logger.debug("Bezig kosten berekenen.")
                KostenmatrixOV = np.zeros((afmeting, afmeting))
                for i in range(afmeting):
                    for j in range(afmeting):
                        KostenmatrixOV[i][j] = KostenOV(OVafstandmatrix[i][j], OVkmtarief, starttarief, Pricecap, Pricecapgetal)
                KostenmatrixOV = KostenmatrixOV.tolist()

            if Ketens:
                KostenbestemmingsPplusROV = np.zeros((afmeting, afmeting))
                KostenherkomstPplusROV = np.zeros((afmeting, afmeting))
                for i in range(afmeting):
                    for j in range(afmeting):
                        KostenbestemmingsPplusROV[i][j] = KostenOV(PplusRbestemmingsOVafstandmatrix[i][j], OVkmtarief, starttarief, Pricecap, Pricecapgetal)
                        KostenherkomstPplusROV[i][j] = KostenOV(PplusRherkomstOVafstandmatrix[i][j], OVkmtarief, starttarief)
                KostenbestemmingsPplusROV = KostenbestemmingsPplusROV.tolist()
                KostenherkomstPplusROV = KostenherkomstPplusROV.tolist()

            for i in range(afmeting):
                for j in range(afmeting):
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

            datasource.write_csv(GGRskim, 'Ervarenreistijd', 'Fiets', ds, regime=regime, mot=mot)

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
        
                    datasource.write_csv(GGRskim, 'Ervarenreistijd', f"Auto_{srtbr}", ds, ink=ink, regime=regime, mot=mot)


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

                datasource.write_csv(GGRskim, 'Ervarenreistijd', 'OV', ds, ink=ink, regime=regime, mot=mot)

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

                    datasource.write_csv(GGRskim, 'Ervarenreistijd', f'{sga}', ds, ink=ink, regime=regime, mot=mot)

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
                    datasource.write_csv(GGRskim, 'Ervarenreistijd', 'GratisAuto', ds, ink=ink, regime=regime, mot=mot)

                #Nu GratisOV
                GGRskim = []
                for i in range (0,aantal_zones):
                    GGRskim.append([])
                    for j in range (0,aantal_zones):
                        if OVtijdmatrix[i][j]>0.5:
                            GGRskim[i].append(int(OVtijdmatrix [i][j]))
                        else:
                            GGRskim[i].append(9999)

                datasource.write_csv(GGRskim, 'Ervarenreistijd', 'GratisOV', ds, regime=regime, mot=mot)

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

                        datasource.write_csv(GGRskim, 'Ervarenreistijd', 'Pplusfiets', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot)

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

                        datasource.write_csv(GGRskim, 'Ervarenreistijd', 'PplusRbestemmings', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot)

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

                        datasource.write_csv(GGRskim, 'Ervarenreistijd', 'PplusRherkomst', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot)
