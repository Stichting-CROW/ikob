import os

import ikob.utils as utils
from ikob.datasource import get_project_name
from ikob.gui.configuration_definition import NoCarKind
from ikob.ikobconfig import get_config_from_args

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = get_config_from_args()
# nieuw automatisch toegevoegd config item.
Projectbestandsnaam = get_project_name(config)

# Haal (voor het gemak) onderdelen voor dit script er uit.
project_config = config.project
paden_config = config.project.paths
skims_config = config.skims
tvom_config = config.tvom
ketens_config = config.chains_and_hubs

# Ophalen van instellingen
jaar = project_config.urbanization_scenario
Basisdirectory = paden_config.skims_directory
Skimsdirectory = os.path.join(Basisdirectory, "skims")
os.makedirs(Skimsdirectory, exist_ok=True)
motieven = project_config.motives
Ketens = ketens_config.use
Hubnaam = ketens_config.hub_collection
TVOMwerk = tvom_config.work_tvom
TVOMoverig = tvom_config.other_tvom
varautotarief = skims_config.ice_costs.cent_per_km
kmheffing = skims_config.ice_costs.km_charge
varkostenga = skims_config.no_car_costs.no_car_euro_per_km
tijdkostenga = skims_config.no_car_costs.no_car_euro_per_min
dagsoort = skims_config.parts_of_day
soortgeenauto = list(NoCarKind)

OVkmtarief = skims_config.pt_costs.cent_per_km
starttarief = skims_config.pt_costs.base_fare_cent
Parkeerzoektijdfile = skims_config.parking_search_time_file
Additionele_kosten = config.advanced.additional_costs_cents.use
Additionele_kostenfile = config.advanced.additional_costs_cents.file
Parkeerkosten = config.advanced.parking_costs_cents.use
Parkeerkostenfile = config.advanced.parking_costs_cents.file


if Additionele_kosten:
    Additionele_kostenfile = Additionele_kostenfile.replace(".csv", "")
    Additionele_kostenmatrix = utils.read_csv_int(Additionele_kostenfile, aantal_lege_regels=0)

# Vaste waarden
inkomens = ["laag", "middellaag", "middelhoog", "hoog"]

OVkmtarief = float(OVkmtarief) / 100
starttarief = float(starttarief) / 100
varautotarief = float(varautotarief) / 100
Parkeerzoektijdfile = Parkeerzoektijdfile.replace(".csv", "")
Parkeertijdlijst = utils.read_csv(Parkeerzoektijdfile, aantal_lege_regels=1)
print(Projectbestandsnaam)
Projectdirectory = os.path.join(Basisdirectory, Projectbestandsnaam)
print(Projectdirectory)
os.makedirs(Projectdirectory, exist_ok=True)
Ervarenreistijddirectory = os.path.join(Projectdirectory, "ervarenreistijd")
print(Ervarenreistijddirectory)
os.makedirs(Ervarenreistijddirectory, exist_ok=True)


def KostenOV(afstand, OVkmtarief, starttarief):
    flaf = float(afstand)
    if flaf <= 0:
        return 0
    else:
        return flaf * OVkmtarief + starttarief
    return 0


