import logging
import ikob.utils as utils
import numpy as np
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def get_gewichten_matrix(gewichten_enkel: DataSource,
                         gewichten_combi: DataSource,
                         gr, mod, mot, regime, ds, ink, inkgr,
                         ratio_electric: float):
    vk = utils.find_preference(gr, mod)

    if mod == 'Fiets' or mod == 'EFiets':
        vkfiets = 'Fiets' if vk == 'Fiets' else ''
        key = DataKey(f"{mod}_vk",
                      part_of_day=ds,
                      regime=regime,
                      motive=mot,
                      preference=vkfiets)
        return gewichten_enkel.get(key)

    enkele_groep = utils.single_group(mod, gr)
    combi_groep = utils.combined_group(mod, gr)

    if mod == 'Auto' and 'WelAuto' in gr or combi_groep[0] == 'A':
        subtopic = '' if mod == 'Auto' else 'combinaties'
        gewichten = gewichten_enkel if mod == 'Auto' else gewichten_combi
        string = enkele_groep if mod == 'Auto' else combi_groep
        key = DataKey(f"{string}_vk",
                      part_of_day=ds,
                      regime=regime,
                      motive=mot,
                      preference=vk,
                      income=ink,
                      subtopic=subtopic,
                      fuel_kind="fossiel")
        Matrix_fossiel = gewichten.get(key)

        key = DataKey(f"{string}_vk",
                      part_of_day=ds,
                      regime=regime,
                      motive=mot,
                      preference=vk,
                      income=ink,
                      subtopic=subtopic,
                      fuel_kind="elektrisch")
        Matrix_elektrisch = gewichten.get(key)
        return ratio_electric * Matrix_elektrisch + (1 - ratio_electric) * Matrix_fossiel

    if mod == 'Auto' or mod == 'OV':
        key = DataKey(f"{enkele_groep}_vk",
                      part_of_day=ds,
                      regime=regime,
                      motive=mot,
                      preference=vk,
                      income=ink)
        return gewichten_enkel.get(key)

    key = DataKey(f"{combi_groep}_vk",
                  part_of_day=ds,
                  regime=regime,
                  motive=mot,
                  preference=vk,
                  income=ink,
                  subtopic="combinaties")
    return gewichten_combi.get(key)


def competition_on_jobs(config,
                                    gewichten_enkel: DataSource,
                                    gewichten_combi: DataSource,
                                    herkomsten: DataSource) -> DataSource:
    return concurrentie(config, gewichten_enkel, gewichten_combi, herkomsten, inwoners=False)


def competition_on_citizens(config,
                             gewichten_enkel: DataSource,
                             gewichten_combi: DataSource,
                             herkomsten: DataSource) -> DataSource:
    return concurrentie(config, gewichten_enkel, gewichten_combi, herkomsten, inwoners=True)


def concurrentie(config,
                 gewichten_enkel: DataSource,
                 gewichten_combi: DataSource,
                 herkomsten: DataSource,
                 inwoners: bool = True) -> DataSource:
    if inwoners:
        msg = "Concurrentiepositie voor bedrijven qua bereikbaarheid"
    else:
        msg = "Concurrentiepositie voor bereik arbeidsplaatsen"
    logger.info(msg)

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

    concurrenties = DataSource(config, DataType.COMPETITION)

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
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten:
                        key = DataKey("Totaal",
                                      part_of_day=ds,
                                      motive=mot,
                                      modality=mod,
                                      income=inkgr,
                                      group=abg)
                        Bereik = herkomsten.get(key)

                        concurrentie_totaal = np.zeros(len(Arbeidsplaatsen))
                        for i_gr, gr in enumerate(Groepen):
                            if inwoners:
                                inwoners_of_arbeidsplaatsen = Inwonersperklasse.T[i_inkgr]
                            else:
                                inwoners_of_arbeidsplaatsen = Arbeidsplaatsen.T[i_inkgr]
                            verdeling = Verdelingsmatrix[:, i_gr]
                            inkomens_verdeling = Inkomensverdeling[:, i_inkgr]

                            ink = utils.group_income_level(gr)
                            if inkgr == ink or inkgr == 'alle':
                                K = percentageelektrisch.get(inkgr)/100
                                Matrix = get_gewichten_matrix(gewichten_enkel, gewichten_combi, gr, mod, mot, regime, ds, ink, inkgr, K)

                                concurrentie = Matrix @ (inwoners_of_arbeidsplaatsen / np.where(Bereik > 0, Bereik, 1.0))
                                concurrentie_totaal += concurrentie * verdeling / np.where(inkomens_verdeling > 0, inkomens_verdeling, 1)

                        key = DataKey(id='Totaal',
                                      part_of_day=ds,
                                      subtopic=subtopic_concurrentie,
                                      income=inkgr,
                                      motive=mot,
                                      modality=mod)
                        concurrenties.set(key, concurrentie_totaal.copy())

                        Generaaltotaal_potenties.append(concurrenties.get(key))
                        Generaaltotaaltrans = utils.transpose(Generaaltotaal_potenties)
                        key = DataKey(id='Ontpl_conc',
                                      part_of_day=ds,
                                      subtopic=subtopic_concurrentie,
                                      income=inkgr,
                                      motive=mot)
                        concurrenties.write_csv(Generaaltotaaltrans, key, header=headstring)
                        concurrenties.write_xlsx(Generaaltotaaltrans, key, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        key = DataKey("Totaal",
                                      part_of_day=ds,
                                      motive=mot,
                                      modality=mod,
                                      income=inkgr,
                                      subtopic=subtopic_concurrentie)
                        Generaalmatrix.append(concurrenties.get(key))
                        Generaaltotaaltrans = utils.transpose(Generaalmatrix)

                    for i in range(len(Inwonersperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range(len(Inwonersperklasse[0])):
                            if Inwonersperklasse[i][j] > 0:
                                Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    key = DataKey(id='Ontpl_conc',
                                  part_of_day=ds,
                                  subtopic=subtopic_concurrentie,
                                  motive=mot,
                                  modality=mod)
                    concurrenties.write_xlsx(Generaaltotaaltrans, key, header=header)

                    key = DataKey(id='Ontpl_concproduct',
                                  part_of_day=ds,
                                  subtopic=subtopic_concurrentie,
                                  motive=mot,
                                  modality=mod)
                    concurrenties.write_xlsx(Generaalmatrixproduct, key, header=header)

    return concurrenties
