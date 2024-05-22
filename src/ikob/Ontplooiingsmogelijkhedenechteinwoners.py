import logging
import ikob.Routines as Routines
import numpy as np

logger = logging.getLogger(__name__)


def potenties(Matrix, Arbeidsplaatsen, Beroepsbevolkingsverdeling, Beroepsbevolkingaandeel, inkgr, gr, inkgroepen, Groepen):
    Dezegroeplijst = np.zeros(len(Matrix))

    for i, row in enumerate(Matrix):
        Gewogenmatrix = np.zeros(len(row))

        for j, (r, abp) in enumerate(zip(row, Arbeidsplaatsen[inkgroepen.index(inkgr)])):
            Gewogenmatrix[j] = r * abp * Beroepsbevolkingsverdeling[Groepen.index(gr)][i]

        if Beroepsbevolkingaandeel[i] > 0:
            Dezegroeplijst[i] = sum(Gewogenmatrix)/Beroepsbevolkingaandeel[i]

    return Dezegroeplijst.tolist()


def bereken_potenties_nietwerk(Matrix, Bestemmingen, Inwonersverdeling, Inwonersaandeel, gr, Groepen):
    Dezegroeplijst = np.zeros(len(Matrix))

    for i, row in enumerate(Matrix):
        Gewogenmatrix = np.zeros(len(row))

        for j, (r, b) in enumerate(zip(row, Bestemmingen)):
            Gewogenmatrix[j] = r * b * Inwonersverdeling[Groepen.index(gr)][i]

        if Inwonersaandeel[i] > 0:
            Dezegroeplijst[i] = sum(Gewogenmatrix)/(Inwonersaandeel[i])

    return Dezegroeplijst.tolist()