Jaardirectory = os.path.join(Ervarenreistijddirectory)
os.makedirs(Jaardirectory, exist_ok=True)
print(Jaardirectory)
Jaarinvoerdirectory = os.path.join(Skimsdirectory)
for ds in dagsoort:
    Invoerdirectory = os.path.join(Jaarinvoerdirectory, ds)
    Uitvoerdirectory = os.path.join(Jaardirectory, ds)
    os.makedirs(Uitvoerdirectory, exist_ok=True)
    print(Uitvoerdirectory)
    Autotijdfilenaam = os.path.join(Invoerdirectory, "Auto_Tijd")
    Autotijdmatrix = utils.read_csv_float(Autotijdfilenaam, aantal_lege_regels=0)
    Autoafstandfilenaam = os.path.join(Invoerdirectory, "Auto_Afstand")
    Autoafstandmatrix = utils.read_csv_float(Autoafstandfilenaam, aantal_lege_regels=0)
    Fietstijdfilenaam = os.path.join(Invoerdirectory, "Fiets_Tijd")
    Fietstijdmatrix = utils.read_csv_float(Fietstijdfilenaam, aantal_lege_regels=0)
    OVtijdfilenaam = os.path.join(Invoerdirectory, "OV_Tijd")
    OVtijdmatrix = utils.read_csv_float(OVtijdfilenaam, aantal_lege_regels=0)
    OVafstandfilenaam = os.path.join(Invoerdirectory, "OV_Afstand")
    OVafstandmatrix = utils.read_csv_float(OVafstandfilenaam, aantal_lege_regels=0)
    if Parkeerkosten:
        Parkeerkostenfile = Parkeerkostenfile.replace(".csv", "")
        Parkeerkostenlijst = utils.read_csv_int(Parkeerkostenfile, aantal_lege_regels=0)
    else:
        Parkeerkostenlijst = utils.zeros(len(OVafstandmatrix))
    print(Parkeerkostenlijst)

    if Ketens:
        Pplusfietstijdfilenaam = os.path.join(Invoerdirectory, f"Pplusfiets_{Hubnaam}_Tijd")
        Pplusfietstijdmatrix = utils.read_csv_float(Pplusfietstijdfilenaam, aantal_lege_regels=0)
        Pplusfietsafstandfilenaam = os.path.join(Invoerdirectory, f"Pplusfiets_{Hubnaam}_Afstand_Auto")
        Pplusfietsafstandmatrix = utils.read_csv_float(Pplusfietsafstandfilenaam, aantal_lege_regels=0)
        PplusRbestemmingstijdfilenaam = os.path.join(Invoerdirectory, f"PplusR_{Hubnaam}_bestemmings_Tijd")
        PplusRbestemmingstijdmatrix = utils.read_csv_float(PplusRbestemmingstijdfilenaam, aantal_lege_regels=0)
        PplusRherkomsttijdfilenaam = os.path.join(Invoerdirectory, f"PplusR_{Hubnaam}_herkomst_Tijd")
        PplusRherkomsttijdmatrix = utils.read_csv_float(PplusRherkomsttijdfilenaam, aantal_lege_regels=0)
        PplusRbestemmingsOVafstandfilenaam = os.path.join(Invoerdirectory, f"PplusR_{Hubnaam}_bestemmings_Afstand_OV")
        PplusRbestemmingsOVafstandmatrix = utils.read_csv_float(
            PplusRbestemmingsOVafstandfilenaam, aantal_lege_regels=0
        )
        PplusRbestemmingsautoafstandfilenaam = os.path.join(
            Invoerdirectory, f"PplusR_{Hubnaam}_bestemmings_Afstand_Auto"
        )
        PplusRbestemmingsautoafstandmatrix = utils.read_csv_float(
            PplusRbestemmingsautoafstandfilenaam, aantal_lege_regels=0
        )
        PplusRherkomstOVafstandfilenaam = os.path.join(Invoerdirectory, f"PplusR_{Hubnaam}_herkomst_Afstand_OV")
        PplusRherkomstOVafstandmatrix = utils.read_csv_float(PplusRherkomstOVafstandfilenaam, aantal_lege_regels=0)
        PplusRherkomstautoafstandfilenaam = os.path.join(Invoerdirectory, f"PplusR_{Hubnaam}_herkomst_Afstand_Auto")
        PplusRherkomstautoafstandmatrix = utils.read_csv_float(PplusRherkomstautoafstandfilenaam, aantal_lege_regels=0)

    print("Parkeertijden bevat {} zones.".format(len(Parkeertijdlijst)))
    aantal_zones_tijd = len(Autotijdmatrix)
    print("Autotijdmatrix bevat {} zones.".format(aantal_zones_tijd))
    aantal_zones_afstand = len(Autoafstandmatrix)
    print("Auto-afstandmatrix bevat {} zones.".format(aantal_zones_afstand))
    if aantal_zones_afstand != aantal_zones_tijd:
        print("FOUT: Aantal zones niet gelijk!?")
        quit()
    aantal_zones = aantal_zones_tijd

    # kostenmatrix

    print("Bezig kosten berekenen.")
    afmeting = len(OVafstandmatrix)
    KostenmatrixOV = [
        [
            KostenOV(
                OVafstandmatrix[i][j],
                OVkmtarief,
                starttarief,
            )
            for j in range(afmeting)
        ]
        for i in range(afmeting)
    ]
    if Ketens:
        KostenbestemmingsPplusROV = [
            [
                KostenOV(
                    PplusRbestemmingsOVafstandmatrix[i][j],
                    OVkmtarief,
                    starttarief,
                )
                for j in range(afmeting)
            ]
            for i in range(afmeting)
        ]
        KostenherkomstPplusROV = [
            [
                KostenOV(
                    PplusRherkomstOVafstandmatrix[i][j],
                    OVkmtarief,
                    starttarief,
                )
                for j in range(afmeting)
            ]
            for i in range(afmeting)
        ]

    # Eerst de fiets:

    GTRskim = []
    aantal_zones_fiets = len(Fietstijdmatrix)
    for i in range(0, aantal_zones_fiets):
        GTRskim.append([])
        for j in range(0, aantal_zones_fiets):
            if Fietstijdmatrix[i][j] < 180:
                GTRskim[i].append(int(Fietstijdmatrix[i][j]))
            else:
                GTRskim[i].append(9999)
        for j in range(aantal_zones_fiets, aantal_zones):
            GTRskim[i].append(9999)
    for i in range(aantal_zones_fiets, aantal_zones):
        GTRskim.append([])
        for j in range(0, aantal_zones):
            GTRskim[i].append(9999)

    Uitvoerfilenaam = os.path.join(Uitvoerdirectory, "Fiets")
    utils.write_csv(GTRskim, Uitvoerfilenaam)

    for ink in inkomens:
        GTRskim = []
        Vermenigvuldigingsfactor = TVOMwerk.get(ink)
        for i in range(0, aantal_zones):
            GTRskim.append([])
            for j in range(0, aantal_zones):
                totaleTijd = Autotijdmatrix[i][j] + float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2])
                if Additionele_kosten:
                    GTRskim[i].append(
                        int(
                            totaleTijd
                            + Vermenigvuldigingsfactor
                            * (
                                Autoafstandmatrix[i][j] * (varautotarief + kmheffing)
                                + Additionele_kostenmatrix[i][j] / 100
                            )
                            + Parkeerkostenlijst[j] / 100
                        )
                    )
                else:
                    GTRskim[i].append(
                        int(
                            totaleTijd
                            + Vermenigvuldigingsfactor
                            * (Autoafstandmatrix[i][j] * (varautotarief + kmheffing) + Parkeerkostenlijst[j] / 100)
                        )
                    )

        Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"Auto_{ink}")
        utils.write_csv(GTRskim, Uitvoerfilenaam)

        # Dan het OV
        GTRskim = []
        Vermenigvuldigingsfactor = TVOMwerk.get(ink)
        for i in range(0, aantal_zones):
            GTRskim.append([])
            for j in range(0, aantal_zones):
                if float(OVtijdmatrix[i][j]) > 0.5:
                    Resultaat = float(OVtijdmatrix[i][j]) + Vermenigvuldigingsfactor * float(KostenmatrixOV[i][j])
                    Resultaatint = int(Resultaat)
                    GTRskim[i].append(Resultaatint)
                else:
                    GTRskim[i].append(9999)

        Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"OV_{ink}")
        utils.write_csv(GTRskim, Uitvoerfilenaam)

        # Dan geen auto (rijbewijs)
        for sga in soortgeenauto:
            GTRskim = []
            Vermenigvuldigingsfactor = TVOMwerk.get(ink)
            for i in range(0, aantal_zones):
                GTRskim.append([])
                for j in range(0, aantal_zones):
                    if Autotijdmatrix[i][j] < 7:
                        GTRskim[i].append(99999)
                    else:
                        totaleTijd = (
                            Autotijdmatrix[i][j] + float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2])
                        )
                        totaleKosten = Autotijdmatrix[i][j] * tijdkostenga.get(sga) + Autoafstandmatrix[i][j] * (
                            varkostenga.get(sga) + kmheffing
                        )
                        GTRskim[i].append(int(totaleTijd + Vermenigvuldigingsfactor * totaleKosten))

            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"{sga}_{ink}")
            utils.write_csv(GTRskim, Uitvoerfilenaam)

        # Nu GratisAuto
        for ink in inkomens:
            GTRskim = []
            Vermenigvuldigingsfactor = TVOMwerk.get(ink)
            for i in range(0, aantal_zones):
                GTRskim.append([])
                for j in range(0, aantal_zones):
                    totaleTijd = Autotijdmatrix[i][j] + float(Parkeertijdlijst[i][1]) + float(Parkeertijdlijst[j][2])
                    if Additionele_kosten:
                        GTRskim[i].append(
                            int(
                                totaleTijd
                                + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] * kmheffing
                                + Additionele_kostenmatrix[i][j] / 100
                                + Parkeerkostenlijst[j] / 100
                            )
                        )
                    else:
                        GTRskim[i].append(
                            int(
                                totaleTijd
                                + Vermenigvuldigingsfactor * Autoafstandmatrix[i][j] * kmheffing
                                + Parkeerkostenlijst[j] / 100
                            )
                        )
            Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"GratisAuto_{ink}")
            utils.write_csv(GTRskim, Uitvoerfilenaam)

        # Nu GratisOV
        GTRskim = []
        for i in range(0, aantal_zones):
            GTRskim.append([])
            for j in range(0, aantal_zones):
                if OVtijdmatrix[i][j] > 0.5:
                    GTRskim[i].append(int(OVtijdmatrix[i][j]))
                else:
                    GTRskim[i].append(9999)

        Uitvoerfilenaam = os.path.join(Uitvoerdirectory, "GratisOV")
        utils.write_csv(GTRskim, Uitvoerfilenaam)

        # Nu de ketens
        # Eerst P+Fiets
        if Ketens:
            for ink in inkomens:
                GTRskim = []
                Vermenigvuldigingsfactor = TVOMwerk.get(ink)
                for i in range(0, aantal_zones):
                    GTRskim.append([])
                    for j in range(0, aantal_zones):
                        if Additionele_kosten:
                            GTRskim[i].append(
                                int(
                                    Pplusfietstijdmatrix[i][j]
                                    + Vermenigvuldigingsfactor
                                    * (
                                        Pplusfietsafstandmatrix[i][j] * (varautotarief + kmheffing)
                                        + Additionele_kostenmatrix[i][j] / 100
                                    )
                                )
                            )
                        else:
                            GTRskim[i].append(
                                int(
                                    Pplusfietstijdmatrix[i][j]
                                    + Vermenigvuldigingsfactor * Pplusfietsafstandmatrix[i][j] * varautotarief
                                    + kmheffing
                                )
                            )

                Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"Pplusfiets_{Hubnaam}_{ink}")
                utils.write_csv(GTRskim, Uitvoerfilenaam)

                # Dan P+R

                GTRskim = []

                for i in range(0, aantal_zones):
                    GTRskim.append([])
                    for j in range(0, aantal_zones):
                        if Additionele_kosten:
                            GTRskim[i].append(
                                int(
                                    PplusRbestemmingstijdmatrix[i][j]
                                    + Vermenigvuldigingsfactor
                                    * (
                                        PplusRbestemmingsautoafstandmatrix[i][j] * (varautotarief + kmheffing)
                                        + Additionele_kostenmatrix[i][j] / 100
                                        + KostenbestemmingsPplusROV[i][j]
                                    )
                                )
                            )
                        else:
                            GTRskim[i].append(
                                int(
                                    PplusRbestemmingstijdmatrix[i][j]
                                    + Vermenigvuldigingsfactor
                                    * (
                                        PplusRbestemmingsautoafstandmatrix[i][j] * (varautotarief + kmheffing)
                                        + KostenbestemmingsPplusROV[i][j]
                                    )
                                )
                            )

                Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"PplusRbestemmings_{Hubnaam}_{ink}")
                utils.write_csv(GTRskim, Uitvoerfilenaam)

                GTRskim = []

                for i in range(0, aantal_zones):
                    GTRskim.append([])
                    for j in range(0, aantal_zones):
                        if Additionele_kosten:
                            GTRskim[i].append(
                                int(
                                    PplusRherkomsttijdmatrix
                                    + Vermenigvuldigingsfactor
                                    * (
                                        PplusRherkomstautoafstandmatrix[i][j] * (varautotarief + kmheffing)
                                        + Additionele_kostenmatrix[i][j] / 100
                                        + KostenherkomstPplusROV[i][j]
                                    )
                                )
                            )
                        else:
                            GTRskim[i].append(
                                int(
                                    PplusRherkomsttijdmatrix[i][j]
                                    + Vermenigvuldigingsfactor
                                    * (
                                        PplusRherkomstautoafstandmatrix[i][j] * (varautotarief + kmheffing)
                                        + KostenherkomstPplusROV[i][j]
                                    )
                                )
                            )

                Uitvoerfilenaam = os.path.join(Uitvoerdirectory, f"PplusRherkomst_{Hubnaam}_{ink}")
                utils.write_csv(GTRskim, Uitvoerfilenaam)
