def correctie_voor_parkeren (Basisdirectory, Parkeerdirectory, motief, aantal_groepen=20):
    import Routines
    import Berekeningen
    import os
    for groep in range (aantal_groepen+1):
        Autobasisskimfile = Basisdirectory + 'skims/Basis_Auto_' + str (groep)
        Parkeeraankomstenfile = Parkeerdirectory  + 'aankomstzoektijd'
        Parkeervertrekkenfile = Parkeerdirectory + 'vertrekzoektijd'
        Autobasisskim = Routines.csvlezen ( Autobasisskimfile )
        if not os.path.exists(Parkeeraankomstenfile):
            Parkeerexcelfile = Parkeerdirectory + 'Parkeertabel.xlsx'
            Parkeertijden=Routines.matrixvuller(Parkeerexcelfile,2, sheetnaam = 'Blad1')
            Parkeeraankomsten = [sub[0] for sub in Parkeertijden]
            Parkeervertrekken = [sub[1] for sub in Parkeertijden]
            Routines.csvwegschrijven (Parkeeraankomsten, Parkeeraankomstenfile, soort='lijst')
            Routines.csvwegschrijven (Parkeervertrekken, Parkeervertrekkenfile, soort='lijst')
        else:
            Parkeeraankomsten = Routines.csvlezen ( Parkeeraankomstenfile )
            Parkeervertrekken = Routines.csvlezen ( Parkeervertrekkenfile )
        Nieuweskim = Berekeningen.parkeeroptel( Parkeeraankomsten, Parkeervertrekken, Autobasisskim )
        Uitvoerfile = Basisdirectory + motief + '/skims/Auto_' + str(groep)
        Routines.csvwegschrijven(Nieuweskim, Uitvoerfile)

def correctie_fiets_vs_auto (Basisdirectory, motief, aantal_groepen=20):
    import Routines
    import Berekeningen
    for groep in range ( aantal_groepen+1 ):
        Autoskimfile = Basisdirectory + motief + '/skims/Auto_' + str ( groep )
        Fietsskimfile = Basisdirectory + 'skims/Fiets_' + str ( groep )
        Autoskimmatrix = Routines.csvlezen ( Autoskimfile )
        Fietsskimmatrix = Routines.csvlezen ( Fietsskimfile )
        Nieuwe_Auto_matrix = Berekeningen.correctie_voor_korter_fietsen_dan_auto( Fietsskimmatrix, Autoskimmatrix )
        Uitvoerfile_Auto = Basisdirectory + motief + '/skims/Auto_' + str(groep)
        Uitvoerfile_Fiets = Basisdirectory + motief + '/skims/Fiets_' + str(groep)
        Routines.csvwegschrijven(Nieuwe_Auto_matrix, Uitvoerfile_Auto)
        Routines.csvwegschrijven ( Fietsskimmatrix, Uitvoerfile_Fiets )


def parkeeroptel (Parkeeraankomsten, Parkeervertrekken, Autobasisskim) :

    Parkeeropteltijd = []
    lengte = len ( Parkeeraankomsten )
    for getal1, getal2 in zip ( Parkeeraankomsten, Parkeervertrekken ):
        Parkeeropteltijd.append ( getal1 + getal2 )
    deur_tot_deur_reistijd_auto = []
    for r in range ( lengte ):
        deur_tot_deur_reistijd_auto.append ( [] )
        for c in range ( lengte ):
            deur_tot_deur_reistijd_auto[r].append (
                Autobasisskim[r][c] + (Parkeeropteltijd[r] + Parkeeropteltijd[c]) / 2 )
    return deur_tot_deur_reistijd_auto

def correctie_voor_korter_fietsen_dan_auto (fietsskim,autoskim, omvang_matrix=1425):
    for r in range (omvang_matrix):
        for c in range (omvang_matrix):
            if fietsskim[r][c] < 12.5 and fietsskim[r][c] < autoskim[r][c] + 7.5 :
                autoskim [r][c] = 9999
    return autoskim

