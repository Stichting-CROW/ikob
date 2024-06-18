import ikob.Routines as Routines
import numpy as np
from ikob.datasource import DataSource


def KostenOV(afstand, OVkmtarief, starttarief, Pricecap, Pricecapgetal):
    afstand = np.where(afstand < 0, 0, afstand)
    afstand = starttarief + afstand * OVkmtarief

    if Pricecap:
        np.clip(afstand, None, Pricecapgetal, out=afstand)

    return afstand


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
    TVOMwerk = tvom_config['werk']
    TVOMoverig = tvom_config['overig']
    varfossiel = skims_config['Kosten auto fossiele brandstof']['variabele kosten']
    kmheffingfossiel = skims_config['Kosten auto fossiele brandstof']['kmheffing']
    varelektrisch = skims_config['Kosten elektrische auto']['variabele kosten']
    kmheffingelelektrisch = skims_config['Kosten elektrische auto']['kmheffing']
    varkostenga = skims_config['varkostenga']
    tijdkostenga = skims_config['tijdkostenga']
    dagsoort = skims_config['dagsoort']
    soortgeenauto = ['GeenAuto', 'GeenRijbewijs']
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
    inkomens = ['laag', 'middellaag', 'middelhoog', 'hoog']

    OVkmtarief = OVkmtarief/100
    starttarief = starttarief/100
    varfossiel = varfossiel/100
    varelektrisch = varelektrisch/100
    kmheffingfossiel = kmheffingfossiel/100
    kmheffingelektrisch = kmheffingelelektrisch/100

    Parkeertijdlijst = datasource.read_parkeerzoektijden()

    soortbrandstof = ['fossiel', 'elektrisch']

    if 'orrectie' in regime:
        motief = motieven[0]
        if '65+' in regime:
            Correctiefactoren = datasource.read_segs(f"Correctiefactoren_{motief}_65plus", scenario=scenario)
        else:
            Correctiefactoren = datasource.read_segs(f"Correctiefactoren_{motief}", scenario=scenario)
    else:
        Correctiefactoren = []
        for i in range(len(Parkeertijdlijst)):
            Correctiefactoren.append([1, 1, 1, 1])

    for mot in motieven:
        TVOM = TVOMwerk if mot == 'werk' else TVOMoverig
        for ds in dagsoort:
            Autotijdmatrix = datasource.read_skims('Auto_Tijd', ds)
            Autoafstandmatrix = datasource.read_skims('Auto_Afstand', ds)
            Fietstijdmatrix = datasource.read_skims('Fiets_Tijd', ds)
            OVtijdmatrix = datasource.read_skims('OV_Tijd', ds)
            OVafstandmatrix = datasource.read_skims('OV_Afstand', ds)
            if Parkeerkosten:
                raise NotImplementedError("Needs to be replaced with datasource reading...")
                Parkeerkostenfile = Parkeerkostenfile.replace('.csv', '')
                Parkeerkostenlijst = Routines.csvintlezen(Parkeerkostenfile, aantal_lege_regels=0)
            else:
                Parkeerkostenlijst = Routines.lijstvolnullen(len(OVafstandmatrix))

            if Ketens:
                Pplusfietstijdmatrix = datasource.read_skims(f'Pplusfiets_{Hubnaam}_Tijd', ds)
                Pplusfietsafstandmatrix = datasource.read_skims(f'Pplusfiets_{Hubnaam}_Afstand_Auto', ds)
                PplusRbestemmingstijdmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_bestemmings_Tijd', ds)
                PplusRherkomsttijdmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_herkomst_Tijd', ds)
                PplusRbestemmingsOVafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_bestemmings_Afstand_OV', ds)
                PplusRbestemmingsautoafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_bestemmings_Afstand_Auto', ds)
                PplusRherkomstOVafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_herkomst_Afstand_OV', ds)
                PplusRherkomstautoafstandmatrix = datasource.read_skims(f'PplusR_{Hubnaam}_herkomst_Afstand_Auto', ds)

            aantal_zones_tijd = len(Autotijdmatrix)
            aantal_zones_afstand = len(Autoafstandmatrix)
            msg = (
                "Number of zones in time and distance have to match: "
                f"{aantal_zones_afstand} == {aantal_zones_tijd}"
            )
            assert aantal_zones_afstand == aantal_zones_tijd, msg
            aantal_zones = aantal_zones_tijd

            afmeting = len(OVafstandmatrix)

            # kostenmatrix
            if OV_Kostenbestand:
                KostenmatrixOV = datasource.read_skims("OV_Kosten", ds)
            else:
                KostenmatrixOV = np.zeros((afmeting, afmeting))
                KostenmatrixOV = KostenOV(OVafstandmatrix, OVkmtarief, starttarief, Pricecap, Pricecapgetal)

            if Ketens:
                KostenbestemmingsPplusROV = np.zeros((afmeting, afmeting))
                KostenherkomstPplusROV = np.zeros((afmeting, afmeting))
                KostenbestemmingsPplusROV = KostenOV(PplusRbestemmingsOVafstandmatrix, OVkmtarief, starttarief, Pricecap, Pricecapgetal)
                KostenherkomstPplusROV = KostenOV(PplusRherkomstOVafstandmatrix, OVkmtarief, starttarief, Pricecap, Pricecapgetal)

            # Eerst de fiets:
            GGRskim = np.where(Fietstijdmatrix < 180, Fietstijdmatrix, 9999).astype(int)
            datasource.write_csv(GGRskim, 'Ervarenreistijd', 'Fiets', ds, regime=regime, mot=mot)

            GGRskim = np.zeros((aantal_zones, aantal_zones), dtype=int)
            for ink in inkomens:
                factor = TVOM.get(ink)

                for srtbr in soortbrandstof:
                    if srtbr == 'fossiel':
                        varautotarief = varfossiel
                        kmheffing = kmheffingfossiel
                    else:
                        varautotarief = varelektrisch
                        kmheffing = kmheffingelektrisch
                    for i in range(aantal_zones):
                        for j in range(aantal_zones):
                            totaleTijd = Autotijdmatrix[i][j] + round(Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2])
                            if Additionele_kosten:
                                GGRskim[i][j] = int(totaleTijd + factor * (Autoafstandmatrix[i][j] *
                                                    (varautotarief + kmheffing) + Additionele_kostenmatrix[i][j]/100) +
                                                    Parkeerkostenlijst[j]/100)
                            else:
                                GGRskim[i][j] = int(totaleTijd + factor * (Autoafstandmatrix [i][j] *
                                                    Correctiefactoren[i][inkomens.index(ink)] *
                                                    (varautotarief+kmheffing) + Parkeerkostenlijst[j]/100))

                    datasource.write_csv(GGRskim, 'Ervarenreistijd', f"Auto_{srtbr}", ds, ink=ink, regime=regime, mot=mot)

                # Dan het OV
                factor = TVOM.get(ink)
                GGRskim = np.where(OVtijdmatrix > 0.5, OVtijdmatrix + factor * KostenmatrixOV, 9999).astype(int)
                datasource.write_csv(GGRskim, 'Ervarenreistijd', 'OV', ds, ink=ink, regime=regime, mot=mot)

                # Dan geen auto (rijbewijs)
                for sga in soortgeenauto:
                    GGRskim.fill(99999)
                    factor = TVOM.get(ink)
                    for i in range(aantal_zones):
                        for j in range(aantal_zones):
                            if Autotijdmatrix[i][j] >= 7:
                                totaleTijd = Autotijdmatrix[i][j] + round(Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2])
                                totaleKosten = Autotijdmatrix[i][j] * tijdkostenga.get(sga) + Correctiefactoren[i][inkomens.index(ink)] * Autoafstandmatrix[i][j] * (varkostenga.get(sga) + kmheffing)
                                GGRskim[i][j] = int(totaleTijd + factor * totaleKosten)

                    datasource.write_csv(GGRskim, 'Ervarenreistijd', f'{sga}', ds, ink=ink, regime=regime, mot=mot)

                # GratisAuto
                for ink in inkomens:
                    GGRskim.fill(0)
                    factor = TVOM.get(ink)
                    for i in range(aantal_zones):
                        for j in range(aantal_zones):
                            totaleTijd = Autotijdmatrix[i][j] + round(Parkeertijdlijst[i][1] + Parkeertijdlijst[j][2])
                            if Additionele_kosten:
                                GGRskim[i][j] = int(totaleTijd + factor * Autoafstandmatrix[i][j] *
                                                    kmheffing + Additionele_kostenmatrix[i][j]/100 +
                                                    Parkeerkostenlijst[j]/100)
                            else:
                                GGRskim[i][j] = int(totaleTijd + Correctiefactoren[i][inkomens.index(ink)] *
                                                    factor * Autoafstandmatrix[i][j] *
                                                    kmheffing + Parkeerkostenlijst[j]/100)
                    datasource.write_csv(GGRskim, 'Ervarenreistijd', 'GratisAuto', ds, ink=ink, regime=regime, mot=mot)

                # GratisOV
                GGRskim = np.where(OVtijdmatrix > 0.5, OVtijdmatrix, 9999).astype(int)
                datasource.write_csv(GGRskim, 'Ervarenreistijd', 'GratisOV', ds, regime=regime, mot=mot)

                if Ketens:
                    # P+Fiets
                    for ink in inkomens:
                        GGRskim.fill(0)
                        kosten = Pplusfietsafstandmatrix * (varautotarief + kmheffing)
                        if Additionele_kosten:
                            kosten += Additionele_kostenmatrix/100

                        factor = TVOM.get(ink)
                        GGRskim = Pplusfietstijdmatrix + factor * kosten
                        datasource.write_csv(GGRskim.astype(int), 'Ervarenreistijd', 'Pplusfiets', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot)

                        # P+R
                        GGRskim.fill(0)
                        kosten = PplusRbestemmingsautoafstandmatrix * (varautotarief + kmheffing) + KostenbestemmingsPplusROV
                        if Additionele_kosten:
                            kosten += Additionele_kostenmatrix / 100

                        GGRskim = PplusRbestemmingstijdmatrix + factor * kosten
                        datasource.write_csv(GGRskim.astype(int), 'Ervarenreistijd', 'PplusRbestemmings', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot)

                        GGRskim.fill(0)
                        kosten = (PplusRherkomstautoafstandmatrix * (varautotarief + kmheffing) + KostenherkomstPplusROV)
                        if Additionele_kosten:
                            kosten += Additionele_kostenmatrix / 100

                        GGRskim = PplusRherkomsttijdmatrix + factor * kosten
                        datasource.write_csv(GGRskim.astype(int), 'Ervarenreistijd', 'PplusRherkomst', ds, ink=ink, hubnaam=Hubnaam, regime=regime, mot=mot)
