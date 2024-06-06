import ikob.Routines as Routines
import logging
import os
import pathlib
from ikob.stedelijkheidsgraad_to_parkeerzoektijden import stedelijkheid_to_parkeerzoektijd

logger = logging.getLogger(__name__)


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
        # TODO: Improve handling of data directory structure:
        # - Extract paths/directory names from constants, e.g. Enum;
        # - Support multi-lingual directory names.
        self.tmp_dir = self.project_dir / 'Tussenresultaten'

    def _add_id_suffix(self, id, vk, mod, hubnaam, ink):
        id += vk
        for suffix in [mod, hubnaam, ink]:
            if suffix:
                id += f"_{suffix}"
        return id

    def _make_file_path(self, id, motief, topic, dagsoort, base, regime='', subtopic='', brandstof='', vk='', ink='', hubnaam='', mod=''):
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

        csv_path = pathlib.Path(csv_path)
        return Routines.csvlezen(csv_path, type_caster)

    def read_skims(self, id: str, dagsoort: str, type_caster = float):
        """Expects a filename to read, which should be located in 
        in subfolder 'dagsoort' of the global path 'Jaarinvoerdirectory'
        """
        path = (self.skims_dir / dagsoort / id).with_suffix(".csv")
        return Routines.csvlezen(path, type_caster=type_caster)

    def read_parkeerzoektijden(self):
        config_skims = self.config["skims"]

        parkeertijden_path = pathlib.Path(config_skims.get(
            "parkeerzoektijden_bestand",
            self.segs_dir / "Parkeerzoektijd.csv"
        ))

        if parkeertijden_path.exists():
            logging.info("Reading parkeerzoektijden: '%s'", parkeertijden_path)
            return Routines.csvintlezen(parkeertijden_path)

        stedelijkheid_path = self.segs_dir / "Stedelijkheidsgraad.csv"
        assert stedelijkheid_path.exists(), (
            "Missing both Parkeerzoektijden, Stedelijkheidsgraad files."
            "Parkeerzoektijden file cannot be generated."
        )

        msg = "Generating parkeerzoektijden from '%s'"
        logger.info(msg, stedelijkheid_path)
        stedelijkheidsgraad = Routines.csvintlezen(stedelijkheid_path)
        return stedelijkheid_to_parkeerzoektijd(stedelijkheidsgraad)

    def _segs_input_dir(self, id, jaar, scenario):
        return self._segs_dir(self.segs_dir, id, jaar, scenario)

    def _segs_output_dir(self, id, jaar, scenario, group="", modifier=""):
        root = self.tmp_dir / 'Groepenverdeling'
        return self._segs_dir(root, id, jaar, scenario, group, modifier)

    def _segs_dir(self, path, id, jaar, scenario, group="", modifier=""):
        filename = id + jaar

        for postfix in [group, modifier]:
            if postfix:
                filename += f"_{postfix}"

        path = path / scenario
        os.makedirs(path, exist_ok=True)
        return path / filename

    def write_segs_csv(self, data, id, header, group="", jaar="", modifier="", scenario=""):
        path = self._segs_output_dir(id, jaar, scenario, group, modifier).with_suffix(".csv")
        return Routines.csvwegschrijven(data, path, header=header)

    def write_segs_xlsx(self, data, id, header, group="", jaar="", modifier="", scenario=""):
        path = self._segs_output_dir(id, jaar, scenario, group, modifier).with_suffix(".xlsx")
        return Routines.xlswegschrijven(data, path, header)

    def read_segs(self, id: str, jaar="", type_caster=int, scenario=""):
        # TODO: This is a temporary fix. The 'Verdeling_over_groepen*'
        # files are written to disk as SEGS files. These were originally
        # written back into the _input_ directory and read out in later
        # stages of the program. This detects that behaviour and diverts
        # reading to the SEGS _output_ directory. Since this only happens
        # for one variable, the fix is introduced here. Once that data is
        # passed along as function arguments (kept in memory), this TODO
        # is to be resolved.
        should_read_from_output = 'Verdeling_over_groepen' in id

        if should_read_from_output:
            path = self._segs_output_dir(id, jaar, scenario)
        else:
            path = self._segs_input_dir(id, jaar, scenario)

        path = path.with_suffix(".csv")
        return Routines.csvlezen(path, type_caster=type_caster)

    def _get_base_dir(self, datatype, id):
        if datatype == "Concurrentie":
            return "Resultaten"
        if datatype == "Herkomsten":
            return "Resultaten"
        if "totaal" in id.lower():
            # Totaal, Ontpl_totaal, Ontpl_totaalproduct
            return "Resultaten"

        return ""

    def read_csv(self, datatype, id, dagsoort, regime='', subtopic='', vk='', ink='', hubnaam='', mot='', mod='', srtbr='', type_caster=float):
        base = self._get_base_dir(datatype, id)
        path = self._make_file_path(id, mot, datatype, dagsoort, base, mod=mod, regime=regime, subtopic=subtopic, brandstof=srtbr, vk=vk, ink=ink, hubnaam=hubnaam)
        path = path.with_suffix(".csv")
        return Routines.csvlezen(path, type_caster=type_caster)

    def write_csv(self, data, datatype, id, dagsoort, header=[], regime='', subtopic='', vk='', ink='', hubnaam='', mot='', mod='', srtbr=''):
        base = self._get_base_dir(datatype, id)
        path = self._make_file_path(id, mot, datatype, dagsoort, base, mod=mod, regime=regime, subtopic=subtopic, brandstof=srtbr, vk=vk, ink=ink, hubnaam=hubnaam)
        path = path.with_suffix(".csv")
        return Routines.csvwegschrijven(data, path, header=header)

    def write_xlsx(self, data, datatype, id, dagsoort, header=[], regime='', subtopic='', vk='', ink='', hubnaam='', mot='', mod='', srtbr=''):
        base = self._get_base_dir(datatype, id)
        path = self._make_file_path(id, mot, datatype, dagsoort, base, mod=mod, regime=regime, subtopic=subtopic, brandstof=srtbr, vk=vk, ink=ink, hubnaam=hubnaam)
        path = path.with_suffix(".xlsx")
        return Routines.xlswegschrijven(data, path, header)
