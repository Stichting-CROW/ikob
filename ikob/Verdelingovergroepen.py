import logging

logger = logging.getLogger(__name__)


def verdeling_over_groepen(config, datasource):
    project_config = config['project']
    verdeling_config = config['verdeling']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    Kunst = verdeling_config['kunstmab']['gebruiken']
    GratisOVpercentage = verdeling_config['GratisOVpercentage']
    motieven = project_config ['motieven']

    # Vaste waarden
    inkomens = ['laag', 'middellaag', 'middelhoog', 'hoog']

    CBSAutobezitegevens = datasource.read_segs('CBS_autos_per_huishouden')
    Stedelijkheidsgraadgegevens = datasource.read_segs('Stedelijkheidsgraad')

    Gratisautonaarinkomens = [0, 0.02, 0.175, 0.275]

    if Kunst:
        Kunstmatigautobezit = datasource.read_verdeling('kunstmab', 'int')

    Sted = []

    for i in range (0,len(Stedelijkheidsgraadgegevens)):
        Sted.append(int (Stedelijkheidsgraadgegevens[i]))
    if Kunst:
        Minimumautobezit = []
        for i in range (0, len(CBSAutobezitegevens)):
            Minimumautobezit.append(min(CBSAutobezitegevens[i],Kunstmatigautobezit[i]))
    else:
        Minimumautobezit = CBSAutobezitegevens

    GRijbewijs = datasource.read_segs('GeenRijbewijs')
    GAuto = datasource.read_segs('GeenAuto')
    WAuto = datasource.read_segs ('WelAuto')
    Voorkeuren = datasource.read_segs('Voorkeuren')
    VoorkeurenGeenAuto = datasource.read_segs('VoorkeurenGeenAuto')

    inkomens =  ['laag', 'middellaag', 'middelhoog', 'hoog']
    voorkeuren = ['Auto','Neutraal', 'Fiets', 'OV']
    voorkeurengeenauto = ['Neutraal', 'Fiets', 'OV']
    soorten = ['GratisAuto', 'WelAuto', 'GeenAuto', 'GeenRijbewijs' ]

    def Corrigeren (Matrix, Lijst) :
        Matrix2 =[]
        for i in range ( len ( Matrix ) ):
            Matrix2.append([])
            Som = sum(Matrix[i])
            if Som > 0:
                Correctiefactor = Lijst[i] / Som
            else:
                Correctiefactor = 1
            for j in range ( len ( Matrix[0] ) ):
                Correctie = Matrix[i][j]*Correctiefactor
                Matrix2[i].append(round(Correctie,4))
        return Matrix2

    Totaaloverzicht = []
    Overzichttotaalautobezit = []
    Header = []
    WelAuto = []
    GratisAuto = []
    GratisAutoenOV = []
    NietGratisAuto = []
    GeenAutoWelRijbewijs = []
    GeenRijbewijs = []

    for mot in motieven:
        if mot == 'werk':
            Bevolkingsdeel = 'Beroepsbevolking'
            Inwonersperklasse = datasource.read_segs(f'{Bevolkingsdeel}_inkomensklasse', scenario=scenario)
        elif mot == 'winkelnietdagelijksonderwijs':
            Bevolkingsdeel = 'Leerlingen'
            Inwonersperklasse = datasource.read_segs(f'{Bevolkingsdeel}', scenario=scenario)
        else:
            Bevolkingsdeel = 'Inwoners'
            Inwonersperklasse = datasource.read_segs(f'{Bevolkingsdeel}_inkomensklasse', scenario=scenario)
        Inwonerstotalen = []
        for i in range (len(Inwonersperklasse)):
            Inwonerstotalen.append(sum(Inwonersperklasse[i]))
        Inkomensverdeling = []
        for i in range (len(Inwonersperklasse)):
            Inkomensverdeling.append([])
            for j in range (len(Inwonersperklasse[0])):
                if Inwonerstotalen[i]>0:
                    Inkomensverdeling[i].append(Inwonersperklasse[i][j]/Inwonerstotalen[i])
                else:
                    Inkomensverdeling[i].append (0)
        logger.debug("Lengte Inkomensverdelingsgegevens: %d, %d", len(Inkomensverdeling), len(Inkomensverdeling[0]))

        for ink in inkomens:
            for srt in soorten :
                if srt== 'GratisAuto' :
                    Header.append (f'{srt}_{ink}')
                    Header.append (f'{srt}_GratisOV_{ink}')
                elif srt== 'WelAuto' :
                    Header.append (f'{srt}_GratisOV_{ink}')
                    for vk in voorkeuren :
                        Header.append (f'{srt}_vk{vk}_{ink}')
                else :
                    Header.append ( f'{srt}_GratisOV_{ink}' )
                    for vkg in voorkeurengeenauto:
                        Header.append ( f'{srt}_vk{vkg}_{ink}' )

                    # Eerst "theoretosch auto- en rijbewijsbezit" vaststellen

        for i in range ( len ( Inkomensverdeling ) ):
            WelAuto.append([])
            GeenAutoWelRijbewijs.append([])
            GeenRijbewijs.append([])
            Totaaloverzicht.append([])
            Overzichttotaalautobezit.append([])
            Autobezitpercentage = []
            for Getal1,Getal2 in zip (Inkomensverdeling[i], WAuto[Sted[i]-1]) :
                Autobezitpercentage.append ( Getal1 * Getal2/100)
            Autobezitpercentages = sum (Autobezitpercentage)

            #Kijken of het werkelijke autobezit lager is:
            if Minimumautobezit[i] > 0 :
                if Minimumautobezit[i]/100 < Autobezitpercentages :
                    Autobezitcorrectiefactor = (Minimumautobezit[i]/100) / Autobezitpercentages
                    Autobezitpercentages = Minimumautobezit [i]/100
                else :
                    Autobezitcorrectiefactor = 1
            else :
                Autobezitcorrectiefactor = 1

            # Nu autobezit, rijbewijsbezit per inkomensklasse bepalen

            for ink in inkomens :
                WAutoaandeeltheor = WAuto[Sted[i]-1][inkomens.index(ink)]/100
                WAutoaandeel = WAutoaandeeltheor * Autobezitcorrectiefactor
                if Autobezitcorrectiefactor!=1 :
                    Geenautobezitcorrectiefactor = (1 - WAutoaandeel)/ (1-WAutoaandeeltheor)
                else:
                    Geenautobezitcorrectiefactor = 1
                WelAuto[i].append (WAutoaandeel)
                GeenAutoWelRijbewijs[i].append (GAuto[Sted[i] - 1][inkomens.index(ink)]/100 * Geenautobezitcorrectiefactor )
                GeenRijbewijs[i].append (GRijbewijs[Sted[i] - 1][inkomens.index(ink)]/100 * Geenautobezitcorrectiefactor)


            for ink in inkomens :
                #Van de auto's de gratisauto's en gratisauto en OV-bepalen en de rest overhouden
                Overzichtperinkomensgroep = []
                Inkomensaandeel = Inkomensverdeling [i][inkomens.index(ink)]
                GratisAuto = WelAuto[i][inkomens.index(ink)] * Gratisautonaarinkomens [inkomens.index(ink)]
                NietGratisAuto= WelAuto[i][inkomens.index(ink)] - GratisAuto
                GratisAutoaandeel = GratisAuto * (1-GratisOVpercentage) * Inkomensaandeel
                Totaaloverzicht[i].append( round(GratisAutoaandeel,4)) # Eerst GratisAuto
                Overzichtperinkomensgroep.append( round(GratisAutoaandeel,4)) # Eerst GratisAuto
                GratisAutoenOVaandeel = GratisAuto * GratisOVpercentage * Inkomensaandeel
                Totaaloverzicht[i].append( round (GratisAutoenOVaandeel,4)) # Dan GratisOV
                Overzichtperinkomensgroep.append( round (GratisAutoenOVaandeel,4)) # Dan GratisOV
                GratisOVaandeel = NietGratisAuto * GratisOVpercentage * Inkomensaandeel
                Totaaloverzicht[i].append( round (GratisOVaandeel,4)) # WelAuto, maar gratisOV
                Overzichtperinkomensgroep.append( round (GratisOVaandeel,4)) # WelAuto, maar gratisOV
                for vk in voorkeuren :
                    Aandeelvk = NietGratisAuto * (1-GratisOVpercentage) * Voorkeuren[Sted[i] - 1][voorkeuren.index ( vk )] / 100
                    Voorkeursaandeel = Aandeelvk * Inkomensaandeel
                    Totaaloverzicht[i].append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren
                    Overzichtperinkomensgroep.append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren

                GeenAuto = GeenAutoWelRijbewijs[i][inkomens.index(ink)]
                GeenAutoGratisOVaandeel = GeenAuto * GratisOVpercentage * Inkomensaandeel
                Totaaloverzicht[i].append ( round(GeenAutoGratisOVaandeel,4)) # Gratis OV voor Geen Auto
                Overzichtperinkomensgroep.append(0)
                for vkg in voorkeurengeenauto:
                    Aandeelvk = GeenAuto * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i] - 1][voorkeurengeenauto.index ( vkg )] / 100
                    Voorkeursaandeel = Aandeelvk * Inkomensaandeel
                    Totaaloverzicht[i].append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren
                    Overzichtperinkomensgroep.append(0)
                GeenRB = GeenRijbewijs[i][inkomens.index(ink)]
                GeenRBGratisOVaandeel = GeenRB * GratisOVpercentage * Inkomensaandeel
                Totaaloverzicht[i].append ( round(GeenRBGratisOVaandeel,4)) # Gratis OV voor Geen Rijbewijs
                Overzichtperinkomensgroep.append(0)
                for vkg in voorkeurengeenauto:
                    Aandeelvk = GeenRB * (1 - GratisOVpercentage) * VoorkeurenGeenAuto[Sted[i] - 1][voorkeurengeenauto.index ( vkg )] / 100
                    Voorkeursaandeel = Aandeelvk * Inkomensaandeel
                    Totaaloverzicht[i].append ( round (Voorkeursaandeel,4)) # Dan de diverse voorkeuren
                    Overzichtperinkomensgroep.append(0)
                for j in range (len(Overzichtperinkomensgroep)):
                    if sum (Overzichtperinkomensgroep)>0:
                        Overzichttotaalautobezit[i].append(round(Overzichtperinkomensgroep[j]/sum (Overzichtperinkomensgroep) *
                                                                 Inkomensaandeel,4))
                    else:
                        Overzichttotaalautobezit[i].append(0)

        logger.debug("Overzichttotaalautobezit: %s", Overzichttotaalautobezit)
        datasource.write_segs_csv(Totaaloverzicht, 'Verdeling_over_groepen', scenario=scenario, header=Header)
        datasource.write_segs_csv(Overzichttotaalautobezit, 'Verdeling_over_groepen_alleen_autobezit', scenario=scenario, header=Header)
        Header.insert(0, 'Zone')
        datasource.write_segs_xlsx(Totaaloverzicht, 'Verdeling_over_groepen', scenario=scenario, header=Header)
        datasource.write_segs_xlsx(Overzichttotaalautobezit, 'Verdeling_over_groepen_alleen_autobezit', scenario=scenario, header=Header)
