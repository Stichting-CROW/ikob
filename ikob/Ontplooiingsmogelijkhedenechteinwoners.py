import Routines
import Berekeningen
import os


def inkomensgroepbepalen(naam):
    if naam[-4:] == 'hoog':
        if naam[-10:] == 'middelhoog':
            return 'middelhoog'
        else:
            return 'hoog'
    elif naam[-4:] == 'laag':
        if naam[-10:] == 'middellaag':
            return 'middellaag'
        else:
            return 'laag'
    else:
        return ''

def vindvoorkeur(naam, mod):
    if 'vk' in naam:
        Beginvk = naam.find ('vk')
        if naam[Beginvk + 2] == "A":
            return 'Auto'
        elif naam[Beginvk + 2] == "N":
            return 'Neutraal'
        elif naam[Beginvk + 2] == "O":
            return 'OV'
        elif naam[Beginvk + 2] == "F":
            return 'Fiets'
        else:
            return ''
    elif 'GratisAuto' in naam:
        if 'GratisAuto_GratisOV' in naam and 'OV' in mod and 'Auto' in mod:
            return 'Neutraal'
        else:
            if 'Auto' in mod:
                return 'Auto'
            else:
                return 'OV'
    elif 'GratisOV' in naam:
        return 'OV'
    else:
        return ''

def enkelegroep(mod, gr) :
    if mod == 'Auto':
        if 'GratisAuto' in gr:
            return 'GratisAuto'
        elif 'Wel' in gr:
            return 'Auto'
        if 'GeenAuto' in gr:
            return 'GeenAuto'
        if 'GeenRijbewijs' in gr:
            return 'GeenRijbewijs'
    if mod == 'OV':
        if 'GratisOV' in gr:
            return 'GratisOV'
        else:
            return 'OV'

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


def Lijstvolnullen(lengte) :
    Lijst = [] 
    for i in range (lengte) :
        Lijst.append(0)
    return Lijst

def bereken_potenties (Matrix, Arbeidsplaatsen, Beroepsbevolkingsverdeling, Beroepsbevolkingaandeel, inkgr, gr, inkgroepen, Groepen):
    Dezegroeplijst = []
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2 in zip ( Matrix[i], Arbeidsplaatsen[inkgroepen.index ( inkgr )] ):
            Gewogenmatrix.append ( Getal1 * Getal2 * Beroepsbevolkingsverdeling[Groepen.index ( gr )][i] )
        if Beroepsbevolkingaandeel[i]>0:
            Dezegroeplijst.append ( sum ( Gewogenmatrix )/(Beroepsbevolkingaandeel[i]) )
        else:
            Dezegroeplijst.append ( 0 )
    return Dezegroeplijst

def bereken_potenties_nietwerk (Matrix, Bestemmingen, Inwonersverdeling, Inwonersaandeel, gr, Groepen):
    Dezegroeplijst = []
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2 in zip ( Matrix[i], Bestemmingen ):
            Gewogenmatrix.append ( Getal1 * Getal2 * Inwonersverdeling[Groepen.index ( gr )][i] )
        if Inwonersaandeel[i]>0:
            Dezegroeplijst.append ( sum ( Gewogenmatrix )/(Inwonersaandeel[i]) )
        else:
            Dezegroeplijst.append ( 0 )
    return Dezegroeplijst


