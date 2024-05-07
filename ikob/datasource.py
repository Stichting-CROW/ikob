import Routines
import os


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
        'Verdeling_over_groepen': 1
    }

    def __init__(self, config, Projectbestandsnaam=None):
        self.config = config
        self.skims_config = config['skims']

        paden_config = config['project']['paden']
        # SEGS
        self.SEGSdirectory = paden_config['segs_directory']

        # SKIMS
        self.Basisdirectory = paden_config['skims_directory']
        Skimsdirectory = os.path.join(self.Basisdirectory, 'skims')
        os.makedirs(Skimsdirectory, exist_ok=True)
        self.Jaarinvoerdirectory = os.path.join(Skimsdirectory)  # ???

        # Files in project output folder:
        if Projectbestandsnaam:
            self.Projectdirectory = os.path.join(
                self.Basisdirectory, Projectbestandsnaam)
            os.makedirs(self.Projectdirectory, exist_ok=True)

            self.Ervarenreistijddirectory = 'Ervarenreistijd' # NOTES Jaardirectory == Ervarenreistijddirectory
            self.Gewichtendirectory = 'Gewichten' # Also called enkeldirectory
            self.Combinatiedirectory = os.path.join(self.Gewichtendirectory, "Combinaties")

    def _add_id_suffix(self, id, vk, ink, mod=''):
        if vk != '':
            id += f'{vk}'
        if mod != '':
            id += f'_{mod}'
        if ink != '':
            id += f'_{ink}'
        return id

    """Methods to read two files as specified in config directory."""

    def _csvlezen_type(self, csv_bestand, aantal_lege_regels, type):
        if type == "float":
            return Routines.csvfloatlezen(csv_bestand, aantal_lege_regels)
        if type == "int":
            return Routines.csvintlezen(csv_bestand, aantal_lege_regels)

    def config_lezen(self, id: str, cijfer_type: str = 'float'):
        """Expects an id that is present in the config dict. Then
        load the file specified by that dict."""
        csv_pad = self.skims_config[id]
        if type(csv_pad) == dict:
            csv_pad = csv_pad["bestand"]
        csv_pad = csv_pad.replace('.csv', '')
        return self._csvlezen_type(csv_pad, self.aantal_lege_regels.get(id, 0), cijfer_type)

    def verdeling_lezen(self, id: str, cijfer_type: str = 'float'):
        csv_pad = self.config['verdeling'][id]
        if type(csv_pad) == dict:
            csv_pad = csv_pad["bestand"]
        csv_pad = csv_pad.replace('.csv', '')
        return self._csvlezen_type(csv_pad, self.aantal_lege_regels.get(id, 0), cijfer_type)
    """"""

    """Methods to write/read ervarenreistijd"""

    def maak_ervarenreistijd_pad(self, id, dagsoort, ink, hubnaam, regime, mot):
        if hubnaam != "":
            id += f"_{hubnaam}"
        if ink != '':
            id += f'_{ink}'
        pad = os.path.join(self.Projectdirectory, regime, mot, self.Ervarenreistijddirectory, dagsoort)
        os.makedirs(pad, exist_ok=True)
        bestandspad = os.path.join(pad, id)
        return bestandspad

    def ervarenreistijd_schrijven(self, data, id: str, dagsoort: str, ink="", hubnaam="", soort='matrix', regime='', mot=''):
        bestandspad = self.maak_ervarenreistijd_pad(id, dagsoort, ink, hubnaam, regime, mot)
        Routines.csvwegschrijven(data, bestandspad, soort)

    def ervarenreistijd_lezen(self, id, dagsoort, ink='', hubnaam="", cijfer_type='float', regime='', mot=''):
        bestandspad = self.maak_ervarenreistijd_pad(id, dagsoort, ink, hubnaam, regime, mot)
        return self._csvlezen_type(bestandspad, aantal_lege_regels=0, type=cijfer_type)
    """"""

    """Methods to read SKIMS"""

    def skims_lezen(self, id: str, dagsoort: str, cijfer_type: str = 'float'):
        """Expects a filename to read, which should be located in 
        in subfolder 'dagsoort' of the global path 'Jaarinvoerdirectory'
        """
        pad = os.path.join(self.Jaarinvoerdirectory, dagsoort)
        bestandspad = os.path.join(pad, id)
        return self._csvlezen_type(bestandspad, self.aantal_lege_regels.get(id, 0), cijfer_type)
    """"""

    """Methods to write/read SEGS """

    def _schrijf_csv_met_header(self, data, pad, header):
        Routines.csvwegschrijvenmetheader(data, pad, header)

    def segs_schrijven(self, data, id, header, jaar="", scenario=""):
        if jaar != "":
            id += jaar
        if scenario == "":
            bestandspad = os.path.join(self.SEGSdirectory, id)
        else:
            bestandspad = os.path.join(self.SEGSdirectory, scenario, id)
        self._schrijf_csv_met_header(data, bestandspad, header)

    def segs_xlsx_schrijven(self, data, id, header, jaar="", scenario=""):
        if jaar != "":
            id += jaar
        if scenario == "":
            bestandspad = os.path.join(self.SEGSdirectory, id)
        else:
            bestandspad = os.path.join(self.SEGSdirectory, scenario, id)
        Routines.xlswegschrijven(data, bestandspad, header)

    def segs_lezen(self, id: str, jaar="", cijfer_type: str = 'int', scenario=""):
        aantal_lege_regels = self.aantal_lege_regels.get(id, 0)
        if jaar != "":
            id += jaar
        if scenario == "":
            bestandspad = os.path.join(self.SEGSdirectory, id)
        else:
            bestandspad = os.path.join(self.SEGSdirectory, scenario, id)
        if cijfer_type == 'int':
            return Routines.csvintlezen(bestandspad, aantal_lege_regels=aantal_lege_regels)
        elif cijfer_type == 'float':
            return Routines.csvfloatlezen(bestandspad, aantal_lege_regels=aantal_lege_regels)
        else:
            raise Exception("Onjuist cijfer-type gespecificeerd!")
    """"""

    """Methods to write/read to main gewichtendirectory """

    def maak_bestandspad_gewichten(self, id, dagsoort, vk, ink, regime='', mot='', srtbr=''):
        id = self._add_id_suffix(id, vk, ink)
        pad = os.path.join(self.Projectdirectory, regime, mot, self.Gewichtendirectory, dagsoort, srtbr)
        os.makedirs(pad, exist_ok=True)
        return os.path.join(pad, id)

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
        pad = os.path.join(self.Projectdirectory, regime, mot, self.Combinatiedirectory, dagsoort, srtbr)
        os.makedirs(pad, exist_ok=True)
        return os.path.join(pad, id)

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
        pad = os.path.join(self.Projectdirectory, 'Resultaten', mot, abg, 'Bestemmingen', dagsoort)
        os.makedirs(pad, exist_ok=True)
        return os.path.join(pad, id)

    def totalen_schrijven(self, data, id, dagsoort, mod='', ink='', write_header=False, header=[], xlsx_format=False, mot='', abg=''):
        bestandspad = self.maak_bestandspad_totalen(id, dagsoort, mod, ink, mot, abg)
        if xlsx_format:
            Routines.xlswegschrijven(data, bestandspad, header)
        else:
            if not write_header:
                Routines.csvwegschrijven(data, bestandspad, soort='lijst')
            else:
                Routines.csvwegschrijvenmetheader(data, bestandspad, header)

    def totalen_lezen(self, id, dagsoort, mod='', ink='', mot='', abg=''):
        bestandspad = self.maak_bestandspad_totalen(id, dagsoort, mod, ink, mot, abg)
        return Routines.csvintlezen(bestandspad)
    """"""


    """Methods to write/read to herkomstendirectory/Totalendirectoryherkomsten"""
    def maak_bestandspad_herkomst_totalen(self, id, dagsoort, mod, ink):
        id = self._add_id_suffix(id, vk='', ink=ink, mod=mod)
        pad = os.path.join(self.Projectdirectory, 'Resultaten', 'Herkomsten', dagsoort)
        os.makedirs(pad, exist_ok=True)
        return os.path.join(pad, id)

    def herkomst_totalen_schrijven(self, data, id, dagsoort, mod='', ink='', write_header=False, header=[], xlsx_format=False):
        bestandspad = self.maak_bestandspad_herkomst_totalen(id, dagsoort, mod, ink)
        if xlsx_format:
            Routines.xlswegschrijven(data, bestandspad, header)
        else:
            if not write_header:
                Routines.csvwegschrijven(data, bestandspad, soort='lijst')
            else:
                Routines.csvwegschrijvenmetheader(data, bestandspad, header)

    def herkomst_totalen_lezen(self, id, dagsoort, mod='', ink=''):
        bestandspad = self.maak_bestandspad_herkomst_totalen(id, dagsoort, mod, ink)
        return Routines.csvintlezen(bestandspad)
    """"""