def aanpassingen_zonder_auto_en_ov (Basisdirectory, motief, aantal_groepen = 20):
    import Berekeningen
    import Routines
    import Invoer
    for groep in range (aantal_groepen+1):
        OVskimfile = Basisdirectory + 'skims/OV_' + str ( groep )
        OVskim = Routines.csvlezen ( OVskimfile )
        NieuweOVskim = Berekeningen.correctie_voor_reizen_binnen_zone( OVskim )
        NieuweOVskimfile = Basisdirectory + motief + '/skims/OV_' + str ( groep)
        Routines.csvwegschrijven(NieuweOVskim, NieuweOVskimfile)

    groepen_zonder_auto = Invoer.welke_hebben_geen_auto()
    for groep in groepen_zonder_auto:
        Autoskimfile = Basisdirectory + motief + '/skims/Auto_' + str ( groep )
        Autoskim = Routines.csvlezen ( Autoskimfile )
        NieuweAutoskim = Berekeningen.correctie_voor_reizen_binnen_zone( Autoskim )
        NieuweAutoskimfile = Basisdirectory + motief + '/skims/Auto_' + str ( groep )
        Routines.csvwegschrijven(NieuweAutoskim, NieuweAutoskimfile)



def correctie_voor_reizen_binnen_zone (skim, omvang_matrix = 1425):
    for r in range (omvang_matrix):
        skim[r][r] = 9999
    return skim

def gewichten (skim, wegingstriplet) :

    import math
    alpha = wegingstriplet[0]
    omega = wegingstriplet[1]
    weging = wegingstriplet[2]
    Gewichtenmatrix = []

    for r in range(0, len(skim)):
        Gewichtenmatrix.append([])
        for k in range(0, len(skim)):
            ervaren_reistijd = skim[r][k]
            if ervaren_reistijd  < 180:
                reistijdwaarde = (1 / (1 + math.exp((-omega + ervaren_reistijd)*alpha)))*weging
            else:
                reistijdwaarde = 0
            if reistijdwaarde < 0.001 :
                reistijdwaarde = 0
            Gewichtenmatrix[r].append( int(10000*reistijdwaarde) )
    return Gewichtenmatrix

def Berekenengewichten_en_wegschrijven (Motievendirectory, aantal_groepen = 20):
    import Routines
    import Berekeningen
    aantal_groepen = 20
    vervoerswijze = ['Fiets', 'Efiets', 'Auto', 'OV']
    Skimdirectory = Motievendirectory + 'skims/'
    Constantendirectory =Motievendirectory + '/Reistijdvervalscurve/'
    Gewichtendirectory = Motievendirectory + '/Gewichten/'
    for vvw in vervoerswijze:
        Alphasfilenaam = Constantendirectory + 'Alphas_' + vvw
        Omegasfilenaam = Constantendirectory + 'Omegas_' + vvw
        Alpharijtje = Routines.csvlezen ( Alphasfilenaam )
        Omegarijtje = Routines.csvlezen ( Omegasfilenaam )
        for groep in range ( aantal_groepen + 1 ):
            if vvw == 'Efiets':
                vvskim = 'Fiets'
            else:
                vvskim = vvw
            Invoernaam2 = Skimdirectory + vvskim + '_' + str ( groep )
            Skimmatrix = Routines.csvlezen ( Invoernaam2 )
            Gewichtenmatrix = Berekeningen.gewichten ( Skimmatrix, Alpharijtje[groep], Omegarijtje[groep] )
            Uitvoernaam = Gewichtendirectory + vvw + '_' + str ( groep )
            Routines.csvwegschrijven ( Gewichtenmatrix, Uitvoernaam )


def berekenen_combigewichten(Gewichtendirectory, aantal_groepen=20, aantal_zones = 1425):

    import Routines

    vervoerswijzen = ['Fiets', 'EFiets', 'Auto', 'OV']
    matrices = {}

    for groep in range (aantal_groepen+1):
        elementnummer = 0
        while elementnummer <4:
            vvw = vervoerswijzen[elementnummer]
            filenaam = Gewichtendirectory + vvw + '_' + str(groep)
            matrixnaam = 'matrix'+ vvw
            matrices[matrixnaam] = Routines.csvlezen(filenaam)
            elementnummer = elementnummer + 1
        for vvw in vervoerswijzen:
            for vvw2 in vervoerswijzen:
                if vervoerswijzen.index ( vvw2 ) > vervoerswijzen.index ( vvw ):
                    if vvw[-1] == vvw2[-1]:
                        continue
                    else:
                        matrix1 = matrices['matrix' + vvw]
                        matrix2 = matrices['matrix' + vvw2]
                        maxmatrix = []
                        for r in range ( 0, aantal_zones ):
                            maxmatrix.append ( [] )
                            for k in range ( 0, aantal_zones ):
                                maxmatrix[r].append ( max ( matrix1[r][k], matrix2[r][k] ) )

                        bestemmingen_wegschrijfnaam = Gewichtendirectory + vvw + '_' + vvw2 + '_' + str (
                            groep )
                    Routines.csvwegschrijven ( maxmatrix, bestemmingen_wegschrijfnaam )

                    for vvw3 in vervoerswijzen:
                        if vervoerswijzen.index ( vvw3 ) > vervoerswijzen.index ( vvw2 ):
                            matrix3 = matrices['matrix' + vvw3]
                            maxmatrix2 = []
                            for r in range ( 0, aantal_zones ):
                                maxmatrix2.append ( [] )
                                for k in range ( 0, aantal_zones ):
                                    maxmatrix2[r].append ( max ( matrix1[r][k], matrix2[r][k], matrix3[r][k] ) )
                            bestemmingen_wegschrijfnaam = Gewichtendirectory + vvw + '_' + vvw2 + '_' + vvw3 + '_' + str (
                                groep )
                            Routines.csvwegschrijven ( maxmatrix2, bestemmingen_wegschrijfnaam )

