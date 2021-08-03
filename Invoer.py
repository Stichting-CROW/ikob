def haal_motief_op():
    from tkinter import Label,Checkbutton,Button,Tk,W, IntVar, mainloop
    master = Tk()

    def var_states():
       print('werk: %d,\nwinkeldagelijks: %d,\nwinkelnietdagelijks: %d, \nonderwijs: %d ,\nzorg: %d, \noverig: %d'
             % (var_werk.get(), var_winkeldagelijks.get(), var_winkelnietdagelijks.get(), var_onderwijs.get(),
                var_zorg.get(), var_overig.get()))

    Label(master, text="Welke vervoersmotief ga je bezig? (slechts 1 keuze mogelijk:").grid(row=0, sticky=W)
    var_werk = IntVar()
    Checkbutton(master, text="werk", variable=var_werk).grid(row=1, sticky=W)
    var_winkeldagelijks = IntVar()
    Checkbutton(master, text="winkeldagelijks", variable=var_winkeldagelijks).grid(row=2, sticky=W)
    var_winkelnietdagelijks = IntVar()
    Checkbutton(master, text="winkelnietdagelijks", variable=var_winkelnietdagelijks).grid(row=3, sticky=W)
    var_onderwijs = IntVar()
    Checkbutton(master, text="onderwijs", variable=var_onderwijs).grid(row=4, sticky=W)
    var_zorg = IntVar()
    Checkbutton(master, text="zorg", variable=var_zorg).grid(row=5, sticky=W)
    var_overig = IntVar()
    Checkbutton(master, text="overig", variable=var_overig).grid(row=6, sticky=W)

    #    Button(master, text='Bevestig', command=pak_waarden).grid(row=8, sticky=W, pady=4)
    Button(master, text='Laat keuze zien', command=var_states).grid(row=7, sticky=W, pady=4)
    Button(master, text='Ga verder', command=master.destroy).grid(row=9, sticky=W, pady=4)
    mainloop()

    if var_werk.get() == 1:
        gekozen_motief = 'werk'
    elif var_winkeldagelijks.get() == 1:
        gekozen_motief = 'winkeldagelijks'
    elif var_winkelnietdagelijks.get() == 1:
        gekozen_motief = 'winkelnietdagelijks'
    elif var_onderwijs.get ( ) == 1:
        gekozen_motief = 'onderwijs'
    elif var_zorg.get() == 1:
        gekozen_motief = 'zorg'
    elif var_overig.get() == 1:
        gekozen_motief = 'inwoners'
    else:
        gekozen_motief = 'geen'

    print (gekozen_motief)
    return (gekozen_motief)

def haal_bestemming_op():
    from tkinter import Label,Checkbutton,Button,Tk,W, IntVar, mainloop
    master = Tk()


    def var_states():
       print('arbeidsplaatsen: %d,\ninwoners: %d,\nwinkeldagelijks: %d,\nwinkelnietdagelijks: %d, \nonderwijs: %d ,'
             '\nzorg: %d'
             % (var_arbeidsplaatsen.get(), var_inwoners.get(), var_winkeldagelijks.get(), var_winkelnietdagelijks.get(), var_onderwijs.get(),
                var_zorg.get()))

    Label(master, text="Welke bestemming gaat het om (slechts 1 keuze mogelijk:").grid(row=0, sticky=W)
    var_arbeidsplaatsen = IntVar()
    Checkbutton(master, text="arbeidsplaatsen", variable=var_arbeidsplaatsen).grid(row=1, sticky=W)
    var_inwoners = IntVar()
    Checkbutton ( master, text="inwoners", variable=var_inwoners ).grid ( row=2, sticky=W )
    var_winkeldagelijks = IntVar ( )
    Checkbutton(master, text="dagelijksinwoners", variable=var_winkeldagelijks).grid(row=3, sticky=W)
    var_winkelnietdagelijks = IntVar()
    Checkbutton(master, text="winkelnietdagelijks", variable=var_winkelnietdagelijks).grid(row=4, sticky=W)
    var_onderwijs = IntVar()
    Checkbutton(master, text="onderwijs", variable=var_onderwijs).grid(row=5, sticky=W)
    var_zorg = IntVar()
    Checkbutton(master, text="zorg", variable=var_zorg).grid(row=6, sticky=W)
    #    Button(master, text='Bevestig', command=pak_waarden).grid(row=8, sticky=W, pady=4)
    # Button(master, text='Laat keuze zien', command=var_states).grid(row=7, sticky=W, pady=4)
    Button(master, text='Ga verder', command=master.destroy).grid(row=9, sticky=W, pady=4)
    mainloop()

    if var_arbeidsplaatsen.get() == 1:
        gekozen_motief = 'arbeidsplaatsen'
    elif var_inwoners.get() == 1:
        gekozen_motief = 'inwoners'
    elif var_winkelnietdagelijks.get() == 1:
        gekozen_motief = 'winkelnietdagelijks'
    elif var_onderwijs.get ( ) == 1:
        gekozen_motief = 'onderwijs'
    elif var_zorg.get() == 1:
        gekozen_motief = 'zorg'
    elif var_inwoners.get() == 1:
        gekozen_motief = 'inwoners'
    else:
        gekozen_motief = 'geen'

    print (gekozen_motief)
    return (gekozen_motief)