def ontplooingsmogelijkheden_echte_inwoners(config, datasource):
    project_config = config['project']
    skims_config = config['skims']
    verdeling_config = config['verdeling']
    dagsoort = skims_config['dagsoort']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config['motieven']
    autobezitgroepen = project_config['welke_groepen']
    inkgroepen = project_config['welke_inkomensgroepen']
    percentageelektrisch = verdeling_config['Percelektrisch']
    logger.debug("percentageelektrisch: %s", percentageelektrisch)

    if 'alle groepen' in autobezitgroepen:
        Basisgroepen = ['GratisAuto', 'GratisAuto_GratisOV', 'WelAuto_GratisOV', 'WelAuto_vkAuto',
                        'WelAuto_vkNeutraal', 'WelAuto_vkFiets', 'WelAuto_vkOV', 'GeenAuto_GratisOV',
                        'GeenAuto_vkNeutraal', 'GeenAuto_vkFiets', 'GeenAuto_vkOV', 'GeenRijbewijs_GratisOV',
                        'GeenRijbewijs_vkNeutraal', 'GeenRijbewijs_vkFiets', 'GeenRijbewijs_vkOV']
    else:
        Basisgroepen = ['GratisAuto', 'GratisAuto_GratisOV', 'WelAuto_GratisOV', 'WelAuto_vkAuto',
                        'WelAuto_vkNeutraal', 'WelAuto_vkFiets', 'WelAuto_vkOV']

    logger.debug("autobezitgroepen zijn: %s", autobezitgroepen)

    Groepen = []
    for inkgr in inkgroepen:
        for bg in Basisgroepen:
            Groepen.append(f'{bg}_{inkgr}')
    logger.debug("Groepen: %s", Groepen)

    modaliteiten = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    headstringExcel = ['Zone', 'Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    soortbrandstof = ['fossiel', 'elektrisch']
    logger.debug("motieven: %s", motieven)

    if 'winkelnietdagelijksonderwijs' in motieven:
        Beroepsbevolkingperklasse = datasource.read_segs("Leerlingen", scenario=scenario, type_caster=float)
        Arbeidsplaats = datasource.read_segs("Leerlingenplaatsen", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = Routines.transponeren(Arbeidsplaats)
        logger.debug("Lengte Leerlingenplaatsen is %s", len(Arbeidsplaats))
    else:
        Beroepsbevolkingperklasse = datasource.read_segs("Beroepsbevolking_inkomensklasse", scenario=scenario, type_caster=float)
        Arbeidsplaats = datasource.read_segs("Arbeidsplaatsen_inkomensklasse", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = Routines.transponeren(Arbeidsplaats)
        logger.debug("Lengte arbeidsplaatsen is %s", len(Arbeidsplaats))

    Beroepsbevolkingtotalen = [sum(bbpk) for bbpk in Beroepsbevolkingperklasse]

    if 'sociaal-recreatief' in motieven:
        id = "L65plus_inkomensklasse" if '65+' in regime else "Inwoners_inkomensklasse"
        Inwonersperklasse = datasource.read_segs(id, scenario=scenario, type_caster=float)
        Inwonerstotalen = [sum(ipk) for ipk in Inwonersperklasse]

    Inkomensverdeling = np.zeros((len(Beroepsbevolkingperklasse), len(Beroepsbevolkingperklasse[0])))
    for i in range(len(Beroepsbevolkingperklasse)):
        for j in range(len(Beroepsbevolkingperklasse[0])):
            if Beroepsbevolkingtotalen[i] > 0:
                Inkomensverdeling[i][j] = Beroepsbevolkingperklasse[i][j]/Beroepsbevolkingtotalen[i]

    Inkomenstransverdeling = Routines.transponeren(Inkomensverdeling)

    for abg in autobezitgroepen:
        for mot in motieven:
            if mot == 'werk':
                Doelgroep = 'Beroepsbevolking'
            elif mot == 'winkelnietdagelijksonderwijs':
                Doelgroep = 'Leerlingen'
            else:
                Doelgroep = 'Inwoners'

            Verdelingsmatrix = datasource.read_segs(f"Verdeling_over_groepen_{Doelgroep}", type_caster=float, scenario=scenario)
            Verdelingstransmatrix = Routines.transponeren(Verdelingsmatrix)

            for ds in dagsoort:
                for inkgr in inkgroepen:
                    logger.debug('We zijn het nu aan het uitrekenen voor de inkomensgroep: %s', inkgr)
                    for mod in modaliteiten:
                        Bijhoudlijst = Routines.lijstvolnullen(len(Arbeidsplaats))
                        for gr in Groepen:
                            ink = Routines.inkomensgroepbepalen(gr)
                            if inkgr == ink or inkgr == 'alle':
                                vk = Routines.vindvoorkeur(gr, mod)
                                if mod == 'Fiets' or mod == 'EFiets':
                                    vkfiets = 'Fiets' if vk == 'Fiets' else ''
                                    Fietsmatrix = datasource.read_csv('Gewichten', f'{mod}_vk', ds, vk=vkfiets, regime=regime, mot=mot)

                                    if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                        Dezegroeplijst = potenties(Fietsmatrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                   Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                    else:
                                        Dezegroeplijst = bereken_potenties_nietwerk(Fietsmatrix, Inwonerstotalen, Verdelingstransmatrix,
                                                                           Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                           gr, Groepen)
                                    for i in range(len(Fietsmatrix)):
                                        Bijhoudlijst[i] += int(Dezegroeplijst[i])

                                elif mod == 'Auto':
                                    String = Routines.enkelegroep(mod,gr)
                                    logger.debug("String: %s", String)
                                    if 'WelAuto' in gr:
                                        for srtbr in soortbrandstof:
                                            Matrix = datasource.read_csv('Gewichten', f'{String}_vk', ds, vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)

                                            if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                                Dezegroeplijst1 = potenties ( Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                                     Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                            else:
                                                Dezegroeplijst1 = bereken_potenties_nietwerk(Matrix, Inwonerstotalen, Verdelingstransmatrix,
                                                                                   Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                                   gr, Groepen)
                                            if srtbr == 'elektrisch':
                                                K = percentageelektrisch.get(inkgr)/100
                                                logger.debug('aandeel elektrisch is %s', K)
                                                DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                            else:
                                                L = 1 - percentageelektrisch.get(inkgr)/100
                                                logger.debug('aandeel fossiel is %s', L)
                                                DezegroeplijstF = [x * L for x in Dezegroeplijst1]

                                        for i in range(len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]

                                        for i in range(len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                    else:
                                        Matrix = datasource.read_csv('Gewichten', f'{String}_vk',ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                        if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                            Dezegroeplijst = potenties(Matrix, Arbeidsplaatsen,
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
                                        for i in range(len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                        logger.debug('Bijhoudlijst niet fossiel is: %s', Bijhoudlijst)
                                elif mod == 'OV':
                                    String = Routines.enkelegroep(mod, gr)
                                    Matrix = datasource.read_csv('Gewichten', f'{String}_vk',ds, vk=vk, ink=ink, regime=regime, mot=mot)
                                    if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                        Dezegroeplijst = potenties(Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                           Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                           inkgr, gr, inkgroepen, Groepen)
                                    else:
                                        Dezegroeplijst = bereken_potenties_nietwerk(Matrix, Inwonerstotalen,
                                                                                    Verdelingstransmatrix,
                                                                                    Inkomenstransverdeling[
                                                                                        inkgroepen.index(inkgr)],
                                                                                    gr, Groepen)
                                    for i in range(len(Matrix)):
                                        Bijhoudlijst[i] += int(Dezegroeplijst[i])

                                else:
                                    String = Routines.combigroep(mod, gr)
                                    logger.debug('de gr is %s', gr)
                                    logger.debug('de string is %s', String)
                                    if String[0] == 'A':
                                        for srtbr in soortbrandstof:
                                            Matrix = datasource.read_csv('Gewichten', f'{String}_vk', ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot, srtbr=srtbr)
                                            if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                                Dezegroeplijst1 = potenties(Matrix, Arbeidsplaatsen,
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

                                        for i in range(len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]

                                        for i in range(len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                    else:
                                        Matrix = datasource.read_csv('Gewichten', f'{String}_vk', ds, subtopic='Combinaties', vk=vk, ink=ink, regime=regime, mot=mot)

                                        if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                            Dezegroeplijst = potenties ( Matrix, Arbeidsplaatsen, Verdelingstransmatrix,
                                                                                 Inkomenstransverdeling[inkgroepen.index(inkgr)], inkgr, gr, inkgroepen, Groepen)
                                        else:
                                            Dezegroeplijst = bereken_potenties_nietwerk(Matrix, Inwonerstotalen, Verdelingstransmatrix,
                                                                               Inkomenstransverdeling[inkgroepen.index(inkgr)],
                                                                               gr, Groepen)
                                        for i in range(len ( Matrix ) ):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])

                        datasource.write_csv(Bijhoudlijst, abg, 'Totaal', ds, mod=mod, ink=inkgr, mot=mot, subtopic='Bestemmingen')
                    # En tot slot alles bij elkaar harken:
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten :
                        Totaalrij = datasource.read_csv(abg, 'Totaal', ds, mod=mod, ink=inkgr, mot=mot, subtopic='Bestemmingen', type_caster=int)
                        Generaaltotaal_potenties.append(Totaalrij)
                    Generaaltotaaltrans = Routines.transponeren(Generaaltotaal_potenties)
                    datasource.write_csv(Generaaltotaaltrans, abg, 'Ontpl_totaal', ds, ink=inkgr, header=headstring, mot=mot, subtopic='Bestemmingen')
                    datasource.write_xlsx(Generaaltotaaltrans, abg, 'Ontpl_totaal', ds, ink=inkgr, header=headstringExcel, mot=mot, subtopic='Bestemmingen')

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        Totaalrij = datasource.read_csv(abg, 'Totaal', ds, mod=mod, ink=inkgr, mot=mot, subtopic='Bestemmingen', type_caster=int)
                        Generaalmatrix.append(Totaalrij)
                    if len(inkgroepen)>1:
                        Generaaltotaaltrans = Routines.transponeren(Generaalmatrix)
                    else:
                        Generaaltotaaltrans = Generaalmatrix
                    for i in range(len(Beroepsbevolkingperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range(len(Beroepsbevolkingperklasse[0])):
                            if Beroepsbevolkingperklasse[i][j] > 0:
                                Generaalmatrixproduct[i].append(int(Generaaltotaaltrans[i][j]*Beroepsbevolkingperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    datasource.write_xlsx(Generaaltotaaltrans, abg, 'Ontpl_totaal', ds, mod=mod, header=header, mot=mot, subtopic='Bestemmingen')
                    datasource.write_xlsx(Generaalmatrixproduct, abg, 'Ontpl_totaalproduct', ds, mod=mod, header=header, mot=mot, subtopic='Bestemmingen')
