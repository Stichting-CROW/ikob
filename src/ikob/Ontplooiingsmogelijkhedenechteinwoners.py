import logging
import ikob.Routines as Routines
import numpy as np

from ikob.concurrentie import get_matrix
from ikob.datasource import DataKey, DataSource


logger = logging.getLogger(__name__)


def ontplooingsmogelijkheden_echte_inwoners(config, datasource: DataSource):
    logger.info("Bereikbaarheid arbeidsplaatsen voor inwoners")

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

    if 'alle groepen' in autobezitgroepen:
        Basisgroepen = ['GratisAuto', 'GratisAuto_GratisOV', 'WelAuto_GratisOV', 'WelAuto_vkAuto',
                        'WelAuto_vkNeutraal', 'WelAuto_vkFiets', 'WelAuto_vkOV', 'GeenAuto_GratisOV',
                        'GeenAuto_vkNeutraal', 'GeenAuto_vkFiets', 'GeenAuto_vkOV', 'GeenRijbewijs_GratisOV',
                        'GeenRijbewijs_vkNeutraal', 'GeenRijbewijs_vkFiets', 'GeenRijbewijs_vkOV']
    else:
        Basisgroepen = ['GratisAuto', 'GratisAuto_GratisOV', 'WelAuto_GratisOV', 'WelAuto_vkAuto',
                        'WelAuto_vkNeutraal', 'WelAuto_vkFiets', 'WelAuto_vkOV']

    Groepen = []
    for inkgr in inkgroepen:
        for bg in Basisgroepen:
            Groepen.append(f'{bg}_{inkgr}')

    modaliteiten = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    headstring = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    headstringExcel = ['Zone', 'Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV', 'Auto_OV_Fiets']
    soortbrandstof = ['fossiel', 'elektrisch']

    if 'winkelnietdagelijksonderwijs' in motieven:
        Beroepsbevolkingperklasse = datasource.read_segs("Leerlingen", scenario=scenario, type_caster=float)
        Arbeidsplaats = datasource.read_segs("Leerlingenplaatsen", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = Routines.transponeren(Arbeidsplaats)
    else:
        Beroepsbevolkingperklasse = datasource.read_segs("Beroepsbevolking_inkomensklasse", scenario=scenario, type_caster=float)
        Arbeidsplaats = datasource.read_segs("Arbeidsplaatsen_inkomensklasse", scenario=scenario, type_caster=float)
        Arbeidsplaatsen = Routines.transponeren(Arbeidsplaats)

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
            if abg == 'alle groepen':
                Verdelingsmatrix = datasource.read_segs(f"Verdeling_over_groepen_{Doelgroep}", type_caster=float, scenario=scenario)
            else:
                Verdelingsmatrix = datasource.read_segs(f"Verdeling_over_groepen_{Doelgroep}_alleen_autobezit", type_caster=float, scenario=scenario)

            Verdelingstransmatrix = Routines.transponeren(Verdelingsmatrix)

            for ds in dagsoort:
                for i_inkgr, inkgr in enumerate(inkgroepen):
                    if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                        arbeidsplaats = np.array(Arbeidsplaatsen[i_inkgr])
                    else:
                        arbeidsplaats = Inwonerstotalen

                    inkomens = np.array(Inkomenstransverdeling[i_inkgr])
                    for mod in modaliteiten:
                        potentie_totaal = np.zeros(len(Arbeidsplaats), dtype=int)

                        for igr, gr in enumerate(Groepen):
                            if mot == 'werk' or mot == 'winkelnietdagelijksonderwijs':
                                verdeling = np.array(Verdelingstransmatrix[igr])
                            else:
                                verdeling = Verdelingstransmatrix

                            ink = Routines.inkomensgroepbepalen(gr)
                            if inkgr == ink or inkgr == 'alle':
                                K = percentageelektrisch.get(inkgr)/100
                                Matrix = get_matrix(datasource, gr, mod, mot, regime, ds, ink, inkgr, K)

                                potentie = Matrix @ arbeidsplaats * verdeling
                                potentie = np.where(inkomens > 0, potentie / inkomens, 0)
                                potentie_totaal += potentie.astype(int)

                        key = DataKey(abg, 'Totaal',
                                      dagsoort=ds,
                                      subtopic='Bestemmingen',
                                      inkomen=inkgr,
                                      motief=mot,
                                      modaliteit=mod)
                        datasource.write_csv(potentie_totaal, key)
                    # En tot slot alles bij elkaar harken:
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten:
                        key = DataKey(abg, 'Totaal',
                                      dagsoort=ds,
                                      subtopic='Bestemmingen',
                                      inkomen=inkgr,
                                      motief=mot,
                                      modaliteit=mod)
                        Totaalrij = datasource.read_csv(key, type_caster=int)
                        Generaaltotaal_potenties.append(Totaalrij)

                    Generaaltotaaltrans = Routines.transponeren(Generaaltotaal_potenties)
                    key = DataKey(abg, 'Ontpl_totaal',
                                  dagsoort=ds,
                                  subtopic='Bestemmingen',
                                  inkomen=inkgr,
                                  motief=mot)
                    datasource.write_csv(Generaaltotaaltrans, key, header=headstring)
                    datasource.write_xlsx(Generaaltotaaltrans, key, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        key = DataKey(abg, 'Totaal',
                                      dagsoort=ds,
                                      subtopic='Bestemmingen',
                                      inkomen=inkgr,
                                      motief=mot,
                                      modaliteit=mod)
                        Totaalrij = datasource.read_csv(key, type_caster=int)
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

                    key = DataKey(abg, 'Ontpl_totaal',
                                  dagsoort=ds,
                                  subtopic='Bestemmingen',
                                  motief=mot,
                                  modaliteit=mod)
                    datasource.write_xlsx(Generaaltotaaltrans, key, header=header)
                    key = DataKey(abg, 'Ontpl_totaalproduct',
                                  dagsoort=ds,
                                  subtopic='Bestemmingen',
                                  motief=mot,
                                  modaliteit=mod)
                    datasource.write_xlsx(Generaalmatrixproduct, key, header=header)