def bereken_best_of_herk (Gewichtenmatrix, SEGSlijst, aantal_zones = 1425):
    Aantal_bestemmingen_matrix = []
    for z in range ( aantal_zones ):
        Aantal_bestemmingen_matrix.append ( [] )
        for i in range (aantal_zones) :
            Aantal_bestemmingen_matrix[z].append ( Gewichtenmatrix [z][i] * SEGSlijst[i] )
    return Aantal_bestemmingen_matrix

def bereken_alle_bestemmings_of_herkomstmatrices (Basisdirectory, SEGSdirectory, motief, functie = "bestemming", aantal_groepen = 20,
                                                  aantal_zones = 1425) :
    import Routines
    import Berekeningen
    vervoerscombis = ['Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV',
                      'Fiets_Auto_OV', 'Efiets_Auto_OV']
    if functie == "bestemming" :
        if motief == "werk" :
            best_of_herk = "arbeidsplaatsen"
        else :
            best_of_herk = motief
    else :
        best_of_herk = "inwoners"
    Motievendirectory = Basisdirectory + motief + '/'
    Gewichtendirectory = Motievendirectory + 'Gewichten/'
    Best_of_herk_directory = Motievendirectory + 'Bestemmingen/' + best_of_herk + '/'
    SEGSfilenaam = SEGSdirectory + best_of_herk
    SEGSlijst = Routines.csvlezen ( SEGSfilenaam )
    for vvwcombi in vervoerscombis:
        print ("Bezig met: ", vvwcombi)
        for groep in range ( 0, aantal_groepen + 1 ):
            Gewichtenmatrix = Routines.csvlezen(Gewichtendirectory + vvwcombi + '_' + str (groep))
            Aantal_herk_of_best_matrix = Berekeningen.bereken_best_of_herk ( Gewichtenmatrix, SEGSlijst )
            bestemmingen_wegschrijfnaam = Best_of_herk_directory + vvwcombi + '_' + str ( groep )
            Routines.csvwegschrijven ( Aantal_herk_of_best_matrix, bestemmingen_wegschrijfnaam )

def berekenen_ontplooiingstotalen_per_groep (Motievendirectory, type_bestemming, aantal_zones = 1425, aantal_groepen = 20):
    import Routines
    vervoerscombis = ['Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV',
                      'Fiets_Auto_OV', 'Efiets_Auto_OV']
    Bestemmingendirectory = Motievendirectory + 'bestemmingen/' + type_bestemming +'/'
    Totalendirectory = Motievendirectory + 'Totalenpergroep/'
    for vvwcombi in vervoerscombis:
        print ( "Bezig met : ", vvwcombi )
        for groep in range ( 0, aantal_groepen + 1 ):
            Inputfilenaam = Bestemmingendirectory + vvwcombi + '_' + str(groep)
            bestemmingsmatrix = Routines.csvlezen (Inputfilenaam)
            somtotaal = [sum ( x ) for x in bestemmingsmatrix]
            sommen_wegschrijfnaam = Totalendirectory + vvwcombi + '_' + str ( groep )
            Routines.csvwegschrijven ( somtotaal, sommen_wegschrijfnaam, soort = 'lijst' )