def Ja_Nee(tekst):
    from tkinter import Label, Checkbutton, Button, Tk, W, IntVar, mainloop
    master = Tk ( )

    Label ( master, text=tekst ).grid ( row=0, sticky=W )
    var_ja = IntVar ( )
    Checkbutton ( master, text="Ja", variable=var_ja ).grid ( row=1, sticky=W )
    var_nee = IntVar ( )
    Checkbutton ( master, text="Nee", variable=var_nee ).grid ( row=2, sticky=W )
    Button ( master, text='Ga verder', command=master.destroy).grid ( row=9, sticky=W, pady=4 )
    mainloop ( )
    if var_ja.get ( ) == 1:
        keuze = 1
    else:
        keuze = 0
    print ( keuze )
    return keuze
#    return

def haal_keuze_op():
    from tkinter import Label,Checkbutton,Button,Tk,W, IntVar, mainloop
    master = Tk()

    Label(master, text="Welke Stap zijn we aan toe?").grid(row=0, sticky=W)
    var_Stap1 = IntVar()
    Checkbutton(master, text="Stap1: De eerste skims corrigeren voor parkeerzoektijd e.d.", 
                variable=var_Stap1).grid(row=1, sticky=W)
    var_Stap2 = IntVar()
    Checkbutton(master, text="Stap2: Van de deur-tot-deur-skims naar de Reistijdvervalgewichten",
                variable=var_Stap2).grid(row=2, sticky=W)
    var_Stap3 = IntVar()
    Checkbutton(master, text="Stap3: Van de Reistijdvervalswaarden naar het aantal bestemmingen per HB-combi", 
                variable=var_Stap3).grid(row=3, sticky=W)
    var_Stap4 = IntVar()
    Checkbutton(master, text="Stap4: De HB-bestemmingswaarde combineren tot sommen over alle zones" , 
                variable=var_Stap4).grid(row=4, sticky=W)
    var_Stap5 = IntVar()
    Checkbutton(master, text="Stap5: Voor de potentie van bedrijven, winkels etc. de HB-bestemmingswaarden combineren met de bevolkingssamenstelling ",
                variable=var_Stap5).grid(row=5, sticky=W)
    var_Stap6 = IntVar()
    Checkbutton(master, text="Stap6: Vanuit de resultaten van Stap 4 berekenen we het aantal bereikbare arbeidsplaatsen, winkels etc rekening houdend met de bevolkingssamenstelling",
                variable=var_Stap6).grid(row=6, sticky=W)
    var_Stap7 = IntVar()
    Checkbutton(master, text="Stap7: Bereken de concurrentie voor het bereiken van de bestemmngen",
                variable=var_Stap7).grid(row=7, sticky=W)
    var_Stap8 = IntVar()
    Checkbutton(master, text="Stap8: Bereken de concurrentiekracht van bedrijven, winkels in bereikbaarheid",
                 variable=var_Stap8).grid(row=8, sticky=W)
    var_Stoppen = IntVar()
    Checkbutton(master, text="Stoppen",
                variable=var_Stoppen).grid(row=9, sticky=W)
    #    Button(master, text='Bevestig', command=pak_waarden).grid(row=8, sticky=W, pady=4)
    Button(master, text='Keuze gemaakt', command=master.destroy).grid(row=10, sticky=W, pady=4)
    mainloop()

    if var_Stap1.get() == 1:
        keuze = 'Stap1'
    elif var_Stap2.get() == 1:
        keuze = 'Stap2'
    elif var_Stap3.get() == 1:
        keuze = 'Stap3'
    elif var_Stap4.get ( ) == 1:
        keuze = 'Stap4'
    elif var_Stap5.get() == 1:
        keuze = 'Stap5'
    elif var_Stap6.get() == 1:
        keuze = 'Stap6'
    elif var_Stap7.get() == 1:
        keuze = 'Stap7'
    elif var_Stap8.get() == 1:
        keuze = 'Stap8'
    elif var_Stoppen.get ( ) == 1:
        keuze = 'Stoppen'
    else:
        keuze = 'geen'
    return keuze

