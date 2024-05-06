import Routines
import Berekeningen
import os


def combigroep(mod, gr) :
    string = ''
    if 'Auto' in mod:
        if 'GratisAuto' in gr:
            string = 'GratisAuto'
        elif 'Wel' in gr:
            string = 'Auto'
        if 'GeenAuto' in gr:
            string = 'GeenAuto'
        if 'GeenRijbewijs' in gr:
            string = 'GeenRijbewijs'
    if 'OV' in mod:
        if 'GratisOV' in gr:
            if string == '':
                string = string + 'GratisOV'
            else:
                string = string + '_GratisOV'
        else:
            if string == '':
                string = string + 'OV'
            else:
                string = string + '_OV'
    if 'EFiets' in mod:
        string = string + '_EFiets'
    elif 'Fiets' in mod:
        string = string + '_Fiets'
    return string


def bereken_concurrentie (Matrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen):
    Dezegroeplijst = []
    Arbeidsplaatsentrans = Berekeningen.Transponeren ( Arbeidsplaatsen )
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2, Getal3 in zip ( Matrix[i], Bereik, Arbeidsplaatsentrans[inkgroepen.index ( inkgr )] ):
            if Getal2 > 0:
                Gewogenmatrix.append ( Getal1 * Getal3 / Getal2 )
            else :
                Gewogenmatrix.append (0)
        Dezegroeplijst.append ( sum ( Gewogenmatrix ) )
    return Dezegroeplijst


