import logging
import Routines
import Berekeningen

logger = logging.getLogger(__name__)


def concurrentie_om_inwoners(config, datasource):
    project_config = config['project']
    skims_config = config['skims']
    verdeling_config = config ['verdeling']
    dagsoort = skims_config['dagsoort']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config ['motieven']
    autobezitgroepen = project_config ['welke_groepen']
    percentageelektrisch = verdeling_config ['Percelektrisch']
    logger.debug("percentageelektrisch: %s", percentageelektrisch)

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
    inkgroepen = ['laag', 'middellaag', 'middelhoog', 'hoog']
    soortbrandstof = ['fossiel','elektrisch']
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']
    headstringExcel=['Zone', 'Fiets', 'Auto', 'OV', 'Auto-Fiets' 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']

    if 'winkelnietdagelijksonderwijs' in motieven:
        Inwonersperklasse = datasource.segs_lezen("Leerlingen", scenario=scenario, cijfer_type='float')
        Arbeidsplaatsen = datasource.segs_lezen("Leerlingenplaatsen", scenario=scenario, cijfer_type='float')
    else:
        Inwonersperklasse = datasource.segs_lezen("Beroepsbevolking_inkomensklasse", scenario=scenario, cijfer_type='float')
        Arbeidsplaatsen = datasource.segs_lezen("Arbeidsplaatsen_inkomensklasse", scenario=scenario, cijfer_type='float')

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


    for abg in autobezitgroepen:
        for mot in motieven:
            if mot == 'werk':
                Doelgroep = 'Beroepsbevolking'
            elif mot == 'winkelnietdagelijksonderwijs':
                Doelgroep = 'Leerlingen'
            else:
                Doelgroep = 'Inwoners'
            Verdelingsmatrix = datasource.segs_lezen(f"Verdeling_over_groepen_{Doelgroep}", scenario=scenario, cijfer_type='float')
            logger.debug('Verdelingsmatrix 4 is %s', Verdelingsmatrix[4])

            for ds in dagsoort:
                for inkgr in inkgroepen:
                    # Eerst de fiets
                    logger.debug('We zijn het nu aan het uitrekenen voor de inkomensgroep %s', inkgr)
                    for mod in modaliteiten:
                        Bijhoudlijst = Routines.lijstvolnullen(len(Arbeidsplaatsen))
                        for gr in Groepen:
                            logger.debug('Bezig met Groep %s', gr)
                            ink = Routines.inkomensgroepbepalen ( gr )
                            if inkgr == ink or inkgr == 'alle':
                                vk = Routines.vindvoorkeur ( gr, mod )
                                if mod == 'Fiets' or mod == 'EFiets':
                                    if vk == 'Fiets':
                                        vkklad = 'Fiets'
                                    else:
                                        vkklad = ''

                                    Fietsmatrix = datasource.gewichten_lezen(f'{mod}_vk', ds, vkklad, regime=regime, mot=mot)
                                    Bereik = datasource.bestemmingen_totalen_lezen("Totaal", ds, mod=mod, ink=inkgr, mot=mot, abg=abg)
                                    Dezegroeplijst = Berekeningen.bereken_concurrentie ( Fietsmatrix, Inwonersperklasse, Bereik, inkgr, inkgroepen)

                                    for i in range ( 0, len ( Fietsmatrix ) ):
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                            Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                            Bijhoudlijst[i] +=  Bijhoudklad

                                elif mod == 'Auto' :
                                    String = Routines.enkelegroep ( mod, gr )
                                    logger.debug("String = %s", String)
                                    if 'WelAuto' in gr:
                                        for srtbr in soortbrandstof:
                                            Matrix = datasource.gewichten_lezen(f'{String}_vk', ds, vk, ink, regime=regime, mot=mot, srtbr=srtbr)
                                            Bereik = datasource.bestemmingen_totalen_lezen("Totaal", ds, mod=mod, ink=inkgr, mot=mot, abg=abg)
                                            Dezegroeplijst1 = Berekeningen.bereken_concurrentie ( Matrix, Inwonersperklasse, Bereik, inkgr, inkgroepen)
                                            if srtbr == 'elektrisch':
                                                K = percentageelektrisch.get(inkgr) / 100
                                                logger.debug('aandeel elektrisch is %s', K)
                                                DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                            else:
                                                L = 1 - percentageelektrisch.get(inkgr) / 100
                                                logger.debug('aandeel fossiel is %s', L)
                                                DezegroeplijstF = [x * L for x in Dezegroeplijst1]
                                        for i in range(len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                            if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                                Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                                Bijhoudlijst[i] += Bijhoudklad
                                    else:
                                        Matrix = datasource.gewichten_lezen(f'{String}_vk', ds, vk, ink, regime=regime, mot=mot)
                                        Bereik = datasource.bestemmingen_totalen_lezen("Totaal", ds, mod=mod, ink=inkgr, mot=mot, abg=abg)
                                        Dezegroeplijst = Berekeningen.bereken_concurrentie(Matrix, Inwonersperklasse, Bereik, inkgr, inkgroepen)
                                        for i in range(len(Matrix)):
                                            if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                                Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                                Bijhoudlijst[i] += Bijhoudklad
                                elif mod == 'OV':
                                    String = Routines.enkelegroep(mod, gr)
                                    Matrix = datasource.gewichten_lezen(f'{String}_vk', ds, vk, ink, regime=regime, mot=mot)
                                    Bereik = datasource.bestemmingen_totalen_lezen("Totaal", ds, mod=mod, ink=inkgr, mot=mot, abg=abg)
                                    Dezegroeplijst = Berekeningen.bereken_concurrentie(Matrix, Inwonersperklasse, Bereik, inkgr, inkgroepen)
                                    for i in range(len(Matrix)):
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                            Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)] / \
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                            Bijhoudlijst[i] += Bijhoudklad
        
                                else:
                                    String = Routines.combigroep(mod, gr)
                                    logger.debug('de gr is %s', gr)
                                    logger.debug('de string is %s', String)
                                    if String[0] == 'A':
                                        for srtbr in soortbrandstof:
                                            Matrix = datasource.combinatie_gewichten_lezen(f'{String}_vk', ds, vk, ink, regime=regime, mot=mot, srtbr=srtbr)
                                            Bereik = datasource.bestemmingen_totalen_lezen("Totaal", ds, mod=mod, ink=inkgr, mot=mot, abg=abg)
                                            Dezegroeplijst1 = Berekeningen.bereken_concurrentie ( Matrix, Inwonersperklasse, Bereik, inkgr, inkgroepen)
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
                                        Matrix = datasource.combinatie_gewichten_lezen(f'{String}_vk', ds, vk, ink, regime=regime, mot=mot)
                                        Bereik = datasource.bestemmingen_totalen_lezen("Totaal", ds, mod=mod, ink=inkgr, mot=mot, abg=abg)
                                        Dezegroeplijst = Berekeningen.bereken_concurrentie(Matrix, Inwonersperklasse, Bereik, inkgr, inkgroepen)
                                        for i in range (len(Matrix)):
                                            if Inkomensverdeling[i][inkgroepen.index(inkgr)]>0:
                                                Bijhoudklad = Dezegroeplijst[i] * Verdelingsmatrix[i][Groepen.index(gr)]/\
                                                              Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                                Bijhoudlijst[i] += Bijhoudklad

                        datasource.concurrentie_totalen_schrijven(Bijhoudlijst, 'Totaal', ds, "inwoners", ink=inkgr, mod=mod)

                    # En tot slot alles bij elkaar harken:
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten:
                        Totaalrij = datasource.concurrentie_totalen_lezen("Totaal", ds, "inwoners", mod=mod, ink=inkgr)
                        Generaaltotaal_potenties.append ( Totaalrij )
                        Generaaltotaaltrans = Routines.transponeren ( Generaaltotaal_potenties )
                        datasource.concurrentie_totalen_schrijven(Generaaltotaaltrans, 'Ontpl_conc', ds, "inwoners", ink=inkgr, write_header=True, header=headstring)
                        datasource.concurrentie_totalen_schrijven(Generaaltotaaltrans, 'Ontpl_conc', ds, "inwoners", ink=inkgr, xlsx_format=True, write_header=True, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag','middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        Totaalrij = datasource.concurrentie_totalen_lezen("Totaal", ds, "inwoners", mod=mod, ink=inkgr)
                        Generaalmatrix.append(Totaalrij)
                        Generaaltotaaltrans = Routines.transponeren(Generaalmatrix)
                    for i in range (len(Inwonersperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range (len(Inwonersperklasse[0])):
                            if Inwonersperklasse[i][j]>0:
                                Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    datasource.concurrentie_totalen_schrijven(Generaaltotaaltrans, 'Ontpl_conc', ds, "inwoners", mod=mod, xlsx_format=True, write_header=True, header=header)
                    datasource.concurrentie_totalen_schrijven(Generaalmatrixproduct, 'Ontpl_concproduct', ds, "inwoners", mod=mod, xlsx_format=True, write_header=True, header=header)