def welke_hebben_geen_auto():
    from tkinter import Label,Checkbutton,Button,Tk,W, IntVar, mainloop
    master = Tk()

    Label(master, text="Geef op welke groepen geen auto hebben").grid(row=0, sticky=W)
    var_Groep1 = IntVar()
    Checkbutton(master, text="Groep1: Auto vd zaak, geen OV vd zaak",
                variable=var_Groep1).grid(row=1, sticky=W)
    var_Groep2 = IntVar()
    Checkbutton(master, text="Groep2: Auto en OV vd zaak",
                variable=var_Groep2).grid(row=2, sticky=W)
    var_Groep3 = IntVar()
    Checkbutton(master, text="Groep3: OV vd zaak, geen auto vd zaak, bezit auto",
                variable=var_Groep3).grid(row=3, sticky=W)
    var_Groep4 = IntVar()
    Checkbutton(master, text="Groep4: Voorkeur auto, hoog inkomen" ,
                variable=var_Groep4).grid(row=4, sticky=W)
    var_Groep5 = IntVar()
    Checkbutton(master, text="Groep5: Voorkeur auto, middel inkomen ",
                variable=var_Groep5).grid(row=5, sticky=W)
    var_Groep6 = IntVar()
    Checkbutton(master, text="Groep6: Voorkeur auto, laag inkomen",
                variable=var_Groep6).grid(row=6, sticky=W)
    var_Groep7 = IntVar()
    Checkbutton(master, text="Groep7: Neutraal qua voorkeur, hoog inkomen, <=2 personen per huizhouden",
                variable=var_Groep7).grid(row=7, sticky=W)
    var_Groep8 = IntVar()
    Checkbutton(master, text="Groep8: Neutraal qua voorkeur, hoog inkomen, >2 personen per huizhouden",
                 variable=var_Groep8).grid(row=8, sticky=W)
    var_Groep9 = IntVar ( )
    Checkbutton ( master, text="Groep9: Neutraal qua voorkeur, laag inkomen, <=2 personen per huizhouden",
                  variable=var_Groep9 ).grid ( row=9, sticky=W )
    var_Groep10 = IntVar ( )
    Checkbutton ( master, text="Groep10: Neutraal qua voorkeur, laag inkomen, >2 personen per huizhouden",
                  variable=var_Groep10 ).grid ( row=10, sticky=W )
    var_Groep11 = IntVar()
    Checkbutton(master, text="Groep11: Voorkeur OV, hoog inkomen",
                variable=var_Groep11).grid(row=11, sticky=W)
    var_Groep12 = IntVar()
    Checkbutton(master, text="Groep12: Voorkeur OV, laag inkomen",
                variable=var_Groep12).grid(row=12, sticky=W)
    var_Groep13 = IntVar()
    Checkbutton(master, text="Groep13: Voorkeur fiets, hoog inkomen",
                variable=var_Groep13).grid(row=13, sticky=W)
    var_Groep14 = IntVar()
    Checkbutton(master, text="Groep14: Voorkeur fiets, laag inkomen",
                variable=var_Groep14).grid(row=14, sticky=W)
    var_Groep15 = IntVar()
    Checkbutton(master, text="Groep15: Bezit geen auto, wel OV vd zaak",
                variable=var_Groep15).grid(row=15, sticky=W)
    var_Groep16 = IntVar()
    Checkbutton(master, text="Groep16: Bezit geen auto, OV voorkeur",
                variable=var_Groep16).grid(row=16, sticky=W)
    var_Groep17 = IntVar()
    Checkbutton(master, text="Groep17: Bezit geen auto, fiets voorkeur",
                variable=var_Groep17).grid(row=17, sticky=W)
    var_Groep18 = IntVar()
    Checkbutton(master, text="Groep18: Bezit geen auto, voorkeur neutraal",
                variable=var_Groep18).grid(row=18, sticky=W)
    var_Groep19 = IntVar()
    Checkbutton(master, text="Groep19: Bezit geen rijbewijs",
                variable=var_Groep19).grid(row=19, sticky=W)
    var_Groep20 = IntVar()
    Checkbutton(master, text="Groep20: OV studentenkaart",
                variable=var_Groep20).grid(row=20, sticky=W)

    #    Button(master, text='Bevestig', command=pak_waarden).grid(row=8, sticky=W, pady=4)
    Button(master, text='Keuze gemaakt', command=master.destroy).grid(row=21, sticky=W, pady=4)
    mainloop()

    groepen_zonder_auto=[]
    for groep in range (1,21):
        varnaam = 'var_Groep' + str(groep)
        globals () [varnaam] = []
        if eval(varnaam).get() == 1:
            groepen_zonder_auto.append(groep)
    return groepen_zonder_auto