def concurrentie_om_arbeidsplaatsen(config):
    Projectbestandsnaam = config['__filename__']  # nieuw automatisch toegevoegd config item.
    project_config = config['project']
    paden_config = config['project']['paden']
    skims_config = config['skims']
    verdeling_config = config ['verdeling']
    #verdeling_config = config['verdeling']
    dagsoort = skims_config['dagsoort']
    #conc_config = config['bedrijven']

    # Ophalen van instellingen
    Basisdirectory = paden_config['skims_directory']
    SEGSdirectory = paden_config['segs_directory']
    #Herkomstendirectory = conc_config['arbeid']['herkomsten_directory']
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config ['motieven']
    percentageelektrisch = verdeling_config ['Percelektrisch']
    print (percentageelektrisch)
    #Scenario = config['project']['scenario']
    #Naamuitvoer = conc_config['uitvoer_directory_naam']
    #Grverdelingfile = verdeling_config['uitvoernaam']

    # Vaste intellingen
    Groepen = ['GratisAuto_laag', 'GratisAuto_GratisOV_laag','WelAuto_GratisOV_laag','WelAuto_vkAuto_laag',
               'WelAuto_vkNeutraal_laag', 'WelAuto_vkFiets_laag','WelAuto_vkOV_laag','GeenAuto_GratisOV_laag',
               'GeenAuto_vkNeutraal_laag','GeenAuto_vkFiets_laag', 'GeenAuto_vkOV_laag','GeenRijbewijs_GratisOV_laag',
               'GeenRijbewijs_vkNeutraal_laag', 'GeenRijbewijs_vkFiets_laag', 'GeenRijbewijs_vkOV_laag',
               'GratisAuto_middellaag', 'GratisAuto_GratisOV_middellaag','WelAuto_GratisOV_middellaag',
               'WelAuto_vkAuto_middellaag','WelAuto_vkNeutraal_middellaag','WelAuto_vkFiets_middellaag',
               'WelAuto_vkOV_middellaag','GeenAuto_GratisOV_middellaag','GeenAuto_vkNeutraal_middellaag',
               'GeenAuto_vkFiets_middellaag', 'GeenAuto_vkOV_middellaag','GeenRijbewijs_GratisOV_middellaag',
               'GeenRijbewijs_vkNeutraal_middellaag','GeenRijbewijs_vkFiets_middellaag', 'GeenRijbewijs_vkOV_middellaag',
               'GratisAuto_middelhoog', 'GratisAuto_GratisOV_middelhoog','WelAuto_GratisOV_middelhoog',
               'WelAuto_vkAuto_middelhoog','WelAuto_vkNeutraal_middelhoog','WelAuto_vkFiets_middelhoog',
               'WelAuto_vkOV_middelhoog','GeenAuto_GratisOV_middelhoog','GeenAuto_vkNeutraal_middelhoog',
               'GeenAuto_vkFiets_middelhoog', 'GeenAuto_vkOV_middelhoog','GeenRijbewijs_GratisOV_middelhoog',
               'GeenRijbewijs_vkNeutraal_middelhoog', 'GeenRijbewijs_vkFiets_middelhoog', 'GeenRijbewijs_vkOV_middelhoog',
               'GratisAuto_hoog', 'GratisAuto_GratisOV_hoog', 'WelAuto_GratisOV_hoog','WelAuto_vkAuto_hoog',
               'WelAuto_vkNeutraal_hoog','WelAuto_vkFiets_hoog','WelAuto_vkOV_hoog','GeenAuto_GratisOV_hoog',
               'GeenAuto_vkNeutraal_hoog','GeenAuto_vkFiets_hoog', 'GeenAuto_vkOV_hoog','GeenRijbewijs_GratisOV_hoog',
               'GeenRijbewijs_vkNeutraal_hoog','GeenRijbewijs_vkFiets_hoog', 'GeenRijbewijs_vkOV_hoog']

    modaliteiten = ['Fiets',  'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets',  'Auto_OV',
                      'Auto_OV_Fiets']
    enkelemodaliteiten = ['Fiets', 'Auto', 'OV']
    inkgroepen = ['laag', 'middellaag', 'middelhoog', 'hoog']
    fiets = ['Fiets']
    OVauto = ['OV', 'Auto']
    voorkeurenfiets = ['', 'Fiets']
    soortbrandstof = ['fossiel','elektrisch']
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']
    headstringExcel=['Zone', 'Fiets', 'Auto', 'OV', 'Auto-Fiets' 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']


    #Grverdelingfile=Grverdelingfile.replace('.csv','')

    #Inkomensverdelingsfilenaam = os.path.join (SEGSdirectory, 'Inkomensverdeling_per_zone')
    #Inkomensverdeling = Routines.csvintlezen (Inkomensverdelingsfilenaam, aantal_lege_regels=1)
    if 'winkelnietdagelijksonderwijs' in motieven:
        Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'Leerlingen')
        Arbeidsplaatsenfilenaam = os.path.join(SEGSdirectory, scenario, f'Leerlingenplaatsen')
        Arbeidsplaatsen = Routines.csvintlezen(Arbeidsplaatsenfilenaam, aantal_lege_regels=1)
    else:
        Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'Beroepsbevolking_inkomensklasse')
        Arbeidsplaatsenfilenaam = os.path.join(SEGSdirectory, scenario, f'Arbeidsplaatsen_inkomensklasse')
        Arbeidsplaatsen = Routines.csvintlezen(Arbeidsplaatsenfilenaam, aantal_lege_regels=1)

    Inwonersperklasse = Routines.csvintlezen(Inwonersperklassenaam, aantal_lege_regels=1)
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


    for mot in motieven:
        if mot == 'werk':
            Doelgroep = 'Beroepsbevolking'
        elif mot == 'winkelnietdagelijksonderwijs':
            Doelgroep = 'Leerlingen'
        else:
            Doelgroep = 'Inwoners'
        Groepverdelingfile = os.path.join(SEGSdirectory, scenario, f'Verdeling_over_groepen_{Doelgroep}')
        Verdelingsmatrix = Routines.csvlezen(Groepverdelingfile, aantal_lege_regels=1)
        print('Verdelingsmatrix 4 is', Verdelingsmatrix[4])
        Verdelingstransmatrix = Berekeningen.Transponeren(Verdelingsmatrix)

        for ds in dagsoort:
            Combinatiedirectory = os.path.join ( Basisdirectory, regime, mot, 'Gewichten', 'Combinaties', ds)
            Enkelemodaliteitdirectory = os.path.join ( Basisdirectory, regime, mot, 'Gewichten', ds)
            Concurrentiedirectory = os.path.join (Basisdirectory, Projectbestandsnaam, 'Resultaten', 'Concurrentie',
                                                  'arbeidsplaatsen',  ds)
            Herkomstendirectory = os.path.join ( Basisdirectory, Projectbestandsnaam, 'Resultaten' , 'Herkomsten', ds )
            #Combinatiedirectory = os.path.join ( Skimsdirectory, 'Gewichten', 'Combinaties', Scenario, 'Restdag')
            #Enkelemodaliteitdirectory = os.path.join ( Skimsdirectory, 'Gewichten', Scenario, 'Restdag')
            #Concurrentiedirectory = os.path.join (Skimsdirectory, 'Concurrrentie', 'arbeidsplaatsen', Naamuitvoer)
            os.makedirs (Concurrentiedirectory, exist_ok=True)

            for inkgr in inkgroepen:

                # Eerst de fiets
                print ( 'We zijn het nu aan het uitrekenen voor de inkomensgroep', inkgr )
                for mod in modaliteiten:
                    Bijhoudlijst = Routines.lijstvolnullen(len(Arbeidsplaatsen))
                    for gr in Groepen:
                        print ( 'Bezig met Groep ', gr )
                        ink = Routines.inkomensgroepbepalen ( gr )
                        if inkgr == ink or inkgr == 'alle':
                            vk = Routines.vindvoorkeur ( gr, mod )
                            if mod == 'Fiets' or mod == 'EFiets':
                                if vk == 'Fiets':
                                    vkklad = 'Fiets'
                                else:
                                    vkklad = ''

                                Fietsfilenaam = os.path.join ( Enkelemodaliteitdirectory, f'{mod}_vk{vkklad}' )
                                Fietsmatrix = Routines.csvlezen ( Fietsfilenaam )
                                print ( 'Lengte Fietsmatrix is', len ( Fietsmatrix ) )
                                Bereikfilenaam = os.path.join(Herkomstendirectory,f'Totaal_{mod}_{inkgr}')
                                Bereik = Routines.csvintlezen (Bereikfilenaam)
                                Dezegroeplijst = bereken_concurrentie ( Fietsmatrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen)

                                for i in range ( 0, len ( Fietsmatrix ) ):
                                    if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                        Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                        Bijhoudlijst[i] +=  Bijhoudklad

                            elif mod == 'Auto' :
                                String = Routines.enkelegroep ( mod, gr )
                                print ( String )
                                if 'WelAuto' in gr:
                                    for srtbr in soortbrandstof:
                                        AutoFilenaam = os.path.join(Enkelemodaliteitdirectory, srtbr,
                                                                    f'{String}_vk{vk}_{ink}')
                                        print('Filenaam is', AutoFilenaam)
                                        Matrix = Routines.csvlezen(AutoFilenaam)
                                        Bereikfilenaam = os.path.join(Herkomstendirectory,f'Totaal_{mod}_{inkgr}')
                                        Bereik = Routines.csvintlezen (Bereikfilenaam)
                                        Dezegroeplijst1 = bereken_concurrentie ( Matrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen)
                                        if srtbr == 'elektrisch':
                                            K = percentageelektrisch.get(inkgr) / 100
                                            print('aandeel elektrisch is', K)
                                            DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                        else:
                                            L = 1 - percentageelektrisch.get(inkgr) / 100
                                            print('aandeel fossiel is', L)
                                            DezegroeplijstF = [x * L for x in Dezegroeplijst1]
                                    for i in range(len(Matrix)):
                                        Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                            Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                            Bijhoudlijst[i] += Bijhoudklad
                                else:
                                    AutoFilenaam = os.path.join(Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}')
                                    print('Filenaam is', AutoFilenaam)
                                    Matrix = Routines.csvlezen(AutoFilenaam)
                                    Bereikfilenaam = os.path.join(Herkomstendirectory, f'Totaal_{mod}_{inkgr}')
                                    Bereik = Routines.csvintlezen(Bereikfilenaam)
                                    Dezegroeplijst = bereken_concurrentie(Matrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen)
                                    for i in range(len(Matrix)):
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                            Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                            Bijhoudlijst[i] += Bijhoudklad
                            elif mod == 'OV':
                                String = Routines.enkelegroep(mod, gr)
                                print(String)
                                OVFilenaam = os.path.join(Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}')
                                print('Filenaam is', OVFilenaam)
                                Matrix = Routines.csvlezen(OVFilenaam)
                                Bereikfilenaam = os.path.join(Herkomstendirectory, f'Totaal_{mod}_{inkgr}')
                                Bereik = Routines.csvintlezen(Bereikfilenaam)
                                Dezegroeplijst = bereken_concurrentie(Matrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen)
                                for i in range(len(Matrix)):
                                    if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                        Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)] / \
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                        Bijhoudlijst[i] += Bijhoudklad

                            else:
                                String = combigroep(mod, gr)
                                print('de gr is', gr)
                                print('de string is', String)
                                if String[0] == 'A':
                                    for srtbr in soortbrandstof:
                                        CombiFilenaam = os.path.join(Combinatiedirectory, srtbr,
                                                                     f'{String}_vk{vk}_{ink}')
                                        print('Filenaam is', CombiFilenaam)
                                        Matrix = Routines.csvlezen(CombiFilenaam)
                                        Bereikfilenaam = os.path.join ( Herkomstendirectory, f'Totaal_{mod}_{inkgr}' )
                                        Bereik = Routines.csvintlezen ( Bereikfilenaam )
                                        Dezegroeplijst1 = bereken_concurrentie ( Matrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen)
                                        if srtbr == 'elektrisch':
                                            K = percentageelektrisch.get(inkgr)/100
                                            DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                        else:
                                            K = 1 - percentageelektrisch.get(inkgr)/100
                                            DezegroeplijstF = [x * K for x in Dezegroeplijst1]
                                    for i in range (len(Matrix)):
                                        Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                            Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                            Bijhoudlijst[i] += Bijhoudklad
                                else:
                                    CombiFilenaam = os.path.join (Combinatiedirectory, f'{String}_vk{vk}_{ink}')
                                    print ('Filenaam is', CombiFilenaam)
                                    Matrix = Routines.csvlezen ( CombiFilenaam )
                                    Bereikfilenaam = os.path.join(Herkomstendirectory, f'Totaal_{mod}_{inkgr}')
                                    Bereik = Routines.csvintlezen(Bereikfilenaam)
                                    Dezegroeplijst = bereken_concurrentie(Matrix, Arbeidsplaatsen, Bereik, inkgr, inkgroepen)
                                    for i in range (len(Matrix)):
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                            Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                            Bijhoudlijst[i] += Bijhoudklad

                    Bijhoudfilenaam = os.path.join ( Concurrentiedirectory, f'Totaal_{mod}_{inkgr}' )
                    Routines.csvwegschrijven ( Bijhoudlijst, Bijhoudfilenaam, soort='lijst' )
                # En tot slot alles bij elkaar harken:
                Generaaltotaal_potenties = []
                for mod in modaliteiten:
                    Totaalmodfilenaam = os.path.join ( Concurrentiedirectory, f'Totaal_{mod}_{inkgr}' )
                    Totaalrij = Routines.csvlezen ( Totaalmodfilenaam )
                    Generaaltotaal_potenties.append ( Totaalrij )
                    Generaaltotaaltrans = Berekeningen.Transponeren ( Generaaltotaal_potenties )
                    Uitvoerfilenaam = os.path.join ( Concurrentiedirectory, f'Ontpl_conc_{inkgr}' )
                    Routines.csvwegschrijvenmetheader ( Generaaltotaaltrans, Uitvoerfilenaam, headstring )
                    Routines.xlswegschrijven ( Generaaltotaaltrans, Uitvoerfilenaam, headstringExcel )


            header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
            for mod in modaliteiten:
                Generaalmatrixproduct = []
                Generaalmatrix = []
                for inkgr in inkgroepen:

                    Totaalmodfilenaam = os.path.join (Concurrentiedirectory, f'Totaal_{mod}_{inkgr}')
                    Totaalrij = Routines.csvlezen(Totaalmodfilenaam)
                    Generaalmatrix.append(Totaalrij)
                    Generaaltotaaltrans = Berekeningen.Transponeren(Generaalmatrix)
                for i in range (len(Inwonersperklasse)):
                    Generaalmatrixproduct.append([])
                    for j in range (len(Inwonersperklasse[0])):
                        if Inwonersperklasse[i][j]>0:
                            Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                        else:
                            Generaalmatrixproduct[i].append(0)

                Uitvoerfilenaam = os.path.join(Concurrentiedirectory, f'Ontpl_conc_{mod}')
                Uitvoerfilenaamproduct = os.path.join(Concurrentiedirectory, f'Ontpl_concproduct_{mod}')
                Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, header)
                Routines.xlswegschrijven(Generaalmatrixproduct,Uitvoerfilenaamproduct, header)
