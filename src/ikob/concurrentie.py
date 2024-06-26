import logging
import ikob.Routines as Routines
from ikob.ConfiguratieDefinitie import Inkomen
import numpy as np
from typing import Dict
from numpy.typing import NDArray
from ikob.datasource import DataKey, DataSource

logger = logging.getLogger(__name__)


def get_matrix(datasource: DataSource,
               gewichten_enkel: Dict[DataKey, NDArray],
               gewichten_combi: Dict[DataKey, NDArray],
               gr, mod, mot, regime, ds, ink, inkgr, K):
    vk = Routines.vindvoorkeur(gr, mod)

    if mod == 'Fiets' or mod == 'EFiets':
        vkfiets = 'Fiets' if vk == 'Fiets' else ''
        key = DataKey('Gewichten',
                      f"{mod}_vk",
                      dagsoort=ds,
                      regime=regime,
                      motief=mot,
                      voorkeur=vkfiets)
        return gewichten_enkel[key]

    enkele_groep = Routines.enkelegroep(mod, gr)
    combi_groep = Routines.combigroep(mod, gr)

    if mod == 'Auto' and 'WelAuto' in gr or combi_groep[0] == 'A':
        subtopic = '' if mod == 'Auto' else 'Combinaties'
        gewichten = gewichten_enkel if mod == 'Auto' else gewichten_combi
        string = enkele_groep if mod == 'Auto' else combi_groep
        key = DataKey('Gewichten',
                      f"{string}_vk",
                      dagsoort=ds,
                      regime=regime,
                      motief=mot,
                      voorkeur=vk,
                      inkomen=ink,
                      subtopic=subtopic,
                      brandstof="fossiel")
        Matrix_fossiel = gewichten[key]

        key = DataKey('Gewichten',
                      f"{string}_vk",
                      dagsoort=ds,
                      regime=regime,
                      motief=mot,
                      voorkeur=vk,
                      inkomen=ink,
                      subtopic=subtopic,
                      brandstof="elektrisch")
        Matrix_elektrisch = gewichten[key]
        return K * Matrix_elektrisch + (1 - K) * Matrix_fossiel

    if mod == 'Auto' or mod == 'OV':
        key = DataKey('Gewichten',
                      f"{enkele_groep}_vk",
                      dagsoort=ds,
                      regime=regime,
                      motief=mot,
                      voorkeur=vk,
                      inkomen=ink)
        return gewichten_enkel[key]

    key = DataKey('Gewichten',
                  f"{combi_groep}_vk",
                  dagsoort=ds,
                  regime=regime,
                  motief=mot,
                  voorkeur=vk,
                  inkomen=ink,
                  subtopic="Combinaties")
    return gewichten_combi[key]


def concurrentie_om_arbeidsplaatsen(config, datasource: DataSource,
                                    gewichten_enkel: Dict[DataKey, NDArray],
                                    gewichten_combi: Dict[DataKey, NDArray],
                                    herkomsten: Dict[DataKey, NDArray]):
    return concurrentie(config, datasource, gewichten_enkel, gewichten_combi, herkomsten, inwoners=False)


def concurrentie_om_inwoners(config, datasource: DataSource,
                             gewichten_enkel: Dict[DataKey, NDArray],
                             gewichten_combi: Dict[DataKey, NDArray],
                             herkomsten: Dict[DataKey, NDArray]):
    return concurrentie(config, datasource, gewichten_enkel, gewichten_combi, herkomsten, inwoners=True)


def concurrentie(config, datasource: DataSource,
                 gewichten_enkel: Dict[DataKey, NDArray],
                 gewichten_combi: Dict[DataKey, NDArray],
                 herkomsten: Dict[DataKey, NDArray],
                 inwoners: bool = True):
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
    inkgroepen = [inkomen.value for inkomen in Inkomen]
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

    subtopic_concurrentie = "inwoners" if inwoners else "arbeidsplaatsen"
    subtopic_gewichten = "Bestemmingen" if inwoners else "Herkomsten"

    concurrenties = dict()

    for abg in autobezitgroepen:
        for mot in motieven:
            if mot == 'werk':
                Doelgroep = 'Beroepsbevolking'
            elif mot == 'winkelnietdagelijksonderwijs':
                Doelgroep = 'Leerlingen'
            else:
                Doelgroep = 'Inwoners'

            Verdelingsmatrix = datasource.read_segs(f"Verdeling_over_groepen_{Doelgroep}", scenario=scenario, type_caster=float)

            for ds in dagsoort:
                for i_inkgr, inkgr in enumerate(inkgroepen):
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten:
                        key = DataKey(abg, "Totaal",
                                      dagsoort=ds,
                                      motief=mot,
                                      modaliteit=mod,
                                      inkomen=inkgr,
                                      subtopic=subtopic_gewichten)
                        Bereik = herkomsten[key]

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
                                Matrix = get_matrix(datasource, gewichten_enkel, gewichten_combi, gr, mod, mot, regime, ds, ink, inkgr, K)

                                concurrentie = Matrix @ (inwoners_of_arbeidsplaatsen / np.where(Bereik > 0, Bereik, 1.0))
                                concurrentie_totaal += concurrentie * verdeling / np.where(inkomens_verdeling > 0, inkomens_verdeling, 1)

                        key = DataKey('Concurrentie', id='Totaal',
                                      dagsoort=ds,
                                      subtopic=subtopic_concurrentie,
                                      inkomen=inkgr,
                                      motief=mot,
                                      modaliteit=mod)
                        concurrenties[key] = concurrentie_totaal.copy()

                        Generaaltotaal_potenties.append(concurrenties[key])
                        Generaaltotaaltrans = Routines.transponeren(Generaaltotaal_potenties)
                        key = DataKey('Concurrentie', id='Ontpl_conc',
                                      dagsoort=ds,
                                      subtopic=subtopic_concurrentie,
                                      inkomen=inkgr,
                                      motief=mot)
                        datasource.write_csv(Generaaltotaaltrans, key, header=headstring)
                        datasource.write_xlsx(Generaaltotaaltrans, key, header=headstringExcel)

                header = ['Zone', *[inkomen.value for inkomen in Inkomen]]
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        key = DataKey("Concurrentie", "Totaal",
                                      dagsoort=ds,
                                      motief=mot,
                                      modaliteit=mod,
                                      inkomen=inkgr,
                                      subtopic=subtopic_concurrentie)
                        Generaalmatrix.append(concurrenties[key])
                        Generaaltotaaltrans = Routines.transponeren(Generaalmatrix)

                    for i in range(len(Inwonersperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range(len(Inwonersperklasse[0])):
                            if Inwonersperklasse[i][j] > 0:
                                Generaalmatrixproduct[i].append(round(Generaaltotaaltrans[i][j]*Inwonersperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    key = DataKey('Concurrentie', id='Ontpl_conc',
                                  dagsoort=ds,
                                  subtopic=subtopic_concurrentie,
                                  motief=mot,
                                  modaliteit=mod)
                    datasource.write_xlsx(Generaaltotaaltrans, key, header=header)

                    key = DataKey('Concurrentie', id='Ontpl_concproduct',
                                  dagsoort=ds,
                                  subtopic=subtopic_concurrentie,
                                  motief=mot,
                                  modaliteit=mod)
                    datasource.write_xlsx(Generaalmatrixproduct, key, header=header)

    return concurrenties