def Welkomstscherm():
    from tkinter import Label, Checkbutton, Button, Tk, W, IntVar, mainloop
    master = Tk ( )

    Label ( master, text="Welkom bij de berekeningen van Een Nieuwe Kijk Op Bereikbaarheid" ).grid ( row=0, sticky=W )
    Label ( master, text="Stap voor stap zullen we de berekeningen doen" ).grid ( row=1, sticky=W )
    Label ( master, text="Alle tussenresultaten blijven steeds beschikbaar" ).grid ( row=2, sticky=W )
    Label ( master, text="Zorg je er wel voor dat de directory-structuur goed is?" ).grid ( row=3, sticky=W )
    Button ( master, text='Ga verder', command=master.destroy ).grid ( row=9, sticky=W, pady=4 )
    mainloop ( )

def Weergave_groepen():
    from tkinter import Label, Checkbutton, Button, Tk, W, IntVar, mainloop
    master = Tk ( )
    Label ( master, text="Hieronder vind je een beschrijving van alle groepen" ).grid ( row=0, sticky=W )
    Label ( master, text="Groep 1:auto van de zaak, geen OV-forfait" ).grid ( row=1, sticky=W )
    Label ( master, text="Groep 2:auto van de zaak + OV-forfait	" ).grid ( row=2, sticky=W )
    Label ( master, text="Groep 3:OV-forfait, geen auto vd zaak" ).grid ( row=3, sticky=W )
    Label ( master, text="Groep 4:voorkeur auto hoog inkomen" ).grid ( row=4, sticky=W )
    Label ( master, text="Groep 5:voorkeur auto middel inkomen" ).grid ( row=5, sticky=W )
    Label ( master, text="Groep 6:voorkeur auto laag inkomen" ).grid ( row=6, sticky=W )
    Label ( master, text="Groep 7:Neutraal qua voorkeur, hoog inkomen, gezin<=2" ).grid ( row=7, sticky=W )
    Label ( master, text="Groep 8:Neutraal qua voorkeur, hoog inkomen, gezin>2" ).grid ( row=8, sticky=W )
    Label ( master, text="Groep 9:Neutraal qua voorkeur, laag inkomen, gezin<=2" ).grid ( row=9, sticky=W )
    Label ( master, text="Groep 10:Neutraal qua voorkeur, laag inkomen, gezin>2" ).grid ( row=10, sticky=W )
    Label ( master, text="Groep 11:Voorkeur OV, hoog inkomen" ).grid ( row=11, sticky=W )
    Label ( master, text="Groep 12:Voorkeur OV, laag inkomen" ).grid ( row=12, sticky=W )
    Label ( master, text="Groep 13:Voorkeur fiets, hoog inkomen" ).grid ( row=13, sticky=W )
    Label ( master, text="Groep 14:Voorkeur fiets, laag inkomen" ).grid ( row=14, sticky=W )
    Label ( master, text="Groep 15:OV-forfait bezit geen auto" ).grid ( row=15, sticky=W )
    Label ( master, text="Groep 16:Bezit geen auto, OV-voorkeur" ).grid ( row=16, sticky=W )
    Label ( master, text="Groep 17:Bezit geen auto, fietsvoorkeur" ).grid ( row=17, sticky=W )
    Label ( master, text="Groep 18:Bezit geen auto, voorkeur neutraal" ).grid ( row=18, sticky=W )
    Label ( master, text="Groep 19:Bezit geen rijbewijs" ).grid ( row=19, sticky=W )
    Label ( master, text="Groep 20:OV-studentenkaart" ).grid ( row=20, sticky=W )
    Label ( master, text="Groep 0:Gemiddelde bevolkingssamenstelling" ).grid ( row=21, sticky=W )
    Button ( master, text='Ga verder', command=master.destroy ).grid ( row=22, sticky=W, pady=4 )
    mainloop ( )