def maak_potentielijst (Basisdirectory, motief, correctielijst, aantal_groepen = 20, aantal_zones = 1425, soort_bestemming = "inwoners"):

    import Routines
    vervoerscombis = ['Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV',
                      'Fiets_Auto_OV', 'Efiets_Auto_OV']
    Herkomstendirectory = Basisdirectory + motief + '/Bestemmingen/' + soort_bestemming +'/'
    Bevolkingssamenstelling_directory = Basisdirectory +'Bevolkingssamenstelling/'
    Zonesamenstellingsgfilenaam = Bevolkingssamenstelling_directory + 'Alle_buurten'
    Buurtmatrix = Routines.csvlezen ( Zonesamenstellingsgfilenaam )
    Totaallijst = []
    for vvcombis in vervoerscombis:
        print ( "Bezig met : ", vvcombis )
        Tweedimensionele_matrix = []
        Multidimensionele_matrix = []
        Finale_lijst = []
        for groep in range ( 1, aantal_groepen + 1 ):
            Filenaam1 = Herkomstendirectory + vvcombis + '_' + str ( groep )
            Matrix1 = Routines.csvlezen(Filenaam1)
            if len(correctielijst) >0:
                for groep in range (aantal_groepen):
                    if correctielijst[groep] != 1:
                        Kolom = [sub[groep] for sub in Matrix1]
                        Kolom = [x*correctielijst[groep] for x in Kolom]
                        for i in range (aantal_zones):
                            Matrix1[i][groep]=Kolom[i]
            Multidimensionele_matrix.append ( Matrix1 )
        for i in range ( aantal_zones ):
            Tweedimensionele_matrix.append ( [] )
            for groep in range ( 1, aantal_groepen + 1 ):
                Matrix = Multidimensionele_matrix[groep - 1]
                Lijst1 = Matrix[i]
                Lijst2 = [sub[groep - 1] for sub in Buurtmatrix]
                Vermenigvuldig = []
                for Getal1, Getal2 in zip ( Lijst1, Lijst2 ):
                    Vermenigvuldig.append ( Getal1 * Getal2 )
                Tweedimensionele_matrix[i].append ( sum ( Vermenigvuldig ) )
            Finale_lijst.append ( sum ( Tweedimensionele_matrix[i] ) )
            Totaallijst.append ( Finale_lijst )
        Uitfile_A = Basisdirectory + motief + '/Potentie/' + vvcombis + '_matrix'
        Uitfile_B = Basisdirectory + motief + '/Potentie/' + vvcombis + '_lijst'
        Routines.csvwegschrijven ( Tweedimensionele_matrix, Uitfile_A )
        Routines.csvwegschrijven ( Finale_lijst, Uitfile_B, soort="lijst" )
        Uitvoerfile = Basisdirectory + motief + '/UitvoerExcels/potentie_voor_bedrijven'
        Headers = 'Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV', 'Fiets_Auto_OV', 'Efiets_Auto_OV'
        Getallenlijst = Routines.getallenlijst_maken ( 1425 )
        Routines.xlswegschrijven_totalen ( Totaallijst, Headers, Getallenlijst, Uitvoerfile )

def totalen_over_bevolking(Basisdirectory, motief,  aantal_zones = 1425, aantal_groepen = 20):
    import Routines
    vervoerscombis = ['Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV',
                      'Fiets_Auto_OV', 'Efiets_Auto_OV']
    Totalenpergroep_directory = Basisdirectory + motief + '/Totalenpergroep/'
    Bevolkingssamenstelling_directory = Basisdirectory + 'Bevolkingssamenstelling/'
    Zonesamenstellingsgfilenaam = Bevolkingssamenstelling_directory + 'Alle_buurten'
    Buurtmatrix = Routines.csvlezen ( Zonesamenstellingsgfilenaam )
    Correctielijst = Routines.csvlezen (Basisdirectory + motief +'/correctielijst')
    Totaallijst = []
    for vvcombis in vervoerscombis:
        print ( "Bezig met : ", vvcombis )
        Tweedimensionele_matrix = []
        Finale_lijst = []
