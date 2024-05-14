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

    def __init__(self, config, project_name):
        self.config = config
        paden = self.config['project']['paden']
        self.segs_dir = pathlib.Path(paden['segs_directory'])
        self.skims_dir = pathlib.Path(paden['skims_directory'])
        self.output_dir = pathlib.Path(paden['output_directory'])
        self.project_dir = self.output_dir / project_name
        # TODO: This should be based on 'beprijzingsregime'
        self.basis_dir = self.skims_dir.parent

    def _add_id_suffix(self, id, vk, mod, hubnaam, ink):
        id += vk
        for suffix in [mod, hubnaam, ink]:
            if suffix:
                id += f"_{suffix}"
        return id

    def _make_file_path(self, id, motief, topic, dagsoort, regime='', subtopic='', brandstof='', base='', vk='', ink='', hubnaam='', mod=''):
        id_with_suffix = self._add_id_suffix(id, vk, mod, hubnaam, ink)
        path = self.project_dir / base / regime / motief / topic / subtopic / dagsoort / brandstof
        os.makedirs(path, exist_ok=True)
        return path / id_with_suffix

    def read_config(self, key: str, id: str, type_caster=float):
        """Expects an id that is present in the config dict. Then
        load the file specified by that dict."""
        csv_path = self.config[key][id]
        if isinstance(csv_path, dict):
            csv_path = csv_path["bestand"]

        csv_path = pathlib.Path(csv_path).with_suffix('')
        return Routines.csvlezen(csv_path, self.aantal_lege_regels.get(id, 0), type_caster)

    def read_skims(self, id: str, dagsoort: str, type_caster = float):
        """Expects a filename to read, which should be located in 
        in subfolder 'dagsoort' of the global path 'Jaarinvoerdirectory'
        """
        path = self.skims_dir / dagsoort / id
        return Routines.csvlezen(path, self.aantal_lege_regels.get(id, 0), type_caster=type_caster)

    def _segs_dir(self, id, jaar, scenario):
        return self.segs_dir / scenario / (id + jaar)

    def write_segs_csv(self, data, id, header, jaar="", scenario=""):
        path = self._segs_dir(id, jaar, scenario)
        return Routines.csvwegschrijven(data, path, header=header)

    def write_segs_xlsx(self, data, id, header, jaar="", scenario=""):
        path = self._segs_dir(id, jaar, scenario)
        return Routines.xlswegschrijven(data, path, header)

    def read_segs(self, id: str, jaar="", type_caster=int, scenario=""):
        aantal_lege_regels = self.aantal_lege_regels.get(id, 0)
        path = self._segs_dir(id, jaar, scenario)
        return Routines.csvlezen(path, aantal_lege_regels=aantal_lege_regels, type_caster=type_caster)

    def read_csv(self, datatype, id, dagsoort, base='', regime='', subtopic='', vk='', ink='', hubnaam='', mot='', mod='', srtbr='', type_caster=float):
        bestandspad = self._make_file_path(id, mot, datatype, dagsoort, mod=mod, base=base, regime=regime, subtopic=subtopic, brandstof=srtbr, vk=vk, ink=ink, hubnaam=hubnaam)
        return Routines.csvlezen(bestandspad, type_caster=type_caster)

    def write_csv(self, data, datatype, id, dagsoort, header=None, soort='', base='', regime='', subtopic='', vk='', ink='', hubnaam='', mot='', mod='', srtbr=''):
        bestandspad = self._make_file_path(id, mot, datatype, dagsoort, mod=mod, base=base, regime=regime, subtopic=subtopic, brandstof=srtbr, vk=vk, ink=ink, hubnaam=hubnaam)
        return Routines.csvwegschrijven(data, bestandspad, header=header, soort=soort)

    def write_xlsx(self, data, datatype, id, dagsoort, header=None, soort='', base='', regime='', subtopic='', vk='', ink='', hubnaam='', mot='', mod='', srtbr=''):
        bestandspad = self._make_file_path(id, mot, datatype, dagsoort, mod=mod, base=base, regime=regime, subtopic=subtopic, brandstof=srtbr, vk=vk, ink=ink, hubnaam=hubnaam)
        return Routines.xlswegschrijven(data, bestandspad, header)