def ontplooingsmogelijkheden_echte_inwoners(config):
    Projectbestandsnaam = config['__filename__']  # nieuw automatisch toegevoegd config item.
    project_config = config['project']
    paden_config = config['project']['paden']
    #verdeling_config = config['verdeling']
    skims_config = config ['skims']
    verdeling_config = config ['verdeling']
    dagsoort = skims_config['dagsoort']
    #ontpl_config = config['ontplooiing']

    # Ophalen van instellingen
    Basisdirectory = paden_config['skims_directory']
    SEGSdirectory = paden_config['segs_directory']
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config ['motieven']
    autobezitgroepen = project_config ['welke_groepen']
    inkgroepen = project_config ['welke_inkomensgroepen']
    percentageelektrisch = verdeling_config ['Percelektrisch']
    print (percentageelektrisch)

    #Scenario = project_config['scenario']
    #Grverdelingfile = verdeling_config['uitvoernaam']

    if 'alle groepen' in autobezitgroepen:
        Basisgroepen = ['GratisAuto', 'GratisAuto_GratisOV','WelAuto_GratisOV','WelAuto_vkAuto',
               'WelAuto_vkNeutraal', 'WelAuto_vkFiets','WelAuto_vkOV','GeenAuto_GratisOV',
               'GeenAuto_vkNeutraal','GeenAuto_vkFiets', 'GeenAuto_vkOV','GeenRijbewijs_GratisOV',
               'GeenRijbewijs_vkNeutraal', 'GeenRijbewijs_vkFiets', 'GeenRijbewijs_vkOV']
    else:
        Basisgroepen = ['GratisAuto', 'GratisAuto_GratisOV','WelAuto_GratisOV','WelAuto_vkAuto',
               'WelAuto_vkNeutraal', 'WelAuto_vkFiets','WelAuto_vkOV']

    print ('autobezitgroepen zijn', autobezitgroepen)

    Groepen = []
    for inkgr in inkgroepen:
        for bg in Basisgroepen:
            Groepen.append(f'{bg}_{inkgr}')
    print (Groepen)
    """
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
    """
    modaliteiten = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets' ]
    enkelemodaliteiten = ['Fiets', 'Auto', 'OV']
    fiets = ['Fiets']
    OVauto = ['OV', 'Auto']
    voorkeurenfiets = ['', 'Fiets']
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']
    headstringExcel=['Zone', 'Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']
    soortbrandstof = ['fossiel','elektrisch']
    Vermenigvuldig = []
    print (motieven)

    #Grverdelingfile=Grverdelingfile.replace('.csv','')

    #Inkomensverdelingsfilenaam = os.path.join (SEGSdirectory, 'Inkomensverdeling_per_zone')
    #Inkomensverdeling = Routines.csvintlezen (Inkomensverdelingsfilenaam, aantal_lege_regels=1)
    if 'winkelnietdagelijksonderwijs' in motieven:
        Beroepsbevolkingperklassenaam = os.path.join(SEGSdirectory, scenario, f'Leerlingen')
        Beroepsbevolkingperklasse = Routines.csvintlezen(Beroepsbevolkingperklassenaam, aantal_lege_regels=1)
        Beroepsbevolkingtotalen = []
        Arbeidsplaatsenfilenaam = os.path.join(SEGSdirectory, scenario, f'Leerlingenplaatsen')
        print(Arbeidsplaatsenfilenaam)
        Arbeidsplaats = Routines.csvintlezen(Arbeidsplaatsenfilenaam, aantal_lege_regels=1)
        Arbeidsplaatsen = Berekeningen.Transponeren(Arbeidsplaats)
        print('Lengte Leerlingenplaatsen is', len(Arbeidsplaats))
    else:
        Beroepsbevolkingperklassenaam = os.path.join (SEGSdirectory, scenario, f'Beroepsbevolking_inkomensklasse')
        Beroepsbevolkingperklasse = Routines.csvintlezen(Beroepsbevolkingperklassenaam, aantal_lege_regels=1)
        Beroepsbevolkingtotalen = []
        Arbeidsplaatsenfilenaam = os.path.join(SEGSdirectory, scenario, f'Arbeidsplaatsen_inkomensklasse')
        print(Arbeidsplaatsenfilenaam)
        Arbeidsplaats = Routines.csvintlezen(Arbeidsplaatsenfilenaam, aantal_lege_regels=1)
        Arbeidsplaatsen = Berekeningen.Transponeren(Arbeidsplaats)
        print('Lengte arbeidsplaatsen is', len(Arbeidsplaats))
    for i in range(len(Beroepsbevolkingperklasse)):
        Beroepsbevolkingtotalen.append(sum(Beroepsbevolkingperklasse[i]))
    if 'sociaal-recreatief' in motieven:
        if '65+' in regime:
            Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'L65plus_inkomensklasse')
        else:
            Inwonersperklassenaam = os.path.join(SEGSdirectory, scenario, f'Inwoners_inkomensklasse')
        Inwonersperklasse = Routines.csvintlezen(Inwonersperklassenaam, aantal_lege_regels=1)
        Inwonerstotalen = []


        for i in range(len(Inwonersperklasse)):
            Inwonerstotalen.append(sum(Inwonersperklasse[i]))

    Inkomensverdeling = []
    for i in range (len(Beroepsbevolkingperklasse)):
        Inkomensverdeling.append([])
        for j in range (len(Beroepsbevolkingperklasse[0])):
            if Beroepsbevolkingtotalen[i]>0:
                Inkomensverdeling[i].append(Beroepsbevolkingperklasse[i][j]/Beroepsbevolkingtotalen[i])
            else:
                Inkomensverdeling[i].append (0)
    Inkomenstransverdeling = Berekeningen.Transponeren (Inkomensverdeling)

    for abg in autobezitgroepen:
        for mot in motieven:
            if mot == 'werk':
                Doelgroep = 'Beroepsbevolking'
            elif mot == 'winkelnietdagelijksonderwijs':
                Doelgroep = 'Leerlingen'
            else:
                Doelgroep = 'Inwoners'
            if abg == 'alle groepen':
                Groepverdelingfile = os.path.join(SEGSdirectory, scenario, f'Verdeling_over_groepen_{Doelgroep}')
            else:
                Groepverdelingfile = os.path.join(SEGSdirectory, scenario, f'Verdeling_over_groepen_{Doelgroep}_alleen_autobezit')
            Verdelingsmatrix = Routines.csvlezen(Groepverdelingfile, aantal_lege_regels=1)
            print('Verdelingsmatrix 4 is', Verdelingsmatrix[4])
            Verdelingstransmatrix = Berekeningen.Transponeren(Verdelingsmatrix)
            for ds in dagsoort:
                Combinatiedirectory = os.path.join ( Basisdirectory, regime, mot, 'Gewichten', 'Combinaties', ds )
                Enkelemodaliteitdirectory = os.path.join ( Basisdirectory, regime, mot, 'Gewichten', ds )
                Totalendirectorybestemmingen = os.path.join ( Basisdirectory, Projectbestandsnaam, 'Resultaten', mot, abg,
                                                              'Bestemmingen', ds )
                os.makedirs ( Totalendirectorybestemmingen, exist_ok=True )
                print ("De bestemmingen komen in",Totalendirectorybestemmingen)
                # Combinatiedirectory = os.path.join ( Skimsdirectory, 'Gewichten', 'Combinaties', Scenario, 'Restdag')
                # Enkelemodaliteitdirectory = os.path.join ( Skimsdirectory, 'Gewichten', Scenario, 'Restdag')
                # Totalendirectorybestemmingen = os.path.join ( Skimsdirectory, 'Bestemmingen', Scenario, 'Restdag', Naamuitvoer)

                for inkgr in inkgroepen:


                    #Eerst de fiets
                    print('We zijn het nu aan het uitrekenen voor de inkomensgroep', inkgr)
                    for mod in modaliteiten:
                        Bijhoudlijst = Lijstvolnullen(len(Arbeidsplaats))
                        for gr in Groepen:
                            ink = inkomensgroepbepalen ( gr )
                            if inkgr == ink or inkgr == 'alle':
                                vk = vindvoorkeur (gr, mod)
                                if mod == 'Fiets' or mod == 'EFiets':
                                    if vk == 'Fiets':
                                        vkklad = 'Fiets'
                                    else:
                                        vkklad = ''
                                    Fietsfilenaam = os.path.join (Enkelemodaliteitdirectory, f'{mod}_vk{vkklad}')
                                    print ('Filenaam is',Fietsfilenaam)
                                    Fietsmatrix = Routines.csvlezen (Fietsfilenaam)
                                    if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                        Dezegroeplijst = bereken_potenties ( Fietsmatrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                             Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                    else:
                                        Dezegroeplijst = bereken_potenties_nietwerk(Fietsmatrix, Inwonerstotalen, Verdelingstransmatrix,
                                                                           Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                           gr, Groepen)
                                    for i in range(0, len(Fietsmatrix) ):
                                        Bijhoudlijst[i]+= int(Dezegroeplijst[i])
                                elif mod == 'Auto':
                                    String = enkelegroep (mod,gr)
                                    print (String)
                                    if 'WelAuto' in gr:
                                        for srtbr in soortbrandstof:
                                            AutoFilenaam = os.path.join(Enkelemodaliteitdirectory, srtbr, f'{String}_vk{vk}_{ink}')
                                            print ('Filenaam is', AutoFilenaam)
                                            Matrix = Routines.csvlezen(AutoFilenaam)
                                            if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                                Dezegroeplijst1 = bereken_potenties ( Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                                     Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                            else:
                                                Dezegroeplijst1 = bereken_potenties_nietwerk(Matrix, Inwonerstotalen, Verdelingstransmatrix,
                                                                                   Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                                   gr, Groepen)
                                            if srtbr == 'elektrisch':
                                                K = percentageelektrisch.get(inkgr)/100
                                                print ('aandeel elektrisch is', K)
                                                DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                            else :
                                                L = 1 - percentageelektrisch.get(inkgr)/100
                                                print ('aandeel fossiel is', L)
                                                DezegroeplijstF = [x * L for x in Dezegroeplijst1]
                                        for i in range (len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                        for i in range(0, len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                    else:
                                        AutoFilenaam = os.path.join(Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}')
                                        print('Filenaam is', AutoFilenaam)
                                        Matrix = Routines.csvlezen(AutoFilenaam)
                                        if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                            Dezegroeplijst = bereken_potenties(Matrix, Arbeidsplaatsen,
                                                                               Verdelingstransmatrix,
                                                                               Inkomenstransverdeling[
                                                                                   inkgroepen.index(inkgr)],
                                                                               inkgr, gr, inkgroepen, Groepen)
                                        else:
                                            Dezegroeplijst = bereken_potenties_nietwerk(Matrix, Inwonerstotalen,
                                                                                        Verdelingstransmatrix,
                                                                                        Inkomenstransverdeling[
                                                                                            inkgroepen.index(inkgr)],
                                                                                        gr, Groepen)
                                        for i in range(0, len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                        print ('Bijhoudlijst niet fossiel is:',Bijhoudlijst)
                                elif mod == 'OV':
                                    String = enkelegroep(mod, gr)
                                    print(String)
                                    OVFilenaam = os.path.join(Enkelemodaliteitdirectory, f'{String}_vk{vk}_{ink}')
                                    print('Filenaam is', OVFilenaam)
                                    Matrix = Routines.csvlezen(OVFilenaam)
                                    if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                        Dezegroeplijst = bereken_potenties(Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                           Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                           inkgr, gr, inkgroepen, Groepen)
                                    else:
                                        Dezegroeplijst = bereken_potenties_nietwerk(Matrix, Inwonerstotalen,
                                                                                    Verdelingstransmatrix,
                                                                                    Inkomenstransverdeling[
                                                                                        inkgroepen.index(inkgr)],
                                                                                    gr, Groepen)
                                    for i in range(0, len(Matrix)):
                                        Bijhoudlijst[i] += int(Dezegroeplijst[i])

                                else:
                                    String = combigroep (mod,gr)
                                    print ('de gr is', gr)
                                    print ('de string is', String)
                                    if String[0] == 'A':
                                        for srtbr in soortbrandstof:
                                            CombiFilenaam = os.path.join(Combinatiedirectory, srtbr,
                                                                        f'{String}_vk{vk}_{ink}')
                                            print ('Filenaam is', CombiFilenaam)
                                            Matrix = Routines.csvlezen(CombiFilenaam)
                                            if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                                Dezegroeplijst1 = bereken_potenties(Matrix, Arbeidsplaatsen,
                                                                                    Verdelingstransmatrix,
                                                                                    Inkomenstransverdeling[
                                                                                        inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                            else:
                                                Dezegroeplijst1 = bereken_potenties_nietwerk(Matrix, Inwonerstotalen,
                                                                                             Verdelingstransmatrix,
                                                                                             Inkomenstransverdeling[
                                                                                                 inkgroepen.index(inkgr)],
                                                                                             gr, Groepen)
                                            if srtbr == 'elektrisch':
                                                K = percentageelektrisch.get(inkgr)/100
                                                DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                            else:
                                                K = 1 - percentageelektrisch.get(inkgr)/100
                                                DezegroeplijstF = [x * K for x in Dezegroeplijst1]
                                        for i in range (len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                        for i in range ( 0, len ( Matrix ) ):
                                            Bijhoudlijst[i] += int ( Dezegroeplijst[i] )
                                    else:
                                        CombiFilenaam = os.path.join (Combinatiedirectory, f'{String}_vk{vk}_{ink}')
                                        print ('Filenaam is', CombiFilenaam)
                                        Matrix = Routines.csvlezen ( CombiFilenaam )

                                        if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                            Dezegroeplijst = bereken_potenties ( Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                                 Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                        else:
                                            Dezegroeplijst = bereken_potenties_nietwerk(Matrix, Inwonerstotalen, Verdelingstransmatrix,
                                                                               Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                               gr, Groepen)
                                        for i in range ( 0, len ( Matrix ) ):
                                            Bijhoudlijst[i] += int ( Dezegroeplijst[i] )
                        Bijhoudfilenaam = os.path.join(Totalendirectorybestemmingen, f'Totaal_{mod}_{inkgr}')
                        Routines.csvwegschrijven (Bijhoudlijst,Bijhoudfilenaam,soort='lijst')
                    # En tot slot alles bij elkaar harken:
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten :
                        Totaalmodfilenaam = os.path.join (Totalendirectorybestemmingen, f'Totaal_{mod}_{inkgr}')
                        Totaalrij = Routines.csvintlezen(Totaalmodfilenaam)
                        Generaaltotaal_potenties.append(Totaalrij)
                    Generaaltotaaltrans = Berekeningen.Transponeren(Generaaltotaal_potenties)
                    Uitvoerfilenaam = os.path.join(Totalendirectorybestemmingen, f'Ontpl_totaal_{inkgr}')
                    Routines.csvwegschrijvenmetheader(Generaaltotaaltrans, Uitvoerfilenaam, headstring)
                    Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, headstringExcel)

                header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        Totaalmodfilenaam = os.path.join (Totalendirectorybestemmingen, f'Totaal_{mod}_{inkgr}')
                        Totaalrij = Routines.csvintlezen(Totaalmodfilenaam)
                        Generaalmatrix.append(Totaalrij)
                    if len(inkgroepen)>1:
                        Generaaltotaaltrans = Berekeningen.Transponeren(Generaalmatrix)
                    else:
                        Generaaltotaaltrans = Generaalmatrix
                    for i in range (len(Beroepsbevolkingperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range (len(Beroepsbevolkingperklasse[0])):
                            if Beroepsbevolkingperklasse[i][j]>0:
                                Generaalmatrixproduct[i].append(int(Generaaltotaaltrans[i][j]*Beroepsbevolkingperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    Uitvoerfilenaam = os.path.join(Totalendirectorybestemmingen, f'Ontpl_totaal_{mod}')
                    Uitvoerfilenaamproduct = os.path.join(Totalendirectorybestemmingen, f'Ontpl_totaalproduct_{mod}')
                    Routines.xlswegschrijven(Generaaltotaaltrans, Uitvoerfilenaam, header)
                    Routines.xlswegschrijven(Generaalmatrixproduct,Uitvoerfilenaamproduct, header)