def Haal_correctiefactoren_op():
    import Invoer
    aantal_groepen=20
    correctielijst=[]
    lengte = 0
    while lengte ==0:
        JN = input (
                    "WIlt u de  mate waarin sommige groepen meewegen corrigeren? (met name kan Auto van de zaak overheersend zijn? " )
        lengte = len(JN)
    if JN[0] == "J":
        te_corrigeren_groepen = []
        correctiefactoren = []
        print ( "Nu komen alle groepsomschrijvingen in beeld" )
        Invoer.Weergave_groepen ( )
        nummer = 0
        while int ( nummer ) > -1:
            nummer = input ( "Geef het groepsnummer weer, als er niet meer groepen zijn voor dan -1 in: " )
            if int ( nummer ) < 0:
                break
            else:
                te_corrigeren_groepen.append ( int ( nummer ) )
                correctiefactor = input ( "Geef de correctiefactor voor deze groep:: " )
                correctiefactoren.append ( float ( correctiefactor ) )
        for i in range ( 0, aantal_groepen + 1 ):
            if i in te_corrigeren_groepen:
                indexwaarde = te_corrigeren_groepen.index ( i )
                correctielijst.append ( correctiefactoren[indexwaarde] )
            else:
                correctielijst.append ( 1 )
        correctielijst.pop(0)
    return correctielijst

def Klaar():
    from tkinter import Label, Checkbutton, Button, Tk, W, IntVar, mainloop
    master = Tk ( )

    Label ( master, text="Deze stap is klaar" ).grid ( row=0, sticky=W )
    Button ( master, text='Ga verder', command=master.destroy ).grid ( row=9, sticky=W, pady=4 )
    mainloop ( )

def Nogniet():
    from tkinter import Label, Checkbutton, Button, Tk, W, IntVar, mainloop
    master = Tk ( )

    Label ( master, text="Zover zijn we nog niet" ).grid ( row=0, sticky=W )
    Button ( master, text='Ga verder', command=master.destroy ).grid ( row=9, sticky=W, pady=4 )
    mainloop ( )

def HelemaalKlaar():
    from tkinter import Label, Checkbutton, Button, Tk, W, IntVar, mainloop
    master = Tk ( )

    Label ( master, text="We zijn nu helemaal klaar" ).grid ( row=0, sticky=W )
    Button ( master, text='OK', command=master.destroy ).grid ( row=9, sticky=W, pady=4 )
    mainloop ( )