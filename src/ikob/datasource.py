import enum
import logging
import os
import pathlib
import shutil
from dataclasses import dataclass, field
from typing import Type

import numpy.typing as npt
from numpy.typing import NDArray

import ikob.utils as utils
from ikob.urbanization_grade_to_parking_times import urbanization_grade_to_parking_times

logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    pass


def get_project_name(config) -> str:
    return config["__filename__"]


def get_project_directory(config) -> pathlib.Path:
    paths = config["project"]["paden"]
    output_dir = pathlib.Path(paths["output_directory"])
    return output_dir / get_project_name(config)


def get_temporary_directory(config) -> pathlib.Path:
    project_dir = get_project_directory(config)
    return project_dir / "tussenresultaten"


def read_csv_from_config(config, key: str, id: str, type_caster=float):
    """Read key from id section in the configuration file."""
    csv_path = config[key][id]
    if isinstance(csv_path, dict):
        csv_path = csv_path["bestand"]

    if csv_path == "":
        raise DataSourceError(
            f"Problem occurred while reading path from config with key: '{key}' and id '{id}'. Path is empty"
        )

    csv_path = pathlib.Path(csv_path)
    try:
        return utils.read_csv(csv_path, type_caster)
    except Exception:
        raise DataSourceError(
            f"Problem occurred while reading path from config with key: '{key}' and id '{id}'. Path is '{csv_path}'"
        )


def read_parking_times(config):
    """Read parkeerzoektijden from disk.

    When the parkeerzoektijden file is not present, it is attempted
    to generate the parkeerzoektijden from stedelijkheidsgraad.
    """

    config_skims = config["skims"]
    segs_dir = pathlib.Path(config["project"]["paden"]["segs_directory"])

    parking_time_path = pathlib.Path(config_skims.get("parkeerzoektijden_bestand", segs_dir / "Parkeerzoektijd.csv"))

    if parking_time_path.exists():
        logging.info("Reading parking times from: '%s'", parking_time_path)
        return utils.read_csv_int(parking_time_path)

    urbanization_path = segs_dir / "Stedelijkheidsgraad.csv"
    assert urbanization_path.exists(), (
        "Missing both Parkeerzoektijden, Stedelijkheidsgraad files.Parkeerzoektijden file cannot be generated."
    )

    msg = "Generating parking times from '%s'"
    logger.info(msg, urbanization_path)
    urbanization_grade = utils.read_csv_int(urbanization_path)
    return urbanization_grade_to_parking_times(urbanization_grade)


class SkimsSource:
    """A data provider for skims files."""

    def __init__(self, skims_dir: pathlib.Path | str):
        if skims_dir == "":
            raise DataSourceError("Skims source initialized with empty skims dir")
        self.skims_dir = pathlib.Path(skims_dir)

    def read(
        self, id: str, dagdeel: str, type_caster=float, default: npt.NDArray | None = None, has_index_column=False
    ) -> npt.NDArray:
        """Read skims from disk.

        Reads the skim file formed by the identifier and dagdeel.
        The ``type_caster`` allows to cast the data to a desired type.
        """
        path = (self.skims_dir / dagdeel / id).with_suffix(".csv")
        if os.path.exists(path):
            return utils.read_csv(path, type_caster=type_caster, has_index_column=has_index_column)
        if default is None:
            raise FileNotFoundError(f"Skim file {path} not found, with no default.")
        logger.warning(f"Skim file {path} not found, using default.")
        return default


