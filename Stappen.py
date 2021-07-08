def Stap1 (Basisdirectory, Parkeerdirectory, motief):
    import Berekeningen
    print ('Toepassen parkeerzoektijd en parkeertarieven')
    Berekeningen.correctie_voor_parkeren(Basisdirectory, Parkeerdirectory, motief)
    print ('correctie korte autotijden als fiets sneller is')
    Berekeningen.correctie_fiets_vs_auto(Basisdirectory, motief)
    print ('correctie voor reistijd binnen zone: OV niet in beeld en auto ook niet als je geen auto hebt')
    Berekeningen.aanpassingen_zonder_auto_en_ov(Basisdirectory,motief)

def Stap2 (Basisdirectory, motief ):
    import Berekeningen
    import Routines
    Motievendirectory = Basisdirectory + motief +'/'
    Constantendirectory = Motievendirectory + 'Reistijdvervalscurve/'
    Gewichtendirectory = Motievendirectory + 'Gewichten/'
    print ('Laden constanten voor reistijdvervalscurve')
    Routines.laad_alle_constanten_reistijdvervalcurve ( Constantendirectory, motief)
    print ('Berekenen gewichten voor Fiets, EFiets, Auto en OV')
    Berekeningen.Berekenengewichten_en_wegschrijven(Motievendirectory, motief)
    print ('Berekenen gewichten over de vervoerswijzen heen')
    Berekeningen.berekenen_combigewichten(Gewichtendirectory)

def Stap3 (Basisdirectory, SEGSdirectory, motief ):
    import Berekeningen
    print ('Berekenen matrix voor bestemmingen voor ontplooiing.')
    Berekeningen.bereken_alle_bestemmings_of_herkomstmatrices(Basisdirectory, SEGSdirectory, motief)
    print ('Bereken de herkomsten (inwoners) voor potentie-berekening')
    Berekeningen.bereken_alle_bestemmings_of_herkomstmatrices ( Basisdirectory, SEGSdirectory, motief, functie = "herkomst" )

def Stap4 (Basisdirectory, motief ):
    import Berekeningen
    import Routines
    aantal_groepen = 20
    aantal_zones = 1425
    Motievendirectory = Basisdirectory + motief + '/'
    Totalendirectory = Motievendirectory + 'Totalenpergroep/'
    vervoercombis = ['Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV', 'Fiets_Auto_OV', 'Efiets_Auto_OV']
    Header = 'Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Fiets_Auto', 'Fiets_OV', 'EFiets_Auto', 'Efiets_OV', 'Auto_OV', 'Fiets_Auto_OV', 'Efiets_Auto_OV'
    Getallenlijst = Routines.getallenlijst_maken ( aantal_zones )
    Uitvoerdirectory = Motievendirectory + 'UitvoerExcels/'
    print ('Berekenen de totale ontplooiingsmogelijkheden qua bestemmingen voor alle groepen')
    if motief == 'werk':
        type_bestemming = "arbeidsplaatsen"
    else :
        type_bestemming = motief
    Berekeningen.berekenen_ontplooiingstotalen_per_groep(Motievendirectory, type_bestemming)

    for groep in range ( aantal_groepen + 1 ):
        Getallenmatrix_voor_Excel_uitvoer = Routines.matrixen_maken_voor_Excel_totalen ( Totalendirectory, groep )
        Uitvoerfile = Uitvoerdirectory + 'Totalen_voor_groep_' + str ( groep )
        Routines.csvwegschrijven(Getallenmatrix_voor_Excel_uitvoer, Uitvoerfile)
        Routines.xlswegschrijven_totalen ( Getallenmatrix_voor_Excel_uitvoer, Header, Getallenlijst, Uitvoerfile )

def Stap5(Basisdirectory, motief) :
    import Routines
    import Berekeningen
    import Invoer

    Bevolkingssamenstelling_directory = Basisdirectory + 'Bevolkingssamenstelling/'
    Buurtsamenstellings_excel = Bevolkingssamenstelling_directory + 'Samenstelling_buurten_en _invloedsgebieden_Breburg.xlsx'
    Alle_buurten_matrix = Routines.maak_totale_buurten_file(Buurtsamenstellings_excel)
    Totale_buurtenfile = Bevolkingssamenstelling_directory + 'Alle_buurten'
    Routines.csvwegschrijven ( Alle_buurten_matrix, Totale_buurtenfile )
    Correctielijst = Invoer.Haal_correctiefactoren_op()
    Berekeningen.maak_potentielijst (Basisdirectory, motief,Correctielijst)
    Routines.csvwegschrijven(Correctielijst, Basisdirectory + motief +'/correctielijst', soort = 'lijst')

def Stap6(Basisdirectory, motief):
    import Berekeningen
    Berekeningen.totalen_over_bevolking(Basisdirectory, motief)

def Stap7(Basisdirectory, motief):
    import Berekeningen
    Berekeningen.Concurrentie_positie_herk_of_bestemming(Basisdirectory, motief, "bestemmingen")

def Stap8(Basisdirectory, motief):
    import Berekeningen
    Berekeningen.Concurrentie_positie_herk_of_bestemming(Basisdirectory, motief, "herkomst")