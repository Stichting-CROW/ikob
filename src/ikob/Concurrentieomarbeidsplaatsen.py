import logging
import ikob.Routines as Routines
import numpy as np

logger = logging.getLogger(__name__)


def concurrentie_om_arbeidsplaatsen(config, datasource):
    project_config = config['project']
    skims_config = config['skims']
    verdeling_config = config['verdeling']
    dagsoort = skims_config['dagsoort']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config['motieven']
    percentageelektrisch = verdeling_config['Percelektrisch']
    logger.debug("percentageelektrisch: %s", percentageelektrisch)

    # Vaste intellingen
    Groepen = ['GratisAuto_laag', 'GratisAuto_GratisOV_laag', 'WelAuto_GratisOV_laag', 'WelAuto_vkAuto_laag',
               'WelAuto_vkNeutraal_laag', 'WelAuto_vkFiets_laag', 'WelAuto_vkOV_laag', 'GeenAuto_GratisOV_laag',
               'GeenAuto_vkNeutraal_laag', 'GeenAuto_vkFiets_laag', 'GeenAuto_vkOV_laag', 'GeenRijbewijs_GratisOV_laag',
               'GeenRijbewijs_vkNeutraal_laag', 'GeenRijbewijs_vkFiets_laag', 'GeenRijbewijs_vkOV_laag',
               'GratisAuto_middellaag', 'GratisAuto_GratisOV_middellaag', 'WelAuto_GratisOV_middellaag',
               'WelAuto_vkAuto_middellaag', 'WelAuto_vkNeutraal_middellaag', 'WelAuto_vkFiets_middellaag',
               'WelAuto_vkOV_middellaag', 'GeenAuto_GratisOV_middellaag', 'GeenAuto_vkNeutraal_middellaag',
               'GeenAuto_vkFiets_middellaag', 'GeenAuto_vkOV_middellaag', 'GeenRijbewijs_GratisOV_middellaag',
               'GeenRijbewijs_vkNeutraal_middellaag', 'GeenRijbewijs_vkFiets_middellaag', 'GeenRijbewijs_vkOV_middellaag',
               'GratisAuto_middelhoog', 'GratisAuto_GratisOV_middelhoog', 'WelAuto_GratisOV_middelhoog',
               'WelAuto_vkAuto_middelhoog', 'WelAuto_vkNeutraal_middelhoog', 'WelAuto_vkFiets_middelhoog',
               'WelAuto_vkOV_middelhoog', 'GeenAuto_GratisOV_middelhoog', 'GeenAuto_vkNeutraal_middelhoog',
               'GeenAuto_vkFiets_middelhoog', 'GeenAuto_vkOV_middelhoog', 'GeenRijbewijs_GratisOV_middelhoog',
               'GeenRijbewijs_vkNeutraal_middelhoog', 'GeenRijbewijs_vkFiets_middelhoog', 'GeenRijbewijs_vkOV_middelhoog',
               'GratisAuto_hoog', 'GratisAuto_GratisOV_hoog', 'WelAuto_GratisOV_hoog', 'WelAuto_vkAuto_hoog',
               'WelAuto_vkNeutraal_hoog', 'WelAuto_vkFiets_hoog', 'WelAuto_vkOV_hoog', 'GeenAuto_GratisOV_hoog',
               'GeenAuto_vkNeutraal_hoog', 'GeenAuto_vkFiets_hoog', 'GeenAuto_vkOV_hoog', 'GeenRijbewijs_GratisOV_hoog',
               'GeenRijbewijs_vkNeutraal_hoog', 'GeenRijbewijs_vkFiets_hoog', 'GeenRijbewijs_vkOV_hoog']

    modaliteiten = ['Fiets',  'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets',  'Auto_OV', 'Auto_OV_Fiets']
    inkgroepen = ['laag', 'middellaag', 'middelhoog', 'hoog']
    soortbrandstof = ['fossiel', 'elektrisch']
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    headstringExcel = ['Zone', 'Fiets', 'Auto', 'OV', 'Auto-Fiets' 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']

    if 'winkelnietdagelijksonderwijs' in motieven:
        Inwonersperklasse = datasource.read_segs("Leerlingen", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = datasource.read_segs("Leerlingenplaatsen", scenario=scenario, type_caster=float)
    else:
        Inwonersperklasse = datasource.read_segs("Beroepsbevolking_inkomensklasse", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = datasource.read_segs("Arbeidsplaatsen_inkomensklasse", scenario=scenario, type_caster=float)

    Inwonerstotalen = [sum(ipk) for ipk in Inwonersperklasse]

    Inkomensverdeling = np.zeros((len(Inwonersperklasse), len(Inwonersperklasse[0])))
    for i in range(len(Inwonersperklasse)):
        for j in range(len(Inwonersperklasse[0])):
            if Inwonerstotalen[i] > 0:
                Inkomensverdeling[i][j] = Inwonersperklasse[i][j]/Inwonerstotalen[i]

    for mot in motieven:
        if mot == 'werk':
            Doelgroep = 'Beroepsbevolking'
        elif mot == 'winkelnietdagelijksonderwijs':
            Doelgroep = 'Leerlingen'
        else:
            Doelgroep = 'Inwoners'

        Verdelingsmatrix = datasource.read_segs(f"Verdeling_over_groepen_{Doelgroep}", scenario=scenario, type_caster=float)
        logger.debug('Verdelingsmatrix 4 is %s', Verdelingsmatrix[4])

        for ds in dagsoort:
            for i_inkgr, inkgr in enumerate(inkgroepen):

                # Eerst de fiets
                logger.debug('We zijn het nu aan het uitrekenen voor de inkomensgroep %s', inkgr)
                for mod in modaliteiten:
                    concurrentie_totaal = Routines.lijstvolnullen(len(Arbeidsplaatsen))
                    for gr in Groepen:
                        arbeidsplaatsen_groep = Arbeidsplaatsen.T[i_inkgr]

                        logger.debug('Bezig met Groep %s', gr)
                        ink = Routines.inkomensgroepbepalen(gr)
                        if inkgr == ink or inkgr == 'alle':
                            vk = Routines.vindvoorkeur(gr, mod)
                            if mod == 'Fiets' or mod == 'EFiets':
                                vkfiets = 'Fiets' if vk == 'Fiets' else ''
                                Fietsmatrix = datasource.read_csv('Gewichten', f'{mod}_vk', ds, vk=vkfiets, regime=regime, mot=mot)
                                Bereik = datasource.read_csv('Herkomsten', "Totaal", ds, mot=mot, mod=mod, ink=inkgr)
                                concurrentie = Fietsmatrix @ (arbeidsplaatsen_groep / np.where(Bereik > 0, Bereik, 1.0))

                                for i in range(len(Fietsmatrix)):
                                    if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                        concurrentie_totaal[i] += concurrentie[i] * Verdelingsmatrix[i][Groepen.index(gr)] /\
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]

                            elif mod == 'Auto':
                                String = Routines.enkelegroep(mod, gr)
                                logger.debug("String = %s", String)
                                if 'WelAuto' in gr:
                                    for srtbr in soortbrandstof:
                                        Matrix = datasource.read_csv('Gewichten', f"{String}_vk", ds, vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                        Bereik = datasource.read_csv('Herkomsten', "Totaal", ds, mot=mot, mod=mod, ink=inkgr)
                                        concurrentie = Matrix @ (arbeidsplaatsen_groep / np.where(Bereik > 0, Bereik, 1.0))
                                        if srtbr == 'elektrisch':
                                            K = percentageelektrisch.get(inkgr) / 100
                                            logger.debug('aandeel elektrisch is %s', K)
                                            concurrentie_elektrisch = [x * K for x in concurrentie]
                                        else:
                                            L = 1 - percentageelektrisch.get(inkgr) / 100
                                            logger.debug('aandeel fossiel is %s', L)
                                            concurrentie_fossiel = [x * L for x in concurrentie]
                                    for i in range(len(Matrix)):
                                        concurrentie[i] = concurrentie_elektrisch[i] + concurrentie_fossiel[i]
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                            concurrentie_totaal[i] += concurrentie[i] * Verdelingsmatrix[i][Groepen.index(gr)] /\
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                else:
                                    Matrix = datasource.read_csv('Gewichten', f"{String}_vk", ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                    Bereik = datasource.read_csv('Herkomsten', "Totaal", ds, mot=mot, mod=mod, ink=inkgr)
                                    concurrentie = Matrix @ (arbeidsplaatsen_groep / np.where(Bereik > 0, Bereik, 1.0))
                                    for i in range(len(Matrix)):
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                            concurrentie_totaal[i] += concurrentie[i] * Verdelingsmatrix[i][Groepen.index(gr)] /\
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]
                            elif mod == 'OV':
                                String = Routines.enkelegroep(mod, gr)
                                Matrix = datasource.read_csv('Gewichten', f"{String}_vk", ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                Bereik = datasource.read_csv('Herkomsten', "Totaal", ds, mot=mot, mod=mod, ink=inkgr)
                                concurrentie = Matrix @ (arbeidsplaatsen_groep / np.where(Bereik > 0, Bereik, 1.0))
                                for i in range(len(Matrix)):
                                    if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                        concurrentie_totaal[i] += concurrentie[i] * Verdelingsmatrix[i][Groepen.index(gr)] / \
                                                      Inkomensverdeling[i][inkgroepen.index(inkgr)]

                            else:
                                String = Routines.combigroep(mod, gr)
                                logger.debug('de gr is %s', gr)
                                logger.debug('de string is %s', String)
                                if String[0] == 'A':
                                    for srtbr in soortbrandstof:
                                        Matrix = datasource.read_csv('Gewichten', f'{String}_vk', ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                        Bereik = datasource.read_csv('Herkomsten', "Totaal", ds, mot=mot, mod=mod, ink=inkgr)
                                        concurrentie = Matrix @ (arbeidsplaatsen_groep / np.where(Bereik > 0, Bereik, 1.0))
                                        if srtbr == 'elektrisch':
                                            K = percentageelektrisch.get(inkgr)/100
                                            concurrentie_elektrisch = [x * K for x in concurrentie]
                                        else:
                                            K = 1 - percentageelektrisch.get(inkgr)/100
                                            concurrentie_fossiel = [x * K for x in concurrentie]
                                    for i in range (len(Matrix)):
                                        concurrentie[i] = concurrentie_elektrisch[i] + concurrentie_fossiel[i]
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                            concurrentie_totaal[i] += concurrentie[i] * Verdelingsmatrix[i][Groepen.index(gr)] /\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]
                                else:
                                    Matrix = datasource.read_csv('Gewichten', f'{String}_vk', ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot)
                                    Bereik = datasource.read_csv('Herkomsten', "Totaal", ds, mot=mot, mod=mod, ink=inkgr)
                                    concurrentie = Matrix @ (arbeidsplaatsen_groep / np.where(Bereik > 0, Bereik, 1.0))
                                    for i in range(len(Matrix)):
                                        if Inkomensverdeling[i][inkgroepen.index(inkgr)] > 0:
                                            concurrentie_totaal[i] += concurrentie[i] * Verdelingsmatrix[i][Groepen.index(gr)] /\
                                                          Inkomensverdeling[i][inkgroepen.index(inkgr)]

                    datasource.write_csv(concurrentie_totaal, 'Concurrentie', 'Totaal', ds, subtopic="arbeidsplaatsen", mot=mot, mod=mod, ink=inkgr)
                # En tot slot alles bij elkaar harken:
                Generaaltotaal_potenties = []
                for mod in modaliteiten:
                    Totaalrij = datasource.read_csv('Concurrentie', "Totaal", ds, subtopic="arbeidsplaatsen", mot=mot, mod=mod, ink=inkgr)
                    Generaaltotaal_potenties.append(Totaalrij)
                    Generaaltotaaltrans = Routines.transponeren(Generaaltotaal_potenties)
                    # TODO: This loops over mod, but does _not_ use mod as filename modifiers?
                    datasource.write_csv(Generaaltotaaltrans, 'Concurrentie', 'Ontpl_conc', ds, subtopic="arbeidsplaatsen", mot=mot, ink=inkgr, header=headstring)
                    datasource.write_xlsx(Generaaltotaaltrans, 'Concurrentie', 'Ontpl_conc', ds, subtopic="arbeidsplaatsen", mot=mot, ink=inkgr, header=headstringExcel)

            header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
            for mod in modaliteiten:
                Generaalmatrixproduct = []
                Generaalmatrix = []
                for inkgr in inkgroepen:
                    Totaalrij = datasource.read_csv("Concurrentie", "Totaal", ds, subtopic="arbeidsplaatsen", mot=mot, mod=mod, ink=inkgr)
                    Generaalmatrix.append(Totaalrij)
                    Generaaltotaaltrans = Routines.transponeren(Generaalmatrix)
                for i in range(len(Inwonersperklasse)):
                    Generaalmatrixproduct.append([])
                    for j in range(len(Inwonersperklasse[0])):
                        if Inwonersperklasse[i][j] > 0:
                            Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                        else:
                            Generaalmatrixproduct[i].append(0)

                datasource.write_xlsx(Generaaltotaaltrans, 'Concurrentie', 'Ontpl_conc', ds, subtopic="arbeidsplaatsen", mot=mot, mod=mod, header=header)
                datasource.write_xlsx(Generaalmatrixproduct, 'Concurrentie', 'Ontpl_concproduct', ds, subtopic="arbeidsplaatsen", mot=mot, mod=mod, header=header)