# Eerst maken we een totaalmatrix met als rijen de groepen, als kolommen de zones en als waarde het aantal bestemmingen
        for groep in range ( 1, aantal_groepen + 1 ):
            Filenaam1 = Totalenpergroep_directory + vvcombis + '_' + str ( groep )
            Lijst1 = Routines.csvlezen ( Filenaam1 )
            Factor = 1
            if len (Correctielijst)>0:
                Factor = Correctielijst [groep-1]
            Lijst1 = [x * Factor for x in Lijst1]
            Tweedimensionele_matrix.append ( Lijst1 )
        FilenaamZ = Basisdirectory + '2D_' + vvcombis
        Routines.csvwegschrijven ( Tweedimensionele_matrix, FilenaamZ )
        for i in range ( aantal_zones ):
            Lijst1 = [sub[i] for sub in Tweedimensionele_matrix]
            Lijst2 = Buurtmatrix[i]
            Vermenigvuldig = []
            for Getal1, Getal2 in zip ( Lijst1, Lijst2 ):
                Vermenigvuldig.append ( Getal1 * Getal2 )
            Finale_lijst.append ( sum ( Vermenigvuldig ) )
        Totaallijst.append (Finale_lijst)
        Uitfile_A = Basisdirectory + motief + '/Totalen_over_bevolkingssamenstelling/' + vvcombis
        Routines.csvwegschrijven ( Finale_lijst, Uitfile_A, soort="lijst" )
        Uitfile_B = Basisdirectory + motief + '/Totalen_over_bevolkingssamenstelling/' + vvcombis + '_matrix'
        Routines.csvwegschrijven ( Tweedimensionele_matrix, Uitfile_B )
    Routines.csvwegschrijven ( Totaallijst, 'C:/Users/hansv/OneDrive/Documents/Uitprobeersels/dcef' )
    Uitvoerfile = Basisdirectory + motief + '/UitvoerExcels/ontplooiing_arbeidsplaatsen'
    Headers = 'Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV', 'Fiets_Auto_OV', 'Efiets_Auto_OV'
    Getallenlijst = Routines.getallenlijst_maken ( 1425 )
    Routines.xlswegschrijven_totalen ( Totaallijst, Headers, Getallenlijst, Uitvoerfile )


def Mega_matrix_maken(Bestemmingen_directory, Megamatrix_directory, Correctielijst, vvcombis, aantal_groepen = 20, aantal_zones = 1425):
    import Routines
    Mega_matrix = []
    bestemmingen = {}

    for groep in range ( 1, aantal_groepen + 1 ):
        Filenaam1 = Bestemmingen_directory + vvcombis + '_' + str ( groep )
        bestemmingen['Bestemming' + str(groep)] = Routines.csvlezen ( Filenaam1 )
    for i in range (aantal_zones):
        Mega_matrix.append([])
        for j in range (aantal_zones):
            Mega_matrix[i].append([])
            for groep in range ( 1, aantal_groepen + 1 ):
                if len(Correctielijst)>0:
                    Factor = Correctielijst[groep-1]
                else:
                    Factor = 1
                bestemming = bestemmingen['Bestemming' + str(groep)]
                Mega_matrix[i][j].append(bestemming[i][j]*Factor)
        if i//100 == i/100:
            print(i)
    import pickle
    Megamatrix_filenaam = Megamatrix_directory + vvcombis + '.bin'
    with open ( Megamatrix_filenaam, 'wb') as f:
        pickle.dump ( Mega_matrix, f )
    return Mega_matrix

def TweeD_matrix_maken (Mega_matrix, Buurtmatrix, aantal_groepen = 20, aantal_zones = 1425):
    Tweedimensionele_matrix =[]
    for i in range ( aantal_zones ):
        Tweedimensionele_matrix.append ( [] )
        if i // 100 == i / 100:
            print ( i )
        for j in range ( aantal_zones ):
            Lijst1 = Mega_matrix[i][j]
            Lijst2 = Buurtmatrix[i]
            Vermenigvuldig = []
            for Getal1, Getal2 in zip ( Lijst1, Lijst2 ):
                Vermenigvuldig.append ( Getal1 * Getal2 )
            Tweedimensionele_matrix[i].append ( sum ( Vermenigvuldig ) )
    return Tweedimensionele_matrix

