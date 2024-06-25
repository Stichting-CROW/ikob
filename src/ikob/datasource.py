import ikob.Routines as Routines
import os
import pathlib
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class DataKey:
    """A collection of strings to identify data.

    TODO: Consider replacing strings with limited sets
          of variants with explicit enumerate types.
    """
    datatype: str
    id: str
    dagsoort: str = ""
    regime: str = ""
    subtopic: str = ""
    voorkeur: str = ""
    inkomen: str = ""
    hubnaam: str = ""
    motief: str = ""
    modaliteit: str = ""
    brandstof: str = ""


class DataSource:
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

    def _make_file_path(self, key: DataKey) -> pathlib.Path:
        base = self._get_base_dir(key.datatype, key.id)
        id_with_suffix = self._add_id_suffix(key.id, key.voorkeur, key.modaliteit, key.hubnaam, key.inkomen)
        path = self.project_dir / base / key.regime / key.motief / key.datatype / key.subtopic / key.dagsoort / key.brandstof
        os.makedirs(path, exist_ok=True)
        return path / id_with_suffix

    def read_config(self, key: str, id: str, type_caster=float):
        """Expects an id that is present in the config dict. Then
        load the file specified by that dict."""
        csv_path = self.config[key][id]
        if isinstance(csv_path, dict):
            csv_path = csv_path["bestand"]

        csv_path = pathlib.Path(csv_path)
        return Routines.csvlezen(csv_path, type_caster)

    def read_skims(self, id: str, dagsoort: str, type_caster = float):
        """Expects a filename to read, which should be located in 
        in subfolder 'dagsoort' of the global path 'Jaarinvoerdirectory'
        """
        path = (self.skims_dir / dagsoort / id).with_suffix(".csv")
        return Routines.csvlezen(path, type_caster=type_caster)

    def _segs_dir(self, id, jaar, scenario):
        return self.segs_dir / scenario / (id + jaar)

    def write_segs_csv(self, data, id, header, jaar="", scenario=""):
        path = self._segs_dir(id, jaar, scenario).with_suffix(".csv")
        return Routines.csvwegschrijven(data, path, header=header)

    def write_segs_xlsx(self, data, id, header, jaar="", scenario=""):
        path = self._segs_dir(id, jaar, scenario).with_suffix(".xlsx")
        return Routines.xlswegschrijven(data, path, header)

    def read_segs(self, id: str, jaar="", type_caster=int, scenario=""):
        path = self._segs_dir(id, jaar, scenario).with_suffix(".csv")
        return Routines.csvlezen(path, type_caster=type_caster)

    def _get_base_dir(self, datatype, id) -> str:
        if datatype == "Concurrentie":
            return "Resultaten"
        if datatype == "Herkomsten":
            return "Resultaten"
        if "totaal" in id.lower():
            # Totaal, Ontpl_totaal, Ontpl_totaalproduct
            return "Resultaten"

        return ""

    def read_csv(self, key: DataKey, type_caster=float):
        path = self._make_file_path(key)
        path = path.with_suffix(".csv")
        return Routines.csvlezen(path, type_caster=type_caster)

    def write_csv(self, data, key: DataKey, header=[]):
        path = self._make_file_path(key)
        path = path.with_suffix(".csv")
        return Routines.csvwegschrijven(data, path, header=header)

    def write_xlsx(self, data, key: DataKey, header=[]):
        path = self._make_file_path(key)
        path = path.with_suffix(".xlsx")
        return Routines.xlswegschrijven(data, path, header)
