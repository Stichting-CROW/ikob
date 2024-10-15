import logging
import ikob.utils as utils
from ikob.datasource import DataKey, DataSource, DataType, SegsSource

logger = logging.getLogger(__name__)


def potenties(Matrix, Inwonerstrans, gr, Groepen):
    Dezegroeplijst = []
    for i in range(len(Matrix)):
        Gewogenmatrix = []
        for Getal1, Getal2 in zip(Matrix[i], Inwonerstrans[Groepen.index(gr)]):
            Gewogenmatrix.append(Getal1 * Getal2)
        Dezegroeplijst.append(sum(Gewogenmatrix))
    return Dezegroeplijst


def inwonersfile_maken (Verdelingsmatrix, Beroepsbevolking):
    Inwonersfile = []
    for i in range (len(Beroepsbevolking)) :
        Inwonersfile.append([])
        for j in range (len(Verdelingsmatrix[0])) :
            Inwonersfile[i].append(round(Beroepsbevolking[i]*Verdelingsmatrix[i][j]))
    return Inwonersfile


def possible_companies(config,
                       gewichten_enkel: DataSource,
                       gewichten_combi: DataSource) -> DataSource:
    logger.info("Potentie bereikbaarheid voor bedrijven en instellingen")

    project_config=config['project']
    skims_config = config['skims']
    verdeling_config = config['verdeling']
    dagsoort = skims_config['dagsoort']

    # Ophalen van instellingen
    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motieven = project_config['motieven']
    autobezitgroepen = project_config['welke_groepen']
    logger.debug("motieven: %s", motieven)
    soortbrandstof = ['fossiel', 'elektrisch']
    percentageelektrisch = verdeling_config ['Percelektrisch']

    # Vaste waarden
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

    modaliteiten = ['Fiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_OV',
                      'Auto_OV_Fiets']

    inkgroepen = ['laag', 'middellaag', 'middelhoog', 'hoog']
    headstring = ['Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                      'Auto_OV_Fiets', 'Auto_OV_EFiets']
    headstringExcel=['Zone', 'Fiets', 'EFiets', 'Auto', 'OV', 'Auto_Fiets', 'OV_Fiets', 'Auto_EFiets', 'OV_EFiets', 'Auto_OV',
                      'Auto_OV_Fiets', 'Auto_OV_EFiets']

    segs_source = SegsSource(config)

    #Grverdelingfile=Grverdelingfile.replace('.csv','')
    if 'werk' in motieven:
        Verdelingsmatrix = segs_source.read("Verdeling_over_groepen_Beroepsbevolking", scenario=scenario, type_caster=float)
    elif 'winkelnietdagelijksonderwijs' in motieven:
        Verdelingsmatrix = segs_source.read("Verdeling_over_groepen_Leerlingen", scenario=scenario, type_caster=float)
    if 'winkelnietdagelijksonderwijs' in motieven:
        Beroepsbevolking_inkomensklasse =  segs_source.read("Leerlingen", scenario=scenario, type_caster=int)
        Arbeidsplaatsenperklasse = segs_source.read("Leerlingenplaatsen", scenario=scenario, type_caster=float)
    else:
        Beroepsbevolking_inkomensklasse =  segs_source.read("Beroepsbevolking_inkomensklasse", scenario=scenario, type_caster=int)
        Arbeidsplaatsenperklasse = segs_source.read("Arbeidsplaatsen_inkomensklasse", scenario=scenario, type_caster=float)

    Beroepsbevolking = []

    for i in range (len(Beroepsbevolking_inkomensklasse)):
        Beroepsbevolking.append(sum(Beroepsbevolking_inkomensklasse[i]))
    #Volwassenenfilenaam = os.path.join(SEGSdirectory, f'Beroepsbevolking{scenario}')
    #Volwassenen = utils.read_csv_int (Volwassenenfilenaam)
    logger.debug('Lengte inwoners is %d', len(Beroepsbevolking))

    Inwoners = inwonersfile_maken (Verdelingsmatrix, Beroepsbevolking)
    Inwonerstransmatrix = utils.transpose(Inwoners)

    herkomsten = DataSource(config, DataType.ORIGINS)

    for abg in autobezitgroepen:
        for mot in motieven:
            if mot == 'werk':
                Doelgroep = 'Beroepsbevolking'
            elif mot == 'winkelnietdagelijksonderwijs':
                Doelgroep = 'Leerlingen'
            else:
                Doelgroep = 'Inwoners'

            if abg == "alle groepen":
                Verdelingsmatrix = segs_source.read(f"Verdeling_over_groepen_{Doelgroep}", scenario=scenario, type_caster=float)
            else:
                Verdelingsmatrix = segs_source.read(f"Verdeling_over_groepen_{Doelgroep}_alleen_autobezit", scenario=scenario, type_caster=float)

            for ds in dagsoort:
                for inkgr in inkgroepen:
                    Generaaltotaal_potenties = []
                    for mod in modaliteiten:
                        Bijhoudlijst = utils.zeros(len(Beroepsbevolking))
                        for gr in Groepen:
                            ink = utils.group_income_level ( gr )
                            if inkgr == ink or inkgr == 'alle':
                                vk = utils.find_preference (gr, mod)
                                if mod == 'Fiets' or mod == 'EFiets':
                                    if vk == 'Fiets':
                                        vkklad = 'Fiets'
                                    else:
                                        vkklad = ''

                                    key = DataKey(f'{mod}_vk',
                                                  part_of_day=ds,
                                                  preference=vkklad,
                                                  regime=regime,
                                                  motive=mot)
                                    Fietsmatrix = gewichten_enkel.get(key)
                                    Dezegroeplijst = potenties (Fietsmatrix, Inwonerstransmatrix, gr, Groepen)

                                    for i in range(0, len(Fietsmatrix) ):
                                        Bijhoudlijst[i]+= round(Dezegroeplijst[i])
                                elif mod == 'Auto':
                                    String = utils.single_group(mod, gr)
                                    if 'WelAuto' in gr:
                                        for srtbr in soortbrandstof:
                                            key = DataKey(f'{String}_vk',
                                                          part_of_day=ds,
                                                          preference=vk,
                                                          income=ink,
                                                          regime=regime,
                                                          motive=mot,
                                                          fuel_kind=srtbr)
                                            Matrix = gewichten_enkel.get(key)

                                            Dezegroeplijst1 = potenties(Matrix, Inwonerstransmatrix, gr, Groepen)
                                            if srtbr == 'elektrisch':
                                                K = percentageelektrisch.get(inkgr) / 100
                                                logger.debug('aandeel elektrisch is: %s', K)
                                                DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                            else:
                                                L = 1 - percentageelektrisch.get(inkgr) / 100
                                                logger.debug('aandeel fossiel is %s', L)
                                                DezegroeplijstF = [x * L for x in Dezegroeplijst1]
                                        for i in range(len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                        for i in range(0, len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                    else:
                                        key = DataKey(f'{String}_vk',
                                                      part_of_day=ds,
                                                      preference=vk,
                                                      income=ink,
                                                      regime=regime,
                                                      motive=mot)
                                        Matrix = gewichten_enkel.get(key)

                                        Dezegroeplijst = potenties(Matrix, Inwonerstransmatrix, gr, Groepen)
                                        for i in range(0, len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                        logger.debug('Bijhoudlijst niet fossiel is: %s', Bijhoudlijst)

                                elif mod == 'OV':
                                    String = utils.single_group (mod,gr)
                                    key = DataKey(f'{String}_vk',
                                                  part_of_day=ds,
                                                  preference=vk,
                                                  income=ink,
                                                  regime=regime,
                                                  motive=mot)
                                    Matrix = gewichten_enkel.get(key)

                                    Dezegroeplijst = potenties ( Matrix, Inwonerstransmatrix, gr, Groepen)
                                    for i in range(0, len(Matrix) ):
                                        Bijhoudlijst[i]+= round(Dezegroeplijst[i])
                                else:
                                    String = utils.combined_group(mod, gr)
                                    logger.debug('de gr is %s', gr)
                                    logger.debug('de string is %s', String)
                                    if String[0] == 'A':
                                        for srtbr in soortbrandstof:
                                            key = DataKey(f'{String}_vk',
                                                          part_of_day=ds,
                                                          preference=vk,
                                                          income=ink,
                                                          regime=regime,
                                                          motive=mot,
                                                          subtopic='combinaties',
                                                          fuel_kind=srtbr)
                                            Matrix = gewichten_combi.get(key)

                                            Dezegroeplijst1 = potenties(Matrix, Inwonerstransmatrix, gr, Groepen)

                                            if srtbr == 'elektrisch':
                                                K = percentageelektrisch.get(inkgr) / 100
                                                DezegroeplijstE = [x * K for x in Dezegroeplijst1]
                                            else:
                                                K = 1 - percentageelektrisch.get(inkgr) / 100
                                                DezegroeplijstF = [x * K for x in Dezegroeplijst1]
                                        for i in range(len(Matrix)):
                                            Dezegroeplijst[i] = DezegroeplijstE[i] + DezegroeplijstF[i]
                                        for i in range(0, len(Matrix)):
                                            Bijhoudlijst[i] += int(Dezegroeplijst[i])
                                    else:
                                        key = DataKey(f'{String}_vk',
                                                      part_of_day=ds,
                                                      preference=vk,
                                                      income=ink,
                                                      regime=regime,
                                                      motive=mot,
                                                      subtopic='combinaties')
                                        Matrix = gewichten_combi.get(key)

                                        Dezegroeplijst = potenties ( Matrix, Inwonerstransmatrix, gr, Groepen)
                                        for i in range ( 0, len ( Matrix ) ):
                                            Bijhoudlijst[i] += round ( Dezegroeplijst[i])

                        key = DataKey(id='Totaal',
                                      part_of_day=ds,
                                      group=abg,
                                      income=inkgr,
                                      motive=mot,
                                      modality=mod)
                        herkomsten.set(key, Bijhoudlijst)
                        Generaaltotaal_potenties.append(herkomsten.get(key))

                    key = DataKey(id='Pot_totaal',
                                  part_of_day=ds,
                                  group=abg,
                                  income=inkgr,
                                  motive=mot)

                    herkomsten_totaal = utils.transpose(Generaaltotaal_potenties)
                    herkomsten.write_csv(herkomsten_totaal, key, header=headstring)
                    herkomsten.write_xlsx(herkomsten_totaal, key, header=headstringExcel)

                header = ['Zone', 'laag', 'middellaag', 'middelhoog', 'hoog']
                for mod in modaliteiten:
                    Generaalmatrixproduct = []
                    Generaalmatrix = []
                    for inkgr in inkgroepen:
                        key = DataKey('Totaal',
                                      part_of_day=ds,
                                      income=inkgr,
                                      motive=mot,
                                      group=abg,
                                      modality=mod,
                                      subtopic='')
                        Totaalrij = herkomsten.get(key)

                        Generaalmatrix.append(Totaalrij)
                    Generaaltotaaltrans = utils.transpose(Generaalmatrix)
                    for i in range (len(Arbeidsplaatsenperklasse)):
                        Generaalmatrixproduct.append([])
                        for j in range (len(Arbeidsplaatsenperklasse[0])):
                            if Arbeidsplaatsenperklasse[i][j]>0:
                                Generaalmatrixproduct[i].append(int(Generaaltotaaltrans[i][j]*Arbeidsplaatsenperklasse[i][j]))
                            else:
                                Generaalmatrixproduct[i].append(0)

                    key = DataKey(id='Pot_totaal',
                                  part_of_day=ds,
                                  group=abg,
                                  motive=mot,
                                  modality=mod)
                    herkomsten.write_xlsx(Generaaltotaaltrans, key, header=header)

                    key = DataKey(id='Pot_totaalproduct',
                                  part_of_day=ds,
                                  group=abg,
                                  motive=mot,
                                  modality=mod)
                    herkomsten.write_xlsx(Generaalmatrixproduct, key, header=header)

    return herkomsten
