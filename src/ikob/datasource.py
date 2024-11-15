import enum
import logging
import os
import pathlib
from dataclasses import dataclass
from typing import Optional

from numpy.typing import NDArray

import ikob.utils as utils
from ikob.urbanisation_grade_to_parking_times import \
    urbanisation_grade_to_parking_times

logger = logging.getLogger(__name__)


def get_project_name(config) -> str:
    return config["__filename__"]


def get_project_directory(config) -> pathlib.Path:
    paths = config['project']['paden']
    output_dir = pathlib.Path(paths['output_directory'])
    return output_dir / get_project_name(config)


def get_temporary_directory(config) -> pathlib.Path:
    project_dir = get_project_directory(config)
    return project_dir / 'tussenresultaten'


def read_csv_from_config(config, key: str, id: str, type_caster=float):
    """Read key from id section in the configuration file."""
    csv_path = config[key][id]
    if isinstance(csv_path, dict):
        csv_path = csv_path["bestand"]

    csv_path = pathlib.Path(csv_path)
    return utils.read_csv(csv_path, type_caster)


def read_parking_times(config):
    """Read parkeerzoektijden from disk.

    When the parkeerzoektijden file is not present, it is attempted
    to generate the parkeerzoektijden from stedelijkheidsgraad.
    """

    config_skims = config["skims"]
    segs_dir = pathlib.Path(config['project']['paden']['segs_directory'])

    parking_time_path = pathlib.Path(config_skims.get(
        "parkeerzoektijden_bestand",
        segs_dir / "Parkeerzoektijd.csv"
    ))

    if parking_time_path.exists():
        logging.info("Reading parking times: '%s'", parking_time_path)
        return utils.read_csv_int(parking_time_path)

    urbanisation_path = segs_dir / "Stedelijkheidsgraad.csv"
    assert urbanisation_path.exists(), (
        "Missing both Parkeerzoektijden, Stedelijkheidsgraad files."
        "Parkeerzoektijden file cannot be generated."
    )

    msg = "Generating parking times from '%s'"
    logger.info(msg, urbanisation_path)
    urbanisation_grade = utils.read_csv_int(urbanisation_path)
    return urbanisation_grade_to_parking_times(urbanisation_grade)


class SkimsSource:
    """A data provider for skims files."""

    def __init__(self, skims_dir: pathlib.Path | str):
        self.skims_dir = pathlib.Path(skims_dir)

    def read(self, id: str, dagsoort: str, type_caster=float):
        """Read skims from disk.

        Reads the skim file formed by the identifier and dagsoort.
        The ``type_caster`` allows to cast the data to a desired type.
        """
        path = (self.skims_dir / dagsoort / id).with_suffix(".csv")
        return utils.read_csv(path, type_caster=type_caster)


class SegsSource:
    """A data provider for SEGS files."""

    def __init__(self, config):
        self.segs_dir = pathlib.Path(
            config['project']['paden']['segs_directory'])
        self.tmp_dir = get_temporary_directory(config)

    def _segs_input_dir(self, id, jaar, scenario):
        return self._segs_dir(self.segs_dir, id, jaar, scenario)

    def _segs_output_dir(self, id, jaar, scenario, group="", modifier=""):
        root = self.tmp_dir / 'groepenverdeling'
        return self._segs_dir(root, id, jaar, scenario, group, modifier)

    def _segs_dir(self, path, id, jaar, scenario, group="", modifier=""):
        filename = id + jaar

        for postfix in [group, modifier]:
            if postfix:
                filename += f"_{postfix}"

        path = path / scenario
        os.makedirs(path, exist_ok=True)
        return path / filename

    def read(self, id: str, jaar="", type_caster=int, scenario=""):
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
        return utils.read_csv(path, type_caster=type_caster)

    def write_csv(
            self,
            data,
            id,
            header,
            group="",
            jaar="",
            modifier="",
            scenario=""):
        path = self._segs_output_dir(
            id, jaar, scenario, group, modifier).with_suffix(".csv")
        return utils.write_csv(data, path, header=header)

    def write_xlsx(
            self,
            data,
            id,
            header,
            group="",
            jaar="",
            modifier="",
            scenario=""):
        path = self._segs_output_dir(
            id, jaar, scenario, group, modifier).with_suffix(".xlsx")
        return utils.write_xls(data, path, header)


class DataType(enum.Enum):
    DESTINATIONS = "bestemmingen"
    COMPETITION = "concurrentie"
    GENERALISED_TRAVEL_TIME = "ervarenreistijd"
    WEIGHTS = "gewichten"
    ORIGINS = "herkomsten"
    POTENCY = "potenties"


@dataclass(eq=True, frozen=True)
class DataKey:
    """A collection of strings to identify data from the DataSource.

    A DataKey instance is constructed with a subset of the required
    strings and can be passed towards the DataSource to read/write
    the desired data.
    """
    id: str
    part_of_day: str
    regime: Optional[str] = ""
    subtopic: Optional[str] = ""
    preference: Optional[str] = ""
    income: Optional[str] = ""
    hub_name: Optional[str] = ""
    motive: Optional[str] = ""
    group: Optional[str] = ""
    modality: Optional[str] = ""
    fuel_kind: Optional[str] = ""


class DataSource:
    def __init__(self, config, datatype: DataType):
        self.config = config
        self.project_dir = get_project_directory(config)
        self.cache: dict[DataKey, NDArray] = {}
        self.datatype = datatype

        # TODO: Improve handling of data directory structure:
        # - Extract paths/directory names from constants, e.g. Enum;
        # - Support multi-lingual directory names.

    def _add_id_suffix(self, key: DataKey) -> str:
        id = key.id + key.preference
        for suffix in [key.modality, key.hub_name, key.income]:
            if suffix:
                id += f"_{suffix}"
        return id

    def _make_file_path(self, key: DataKey) -> pathlib.Path:
        base = self._get_base_dir(key)
        id_with_suffix = self._add_id_suffix(key)
        dagsoort = key.part_of_day.lower()
        regime = key.regime.lower()
        path = self.project_dir / base / regime / key.motive / key.group / \
            self.datatype.value / key.subtopic / dagsoort / key.fuel_kind
        os.makedirs(path, exist_ok=True)
        return path / id_with_suffix

    def _get_base_dir(self, key: DataKey) -> str:
        if self.datatype in [DataType.COMPETITION, DataType.ORIGINS]:
            return "resultaten"
        if "totaal" in key.id.lower():
            # Totaal, Ontpl_totaal, Ontpl_totaalproduct
            return "resultaten"
        return ""

    def set(self, key: DataKey, data: NDArray):
        self.cache[key] = data

    def get(self, key: DataKey) -> NDArray:
        if key in self.cache:
            return self.cache[key]

        data = self.read_csv(key)
        self.set(key, data)
        return data

    def store(self):
        for key, data in self.cache.items():
            self.write_csv(data, key)

    def read_csv(self, key: DataKey) -> NDArray:
        path = self._make_file_path(key).with_suffix(".csv")
        return utils.read_csv(path)

    def write_csv(self, data, key: DataKey, header=[]):
        assert isinstance(key, DataKey)
        path = self._make_file_path(key).with_suffix(".csv")
        return utils.write_csv(data, path, header=header)

    def write_xlsx(self, data, key: DataKey, header=[], with_rounding=False):
        path = self._make_file_path(key).with_suffix(".xlsx")
        return utils.write_xls(data, path, header, with_rounding)