class SegsSource:
    """A data provider for SEGS files."""

    def __init__(self, config):
        self.segs_dir = pathlib.Path(config["project"]["paden"]["segs_directory"])
        if self.segs_dir == "":
            raise DataSourceError("Skims source initialized with empty skims dir")
        self.tmp_dir = get_temporary_directory(config)

    def _segs_input_dir(self, id, jaar, scenario):
        return self._segs_dir(self.segs_dir, id, jaar, scenario)

    def _segs_output_dir(self, id, jaar, scenario, group="", modifier=""):
        root = self.tmp_dir / "groepenverdeling"
        return self._segs_dir(root, id, jaar, scenario, group, modifier)

    def _segs_dir(self, path, id, jaar, scenario, group="", modifier=""):
        filename = id + jaar

        for postfix in [group, modifier]:
            if postfix:
                filename += f"_{postfix}"

        path = path / scenario
        os.makedirs(path, exist_ok=True)
        return path / filename

    def read(
        self, id: str, jaar="", type_caster: Type = int, scenario="", group="", modifier="", has_index_column=False
    ):
        # TODO: This is a temporary fix. The 'Verdeling_over_groepen*'
        # files are written to disk as SEGS files. These were originally
        # written back into the _input_ directory and read out in later
        # stages of the program. This detects that behavior and diverts
        # reading to the SEGS _output_ directory. Since this only happens
        # for one variable, the fix is introduced here. Once that data is
        # passed along as function arguments (kept in memory), this TODO
        # is to be resolved.
        should_read_from_output = "Verdeling_over_groepen" in id

        if should_read_from_output:
            path = self._segs_output_dir(id=id, jaar=jaar, scenario=scenario, group=group, modifier=modifier)
        else:
            path = self._segs_input_dir(id, jaar, scenario)

        path = path.with_suffix(".csv")
        try:
            return utils.read_csv(path, type_caster=type_caster, has_index_column=has_index_column)
        except FileNotFoundError:
            raise DataSourceError(
                f"File SEGS file '{path}' not found. Is the scenario (used as subfolder) '{scenario}' correct?"
            )

    def write_csv(
        self, data, id, header, group="", jaar="", modifier="", scenario="", index: utils.CsvIndex = utils.CsvIndex()
    ):
        path = self._segs_output_dir(id, jaar, scenario, group, modifier).with_suffix(".csv")
        return utils.write_csv(data, path, header=header, index=index)


class DataType(enum.Enum):
    DESTINATIONS = "bestemmingen"
    COMPETITION = "concurrentie"
    GENERALIZED_TRAVEL_TIME = "ervarenreistijd"
    WEIGHTS = "gewichten"
    ORIGINS = "inwoners"
    POTENCY = "potenties"


@dataclass(eq=True, frozen=True)
class DataKey:
    """A collection of strings to identify data from the DataSource.

    A DataKey instance is constructed with a subset of the required
    strings and can be passed towards the DataSource to read/write
    the desired data.

    The header and index fields are used only when writing data and are used to add semantic information to the data written

    The temporary field is to indicate that the data stored at this key is not meant to be persisted and only used to store a temporary result for further computation.
    """

    id: str
    part_of_day: str
    regime: str = ""
    subtopic: str = ""
    preference: str = ""
    income: str = ""
    hub_name: str = ""
    motive: str = ""
    group: str = ""
    modality: str = ""
    fuel_kind: str = ""

    header: list[str] = field(default_factory=list, compare=False)
    index: utils.CsvIndex = field(default_factory=utils.CsvIndex, compare=False)

    is_temporary: bool = field(default=False, compare=False)

    @staticmethod
    def zone_header(num_zones):
        return ["zone_" + str(i + 1) for i in range(num_zones)]

    @staticmethod
    def zone_index(num_zones):
        return utils.CsvIndex.zone_index(num_zones)


class DataSource:
    OUTPUT_PATH = "OUTPUT.md"

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
        dagdeel = key.part_of_day.lower()
        regime = key.regime.lower()
        path = (
            self.project_dir
            / base
            / regime
            / key.motive
            / key.group
            / self.datatype.value
            / key.subtopic
            / dagdeel
            / key.fuel_kind
        )
        os.makedirs(path, exist_ok=True)
        return path / id_with_suffix

    def _get_base_dir(self, key: DataKey) -> str:
        if self.datatype in [DataType.COMPETITION, DataType.ORIGINS]:
            return "resultaten"
        # This is fickle. In practice the whole DataType.DESTINATIONS is also sent to the results dir
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
        logger.info("Writing output for data: %s.", self.datatype.value)
        for key, data in self.cache.items():
            self.write_csv(data, key)

    def read_csv(self, key: DataKey) -> NDArray:
        path = self._make_file_path(key).with_suffix(".csv")
        return utils.read_csv(path)

    def write_csv(self, data, key: DataKey, header=[]):
        assert isinstance(key, DataKey)
        if key.is_temporary:
            return
        path = self._make_file_path(key).with_suffix(".csv")
        if not header:
            header = key.header
        utils.write_csv(data, path, header=header, index=key.index)

    @staticmethod
    def write_output_md(config):
        path = get_project_directory(config) / DataSource.OUTPUT_PATH
        shutil.copy(DataSource.OUTPUT_PATH, path)
