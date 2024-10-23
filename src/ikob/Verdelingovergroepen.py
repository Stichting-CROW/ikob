from ikob.datasource import DataSource, SegsSource, read_csv_from_config
import itertools
import logging
import numpy as np

logger = logging.getLogger(__name__)


def verdeling_over_groepen(config):
    logger.info("Verdeling van de groepen over de buurten of zones")

    project_config = config['project']
    verdeling_config = config['verdeling']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    Kunst = verdeling_config['kunstmab']['gebruiken']
    GratisOVpercentage = verdeling_config['GratisOVpercentage']
    motieven = project_config['motieven']

    # Vaste waarden
    inkomens = ['laag', 'middellaag', 'middelhoog', 'hoog']
    voorkeuren = ['Auto', 'Neutraal', 'Fiets', 'OV']
    voorkeurengeenauto = ['Neutraal', 'Fiets', 'OV']
    soorten = ['GratisAuto', 'WelAuto', 'GeenAuto', 'GeenRijbewijs']

    segs_source = SegsSource(config)

    CBSAutobezitegevens = segs_source.read('CBS_autos_per_huishouden')
    Stedelijkheidsgraadgegevens = segs_source.read('Stedelijkheidsgraad')
    # Decrement one to account for zero-based indexing later on.
    Sted = [int(sgg) - 1 for sgg in Stedelijkheidsgraadgegevens]

    Gratisautonaarinkomens = [0, 0.02, 0.175, 0.275]
    Minimumautobezit = CBSAutobezitegevens

    if Kunst:
        Kunstmatigautobezit = read_csv_from_config(config, key='verdeling', id='kunstmab', type_caster=int)
        Minimumautobezit = list(itertools.starmap(min, zip(CBSAutobezitegevens, Kunstmatigautobezit)))

    # Read SEGS input files.
    GRijbewijs = segs_source.read('GeenRijbewijs')
    GAuto = segs_source.read('GeenAuto')
    WAuto = segs_source.read('WelAuto')
    Voorkeuren = segs_source.read('Voorkeuren')
    VoorkeurenGeenAuto = segs_source.read('VoorkeurenGeenAuto')

    Header = []
    for ink in inkomens:
        for srt in soorten:
            if srt == 'GratisAuto':
                Header.append(f'{srt}_{ink}')
                Header.append(f'{srt}_GratisOV_{ink}')
            elif srt == 'WelAuto':
                Header.append(f'{srt}_GratisOV_{ink}')
                for vk in voorkeuren:
                    Header.append(f'{srt}_vk{vk}_{ink}')
            else:
                Header.append(f'{srt}_GratisOV_{ink}')
                for vkg in voorkeurengeenauto:
                    Header.append(f'{srt}_vk{vkg}_{ink}')

    Totaaloverzicht = []
    Overzichttotaalautobezit = []
    GratisAuto = []
    NietGratisAuto = []
    GeenAutoWelRijbewijs = []

    for mot in motieven:
        if mot == 'werk':
            Bevolkingsdeel = 'Beroepsbevolking'
            Inwonersperklasse = segs_source.read(f'{Bevolkingsdeel}_inkomensklasse', scenario=scenario)
        elif mot == 'winkelnietdagelijksonderwijs':
            Bevolkingsdeel = 'Leerlingen'
            Inwonersperklasse = segs_source.read(f'{Bevolkingsdeel}', scenario=scenario)
        else:
            Bevolkingsdeel = 'Inwoners'
            Inwonersperklasse = segs_source.read(f'{Bevolkingsdeel}_inkomensklasse', scenario=scenario)

        Inwonerstotalen = np.sum(Inwonersperklasse, axis=1)
        Inkomensverdeling = Inwonersperklasse / Inwonerstotalen[:, None]
        # Replace inf (result of divide by zero) with zero entries.
        Inkomensverdeling = np.where(np.isinf(Inkomensverdeling), 0, Inkomensverdeling)

        # Eerst "theoretosch auto- en rijbewijsbezit" vaststellen
        for i, inkomen_verdeling in enumerate(Inkomensverdeling):
            Totaaloverzicht.append([])
            Overzichttotaalautobezit.append([])

            Autobezitpercentage = []
            for Getal1, Getal2 in zip(inkomen_verdeling, WAuto[Sted[i]]):
                Autobezitpercentage.append(Getal1 * Getal2/100)
            Autobezitpercentages = sum(Autobezitpercentage)

            # Kijken of het werkelijke autobezit lager is:
            Autobezitcorrectiefactor = 1
            if Minimumautobezit[i] > 0 and Minimumautobezit[i]/100 < Autobezitpercentages:
                Autobezitcorrectiefactor = (Minimumautobezit[i]/100) / Autobezitpercentages
                Autobezitpercentages = Minimumautobezit[i]/100

            # Nu autobezit, rijbewijsbezit per inkomensklasse bepalen
            for i_ink in range(len(inkomens)):
                WAutoaandeeltheor = WAuto[Sted[i]][i_ink]/100
                WelAuto = WAutoaandeeltheor * Autobezitcorrectiefactor

                if Autobezitcorrectiefactor != 1:
                    Geenautobezitcorrectiefactor = (1 - WelAuto)/(1-WAutoaandeeltheor)
                else:
                    Geenautobezitcorrectiefactor = 1

                GeenAutoWelRijbewijs = GAuto[Sted[i]][i_ink]/100 * Geenautobezitcorrectiefactor
                GeenRijbewijs = GRijbewijs[Sted[i]][i_ink]/100 * Geenautobezitcorrectiefactor

                # Van de auto's de gratisauto's en gratisauto en OV-bepalen en de rest overhouden
                Overzichtperinkomensgroep = []
                Inkomensaandeel = inkomen_verdeling[i_ink]

                GratisAuto = WelAuto * Gratisautonaarinkomens[i_ink]
                NietGratisAuto = WelAuto - GratisAuto
                GratisAutoaandeel = round(GratisAuto * (1 - GratisOVpercentage) * Inkomensaandeel, 4)
                Totaaloverzicht[i].append(GratisAutoaandeel)
                Overzichtperinkomensgroep.append(GratisAutoaandeel)

                GratisAutoenOVaandeel = round(GratisAuto * GratisOVpercentage * Inkomensaandeel, 4)
                Totaaloverzicht[i].append(GratisAutoenOVaandeel)
                Overzichtperinkomensgroep.append(GratisAutoenOVaandeel)

                GratisOVaandeel = round(NietGratisAuto * GratisOVpercentage * Inkomensaandeel, 4)
                Totaaloverzicht[i].append(GratisOVaandeel)
                Overzichtperinkomensgroep.append(GratisOVaandeel)

                for i_vk in range(len(voorkeuren)):
                    Aandeelvk = NietGratisAuto * (1-GratisOVpercentage) * Voorkeuren[Sted[i]][i_vk] / 100
                    Voorkeursaandeel = round(Aandeelvk * Inkomensaandeel, 4)
                    Totaaloverzicht[i].append(Voorkeursaandeel)
                    Overzichtperinkomensgroep.append(Voorkeursaandeel)

                GeenAutoGratisOVaandeel = round(GeenAutoWelRijbewijs * GratisOVpercentage * Inkomensaandeel, 4)
                Totaaloverzicht[i].append(GeenAutoGratisOVaandeel)
                Overzichtperinkomensgroep.append(0)

                for i_vk in range(len(voorkeurengeenauto)):
                    Aandeelvk = GeenAutoWelRijbewijs * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i]][i_vk] / 100
                    Voorkeursaandeel = round(Aandeelvk * Inkomensaandeel, 4)
                    Totaaloverzicht[i].append(Voorkeursaandeel)
                    Overzichtperinkomensgroep.append(0)

                GeenRBGratisOVaandeel = round(GeenRijbewijs * GratisOVpercentage * Inkomensaandeel, 4)
                Totaaloverzicht[i].append(GeenRBGratisOVaandeel)
                Overzichtperinkomensgroep.append(0)

                for i_vk in range(len(voorkeurengeenauto)):
                    Aandeelvk = GeenRijbewijs * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i]][i_vk] / 100
                    Voorkeursaandeel = round(Aandeelvk * Inkomensaandeel, 4)
                    Totaaloverzicht[i].append(Voorkeursaandeel)
                    Overzichtperinkomensgroep.append(0)

                for i_oig in range(len(Overzichtperinkomensgroep)):
                    if sum(Overzichtperinkomensgroep) > 0:
                        Overzichttotaalautobezit[i].append(round(Overzichtperinkomensgroep[i_oig]/sum(Overzichtperinkomensgroep) * Inkomensaandeel, 4))
                    else:
                        Overzichttotaalautobezit[i].append(0)

        logger.debug("Overzichttotaalautobezit: %s", Overzichttotaalautobezit)
        segs_source.write_csv(Totaaloverzicht, f'Verdeling_over_groepen', group=Bevolkingsdeel, scenario=scenario, header=Header)
        segs_source.write_csv(Overzichttotaalautobezit, f'Verdeling_over_groepen', group=Bevolkingsdeel, modifier="alleen_autobezit", scenario=scenario, header=Header)
        segs_source.write_xlsx(Totaaloverzicht, f'Verdeling_over_groepen', group=Bevolkingsdeel, scenario=scenario, header=['Zone', *Header])
        segs_source.write_xlsx(Overzichttotaalautobezit, f'Verdeling_over_groepen', group=Bevolkingsdeel, modifier="alleen_autobezit", scenario=scenario, header=['Zone', *Header])
