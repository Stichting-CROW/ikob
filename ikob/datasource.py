import Routines
import os
import pathlib


class DataSource:

    aantal_lege_regels = {
        'parkeerzoektijden_bestand': 1,
        'Inwoners_per_klasse': 1,
        'GeenRijbewijs': 1,
        'GeenAuto': 1,
        'WelAuto': 1,
        'Voorkeuren': 1,
        'VoorkeurenGeenAuto': 1,
        'verdelingovergroepen': 1,
        'Arbeidsplaatsen_inkomensklasse': 1,
        'Beroepsbevolking_inkomensklasse': 1,
        'Verdeling_over_groepen_alleen_autobezit': 1,
        'Verdeling_over_groepen': 1,
        'Verdeling_over_groepen_Beroepsbevolking': 1,
        'Verdeling_over_groepen_Leerlingen': 1,
        'Verdeling_over_groepen_Inwoners': 1,
        'Verdeling_over_groepen_Inwoners_alleen_autobezit': 1,
        'Verdeling_over_groepen_Leerlingen_alleen_autobezit': 1,
        'Verdeling_over_groepen_Beroepsbevolking_alleen_autobezit': 1,
    }

    def __init__(self, config, projectbestandsnaam=None):
        self.config = config
        self.skims_config = config['skims']

        paden_config = config['project']['paden']

        # SEGS
        self.segs_dir = pathlib.Path(paden_config['segs_directory'])

        # SKIMS
        self.basis_dir = pathlib.Path(paden_config['skims_directory'])
        self.skims_dir = self.basis_dir / 'skims'
        os.makedirs(self.skims_dir, exist_ok=True)

        # Files in project output folder:
        if projectbestandsnaam:
            self.project_dir = self.basis_dir / projectbestandsnaam
            os.makedirs(self.project_dir, exist_ok=True)
            self.ervarenreistijd_dir = 'Ervarenreistijd' # NOTES Jaardirectory == Ervarenreistijddirectory
            self.gewichten_dir = 'Gewichten' # Also called enkeldirectory
            self.combinatie_dir = f"{self.gewichten_dir}/Combinaties"

    def _write_csv_or_xlsx(self, data, path, header, xlsx_format):
        if xlsx_format:
            return Routines.xlswegschrijven(data, path, header)

        if header:
            return Routines.csvwegschrijvenmetheader(data, path, header)

        return Routines.csvwegschrijven(data, path, soort='lijst')

    def _add_id_suffix(self, id, vk, ink, mod=''):
        if vk != '':
            id += f'{vk}'
        if mod != '':
            id += f'_{mod}'
        if ink != '':
            id += f'_{ink}'
        return id

    def config_lezen(self, id: str, type_caster=float):
        """Expects an id that is present in the config dict. Then
        load the file specified by that dict."""
        csv_path = self.skims_config[id]
        if isinstance(csv_path, dict):
            csv_path = csv_path["bestand"]

        csv_path = pathlib.Path(csv_path).with_suffix('')
        return Routines.csvlezen(csv_path, self.aantal_lege_regels.get(id, 0), type_caster)

    def verdeling_lezen(self, id: str, type_caster=float):
        csv_path = self.config['verdeling'][id]
        if isinstance(csv_path, dict):
            csv_path = csv_path["bestand"]
        csv_path = pathlib.Path(csv_path).with_suffix('')
        return Routines.csvlezen(csv_path, self.aantal_lege_regels.get(id, 0), type_caster)
    """"""

    """Methods to write/read ervarenreistijd"""

    def maak_ervarenreistijd_pad(self, id, dagsoort, ink, hubnaam, regime, mot):
        if hubnaam != "":
            id += f"_{hubnaam}"
        if ink != '':
            id += f'_{ink}'

        path = self.project_dir / regime / mot / self.ervarenreistijd_dir / dagsoort
        os.makedirs(path, exist_ok=True)
        return path / id

    def ervarenreistijd_schrijven(self, data, id: str, dagsoort: str, ink="", hubnaam="", soort='matrix', regime='', mot=''):
        bestandspad = self.maak_ervarenreistijd_pad(id, dagsoort, ink, hubnaam, regime, mot)
        Routines.csvwegschrijven(data, bestandspad, soort)

    def ervarenreistijd_lezen(self, id, dagsoort, ink='', hubnaam="", type_caster=float, regime='', mot=''):
        bestandspad = self.maak_ervarenreistijd_pad(id, dagsoort, ink, hubnaam, regime, mot)
        return Routines.csvlezen(bestandspad, aantal_lege_regels=0, type_caster=type_caster)
    """"""

    """Methods to read SKIMS"""

    def skims_lezen(self, id: str, dagsoort: str, type_caster = float):
        """Expects a filename to read, which should be located in 
        in subfolder 'dagsoort' of the global path 'Jaarinvoerdirectory'
        """
        path = self.skims_dir / dagsoort / id
        return Routines.csvlezen(path, self.aantal_lege_regels.get(id, 0), type_caster=type_caster)
    """"""

    """Methods to write/read SEGS """

    def _schrijf_csv_met_header(self, data, pad, header):
        Routines.csvwegschrijvenmetheader(data, pad, header)

    def _segs_dir(self, id, jaar, scenario):
        id = id + jaar if jaar else id
        if scenario:
            return self.segs_dir / scenario / id
        else:
            return self.segs_dir / id

    def segs_schrijven(self, data, id, header, jaar="", scenario=""):
        path = self._segs_dir(id, jaar, scenario)
        self._schrijf_csv_met_header(data, path, header)

    def segs_xlsx_schrijven(self, data, id, header, jaar="", scenario=""):
        path = self._segs_dir(id, jaar, scenario)
        Routines.xlswegschrijven(data, path, header)

    def segs_lezen(self, id: str, jaar="", type_caster=int, scenario=""):
        aantal_lege_regels = self.aantal_lege_regels.get(id, 0)
        path = self._segs_dir(id, jaar, scenario)
        return Routines.csvlezen(path, aantal_lege_regels=aantal_lege_regels, type_caster=type_caster)
    """"""

    """Methods to write/read to main gewichtendirectory """

    def maak_bestandspad_gewichten(self, id, dagsoort, vk, ink, regime='', mot='', srtbr=''):
        id = self._add_id_suffix(id, vk, ink)
        path = self.project_dir / regime / mot / self.gewichten_dir / dagsoort / srtbr
        os.makedirs(path, exist_ok=True)
        return path / id

    def gewichten_schrijven(self, gewichten, id, dagsoort, vk='', ink='',regime='', mot='', srtbr=''):
        bestandspad = self.maak_bestandspad_gewichten(id, dagsoort, vk, ink, regime, mot, srtbr)
        Routines.csvwegschrijven(gewichten, bestandspad)

    def gewichten_lezen(self, id, dagsoort, vk='', ink='',regime='', mot='', srtbr=''):
        bestandspad = self.maak_bestandspad_gewichten(id, dagsoort, vk, ink, regime, mot, srtbr)
        return Routines.csvlezen(bestandspad)
    """"""

    """Methods to write/read weights to combinatiedirectory"""

    def maak_bestandspad_combinatiegewichten(self, id, dagsoort, vk, ink, srtbr='', regime='', mot=''):
        id = self._add_id_suffix(id, vk, ink)
        path = self.project_dir / regime / mot / self.combinatie_dir / dagsoort / srtbr
        os.makedirs(path, exist_ok=True)
        return path / id

    def combinatie_gewichten_schrijven(self, gewichten, id, dagsoort, vk='', ink='', srtbr='', regime='', mot=''):
        bestandspad = self.maak_bestandspad_combinatiegewichten(id, dagsoort, vk, ink, srtbr, regime=regime, mot=mot)
        Routines.csvwegschrijven(gewichten, bestandspad)

    def combinatie_gewichten_lezen(self, id, dagsoort, vk='', ink='', srtbr='', regime='', mot=''):
        bestandspad = self.maak_bestandspad_combinatiegewichten(id, dagsoort, vk, ink, srtbr, regime=regime, mot=mot)
        return Routines.csvlezen(bestandspad)
    """"""

    """Methods to write/read to totalendirectory"""
    def maak_bestandspad_totalen(self, id, dagsoort, mod, ink, mot, abg):
        id = self._add_id_suffix(id, vk='', ink=ink, mod=mod)
        path = self.project_dir / 'Resultaten' / mot / abg / 'Bestemmingen' / dagsoort
        os.makedirs(path, exist_ok=True)
        return path / id

    def totalen_schrijven(self, data, id, dagsoort, mod='', ink='', header=[], xlsx_format=False, mot='', abg=''):
        bestandspad = self.maak_bestandspad_totalen(id, dagsoort, mod, ink, mot, abg)
        return self._write_csv_or_xlsx(data, bestandspad, header, xlsx_format)

    def totalen_lezen(self, id, dagsoort, mod='', ink='', mot='', abg=''):
        bestandspad = self.maak_bestandspad_totalen(id, dagsoort, mod, ink, mot, abg)
        return Routines.csvintlezen(bestandspad)
    """"""


    """Methods to write/read to herkomstendirectory/Totalendirectoryherkomsten"""
    def maak_bestandspad_herkomst_totalen(self, id, dagsoort, mot, mod, ink):
        id = self._add_id_suffix(id, vk='', ink=ink, mod=mod)
        path = self.project_dir / 'Resultaten' / mot / 'Herkomsten' / dagsoort
        os.makedirs(path, exist_ok=True)
        return path / id

    def herkomst_totalen_schrijven(self, data, id, dagsoort, mot, mod='', ink='', header=[], xlsx_format=False):
        bestandspad = self.maak_bestandspad_herkomst_totalen(id, dagsoort, mot, mod, ink)
        return self._write_csv_or_xlsx(data, bestandspad, header, xlsx_format)

    def herkomst_totalen_lezen(self, id, dagsoort, mot, mod='', ink=''):
        bestandspad = self.maak_bestandspad_herkomst_totalen(id, dagsoort, mot, mod, ink)
        return Routines.csvintlezen(bestandspad)
    """"""

    """Methods to write/read to concurrentiedirectory/Totalendirectoryconcurrentie"""
    def maak_bestandspad_concurrentie_totalen(self, id, dagsoort, mot, mod, ink, kind):
        assert kind == "arbeidsplaatsen" or kind == "inwoners"
        id = self._add_id_suffix(id, vk='', ink=ink, mod=mod)
        path = self.project_dir / 'Resultaten' / mot / 'Concurrentie' / kind / dagsoort
        os.makedirs(path, exist_ok=True)
        return path / id

    def concurrentie_totalen_schrijven(self, data, id, dagsoort, kind, mot, mod='', ink='', header=[], xlsx_format=False):
        bestandspad = self.maak_bestandspad_concurrentie_totalen(id, dagsoort, mot, mod, ink, kind)
        return self._write_csv_or_xlsx(data, bestandspad, header, xlsx_format)

    def concurrentie_totalen_lezen(self, id, dagsoort, kind, mot, mod='', ink=''):
        bestandspad = self.maak_bestandspad_concurrentie_totalen(id, dagsoort, mot, mod, ink, kind)
        return Routines.csvlezen(bestandspad)
    """"""

    """Methods to write/read to bestemmingendirectory/Totalendirectorybestemmingen"""
    def maak_bestandspad_bestemmingen_totalen(self, id, dagsoort, mod, ink, mot, abg):
        id = self._add_id_suffix(id, vk='', ink=ink, mod=mod)
        path = self.project_dir / 'Resultaten' / mot / abg / 'Bestemmingen' / dagsoort
        os.makedirs(path, exist_ok=True)
        return path / id

    def bestemmingen_totalen_schrijven(self, data, id, dagsoort, mod='', ink='', header=[], xlsx_format=False):
        bestandspad = self.maak_bestandspad_bestemmingen_totalen(id, dagsoort, mod, ink)
        return self._write_csv_or_xlsx(data, bestandspad, header, xlsx_format)

    def bestemmingen_totalen_lezen(self, id, dagsoort, mod='', ink='', mot='', abg=''):
        bestandspad = self.maak_bestandspad_bestemmingen_totalen(id, dagsoort, mod, ink, mot, abg)
        return Routines.csvlezen(bestandspad)
    """"""
