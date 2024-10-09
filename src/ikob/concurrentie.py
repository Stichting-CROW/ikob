import logging
import ikob.Routines as Routines
import numpy as np
from ikob.datasource import DataSource, SegsSource

logger = logging.getLogger(__name__)


def get_gewichten_matrix(datasource: DataSource, gr, mod, mot, regime, ds, ink, inkgr, ratio_electric):
    vk = Routines.vindvoorkeur(gr, mod)

    if mod == 'Fiets' or mod == 'EFiets':
        vkfiets = 'Fiets' if vk == 'Fiets' else ''
        return datasource.read_csv('gewichten', f'{mod}_vk', ds, vk=vkfiets, regime=regime, mot=mot)

    enkele_groep = Routines.enkelegroep(mod, gr)
    combi_groep = Routines.combigroep(mod, gr)

    if mod == 'Auto' and 'WelAuto' in gr or combi_groep[0] == 'A':
        subtopic = '' if mod == 'Auto' else 'combinaties'
        string = enkele_groep if mod == 'Auto' else combi_groep
        Matrix_fossiel = datasource.read_csv('gewichten', f"{string}_vk", ds, subtopic=subtopic, vk=vk, ink=ink, regime=regime, mot=mot, srtbr="fossiel")
        Matrix_elektrisch = datasource.read_csv('gewichten', f"{string}_vk", ds, subtopic=subtopic, vk=vk, ink=ink, regime=regime, mot=mot, srtbr="elektrisch")
        return ratio_electric * Matrix_elektrisch + (1 - ratio_electric) * Matrix_fossiel

    if mod == 'Auto' or mod == 'OV':
        return datasource.read_csv('gewichten', f"{enkele_groep}_vk", ds, vk=vk, ink=ink, regime=regime, mot=mot)

    return datasource.read_csv('gewichten', f'{combi_groep}_vk', ds, subtopic='combinaties', vk=vk, ink=ink, regime=regime, mot=mot)


def concurrentie_om_arbeidsplaatsen(config, datasource: DataSource):
    return concurrentie(config, datasource, inwoners=False)


def concurrentie_om_inwoners(config, datasource: DataSource):
    return concurrentie(config, datasource, inwoners=True)


def concurrentie(config, datasource: DataSource, inwoners: bool = True):
    project_config = config['project']
    skims_config = config['skims']
    verdeling_config = config['verdeling']
    dagsoort = skims_config['dagsoort']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config['motieven']
    autobezitgroepen = project_config['welke_groepen']
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
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    headstringExcel = ['Zone', 'Fiets', 'Auto', 'OV', 'Auto-Fiets' 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']

    segs_source = SegsSource(config)

    if 'winkelnietdagelijksonderwijs' in motieven:
        Inwonersperklasse = segs_source.read("Leerlingen", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = segs_source.read("Leerlingenplaatsen", scenario=scenario, type_caster=float)
    else:
        Inwonersperklasse = segs_source.read("Beroepsbevolking_inkomensklasse", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = segs_source.read("Arbeidsplaatsen_inkomensklasse", scenario=scenario, type_caster=float)

    Inwonerstotalen = [sum(ipk) for ipk in Inwonersperklasse]

    Inkomensverdeling = np.zeros((len(Inwonersperklasse), len(Inwonersperklasse[0])))
    for i in range(len(Inwonersperklasse)):
        for j in range(len(Inwonersperklasse[0])):
            if Inwonerstotalen[i] > 0:
                Inkomensverdeling[i][j] = Inwonersperklasse[i][j]/Inwonerstotalen[i]

    subtopic_concurrentie = "inwoners" if inwoners else "arbeidsplaatsen"
    subtopic_gewichten = "bestemmingen" if inwoners else "herkomsten"

    for abg in autobezitgroepen:
        for mot in motieven:
            if mot == 'werk':
                Doelgroep = 'Beroepsbevolking'
            elif mot == 'winkelnietdagelijksonderwijs':
                Doelgroep = 'Leerlingen'
            else:
                Doelgroep = 'Inwoners'

            Verdelingsmatrix = segs_source.read(f"Verdeling_over_groepen_{Doelgroep}", scenario=scenario, type_caster=float)

            for ds in dagsoort:
                for i_inkgr, inkgr in enumerate(inkgroepen):
                    for mod in modaliteiten:
                        Bereik = datasource.read_csv(abg, "Totaal", ds, mot=mot, mod=mod, ink=inkgr, subtopic=subtopic_gewichten)
                        concurrentie_totaal = np.zeros(len(Arbeidsplaatsen))
                        for i_gr, gr in enumerate(Groepen):
                            if inwoners:
                                inwoners_of_arbeidsplaatsen = Inwonersperklasse.T[i_inkgr]
                            else:
                                inwoners_of_arbeidsplaatsen = Arbeidsplaatsen.T[i_inkgr]
                            verdeling = Verdelingsmatrix[:, i_gr]
                            inkomens_verdeling = Inkomensverdeling[:, i_inkgr]

                            ink = Routines.inkomensgroepbepalen(gr)
                            if inkgr == ink or inkgr == 'alle':
                                K = percentageelektrisch.get(inkgr)/100
                                Matrix = get_gewichten_matrix(datasource, gr, mod, mot, regime, ds, ink, inkgr, K)

                                concurrentie = Matrix @ (inwoners_of_arbeidsplaatsen / np.where(Bereik > 0, Bereik, 1.0))
                                concurrentie_totaal += concurrentie * verdeling / np.where(inkomens_verdeling > 0, inkomens_verdeling, 1)

                        datasource.write_csv(concurrentie_totaal, 'concurrentie', 'Totaal', ds, subtopic=subtopic_concurrentie, mot=mot, mod=mod, ink=inkgr)

                    # En tot slot alles bij elkaar harken:
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten:
                        Totaalrij = datasource.read_csv('concurrentie', "Totaal", ds, subtopic=subtopic_concurrentie, mot=mot, mod=mod, ink=inkgr)
                        Generaaltotaal_potenties.append(Totaalrij)
                        Generaaltotaaltrans = Routines.transponeren(Generaaltotaal_potenties)
                        datasource.write_csv(Generaaltotaaltrans, 'concurrentie', 'Ontpl_conc', ds, subtopic=subtopic_concurrentie, mot=mot, ink=inkgr, header=headstring)
                        datasource.write_xlsx(Generaaltotaaltrans, 'concurrentie', 'Ontpl_conc', ds, subtopic=subtopic_concurrentie, mot=mot, ink=inkgr, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        Totaalrij = datasource.read_csv("concurrentie", "Totaal", ds, subtopic=subtopic_concurrentie, mot=mot, mod=mod, ink=inkgr)
                        Generaalmatrix.append(Totaalrij)
                        Generaaltotaaltrans = Routines.transponeren(Generaalmatrix)

                    for i in range(len(Inwonersperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range(len(Inwonersperklasse[0])):
                            if Inwonersperklasse[i][j] > 0:
                                Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    datasource.write_xlsx(Generaaltotaaltrans, 'concurrentie', 'Ontpl_conc', ds, subtopic=subtopic_concurrentie, mot=mot, mod=mod, header=header)
                    datasource.write_xlsx(Generaalmatrixproduct, 'concurrentie', 'Ontpl_concproduct', ds, subtopic=subtopic_concurrentie, mot=mot, mod=mod, header=header)