def Concurrentie_positie_herk_of_bestemming (Basisdirectory, motief, h_of_b,aantal_zones = 1425, aantal_groepen = 20) :
    import Routines
    import os
    import pickle
    import Berekeningen

    Correctielijst = Routines.csvlezen (Basisdirectory + motief +'/correctielijst')
    vervoerscombis = ['Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV',
                      'Fiets_Auto_OV', 'Efiets_Auto_OV']
    if h_of_b == "herkomst":
        h_of_b_soort = "inwoners"
    else:
        if motief == "werk":
            h_of_b_soort = "arbeidsplaatsen"
        else:
            h_of_b_soort = motief

    H_of_b_directory = Basisdirectory + motief + '/Bestemmingen/' + h_of_b_soort + '/'
    Bevolkingssamenstelling_directory = Basisdirectory + 'Bevolkingssamenstelling/'
    Zonesamenstellingsgfilenaam = Bevolkingssamenstelling_directory + 'Alle_buurten'
    Buurtmatrix = Routines.csvlezen ( Zonesamenstellingsgfilenaam )
    Megamatrix_directory = Basisdirectory + motief + '/Megamatrix/' + h_of_b_soort +'/'
    Alleverhoudingenuitvoer = []
    for vvcombis in vervoerscombis:
        print ( "Bezig met : ", vvcombis )
        filenaam = Megamatrix_directory + vvcombis + '.bin'
        if os.path.exists ( filenaam ):
            with open ( filenaam, 'rb' ) as f:
                Mega_matrix = pickle.load ( f )
        else:
            Mega_matrix = Berekeningen.Mega_matrix_maken ( H_of_b_directory, Megamatrix_directory, Correctielijst, vvcombis )

        filenaam2 = Megamatrix_directory + '2D_' + vvcombis

        if os.path.exists ( filenaam2 ):
            Tweedimensionele_matrix = Routines.csvlezen ( filenaam2 )
        else:
            Tweedimensionele_matrix = Berekeningen.TweeD_matrix_maken ( Mega_matrix, Buurtmatrix )
            TweeDmatrix_filenaam = Megamatrix_directory + '2D_' + vvcombis
            Routines.csvwegschrijven ( Tweedimensionele_matrix, TweeDmatrix_filenaam )


        if h_of_b == "bestemmingen":
            Werkpotentiefile = Basisdirectory + motief + '/Potentie/' + vvcombis + '_lijst'
            Vermenigvuldigingsfactor = 2.1   # Deze is om te corrigeren voor de verhouding tussen inwoners en arbeidsplaatsen
        else:
            Werkpotentiefile = Basisdirectory + motief + '/Totalen_over_bevolkingssamenstelling/' + vvcombis
            Vermenigvuldigingsfactor = 1/2.1  # Deze is om te corrigeren voor de verhouding tussen inwoners en arbeidsplaatsen
        Potentie_lijst = Routines.csvlezen ( Werkpotentiefile )
        Sommenlijst = [sum(x) for x in Tweedimensionele_matrix]
        Verhouding = []
        for i in range (aantal_zones):
            if Potentie_lijst[i]==0:
                Potentie_lijst[i] = 999999999
        for i in range (aantal_zones):
            Verhouding.append(Sommenlijst[i] * Vermenigvuldigingsfactor / Potentie_lijst[i])
        Concurrentiedirectory = Basisdirectory + motief + '/Concurrentie/' + h_of_b_soort +'/'
        Aandeel_filenaam = Concurrentiedirectory + vvcombis
        Routines.csvwegschrijven(Verhouding, Aandeel_filenaam, soort = 'lijst')
        Alleverhoudingenuitvoer.append(Verhouding)
    Uitvoerfile = Basisdirectory + motief + '/UitvoerExcels/concurrentie_' + h_of_b_soort
    Headers = 'Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV', 'Fiets_Auto_OV', 'Efiets_Auto_OV'
    Getallenlijst = Routines.getallenlijst_maken ( 1425 )
    Routines.xlswegschrijven_totalen ( Alleverhoudingenuitvoer, Headers, Getallenlijst, Uitvoerfile )

def Transponeren (Matrix) :
    Transp = [[Matrix[j][i] for j in range(len(Matrix))] for i in range(len(Matrix[0]))]
    return Transp


def bereken_concurrentie (Matrix, Beroepsbevolking, Bereik, inkgr, inkgroepen):
    Dezegroeplijst = []
    Beroepsbevolkingtrans = Transponeren ( Beroepsbevolking )
    for i in range ( len ( Matrix ) ):
        Gewogenmatrix = []
        for Getal1, Getal2, Getal3 in zip ( Matrix[i], Bereik, Beroepsbevolkingtrans[inkgroepen.index ( inkgr )] ):
            if Getal2 > 0:
                Gewogenmatrix.append ( Getal1 * Getal3 / Getal2 )
            else :
                Gewogenmatrix.append (0)
        Dezegroeplijst.append ( sum ( Gewogenmatrix ) )
    return Dezegroeplijst
