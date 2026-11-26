import logging
from pathlib import Path
from typing import NamedTuple

from ikob import utils
from ikob.datasource import SegsSource, SkimsSource, configured_csv_path
from ikob.id_store import IdStore, ZoneIdStoreSingleton

logger = logging.getLogger(__name__)


class ZoneIdInputFile(NamedTuple):
    path: Path
    has_id_header: bool
    optional: bool = False


def _zone_id_input_files(config) -> list[ZoneIdInputFile]:
    project = config["project"]
    skims_reader = SkimsSource(config)
    segs_reader = SegsSource(config)
    skims = config["skims"]
    advanced = config["geavanceerd"]
    input_files: list[ZoneIdInputFile] = []

    skim_ids = ["Auto_Tijd", "Auto_Afstand", "Fiets_Tijd", "Fiets_Afstand", "OV_Tijd"]
    skim_ids.append("OV_Kosten" if skims["OV kostenbestand"]["gebruiken"] else "OV_Afstand")
    for part_of_day in skims["dagsoort"]:
        input_files.extend(
            ZoneIdInputFile(skims_reader.path_for(skim_id, part_of_day), True, optional=skim_id == "Fiets_Afstand")
            for skim_id in skim_ids
        )

    input_files.extend(
        ZoneIdInputFile(segs_reader.segs_input_path(filename), False)
        for filename in ("CBS_autos_per_huishouden", "Stedelijkheidsgraad")
    )
    scenario = project["verstedelijkingsscenario"]
    motive = project["motief"]
    input_files.extend(
        ZoneIdInputFile(segs_reader.segs_input_path(Path(motive[key]).name, scenario=scenario), False)
        for key in ("reizende populatie", "bestemmingsplaatsen")
    )
    input_files.append(ZoneIdInputFile(SkimsSource.parking_times_path(config), False, optional=True))

    for key in ("kunstmab", "parkeerkosten", "additionele_kosten"):
        if not advanced[key]["gebruiken"]:
            continue
        configured_path = configured_csv_path(config, "geavanceerd", key)
        if configured_path is None:
            raise ValueError(f"Enabled input geavanceerd. {key} has an empty file path.")

        has_id_header = key == "additionele_kosten"
        input_files.append(ZoneIdInputFile(configured_path, has_id_header=has_id_header))

    return input_files


def initialize_zone_id_store(config, allow_extra_zone_ids: bool = True) -> bool:
    """Install the common zone mapping, returning False with a warning if discovery fails.

    Returns whether the id store initialization was successful. A failure is only an error when we are trying to run ikob right now.
    An error can be thrown based on the return value of this method.
    When loading / saving config a warning is sufficient.
    """
    logger.info("Scanning zone id's used in project..")
    common_ids: set[str] | None = None
    zone_id_order: list[str] = []

    try:
        input_files = _zone_id_input_files(config)
    except (OSError, ValueError) as error:
        logger.warning("Unable to determine zone ID input files.", exc_info=error)
        return False

    for input_file in input_files:
        try:
            if input_file.optional and not input_file.path.exists():
                continue
            row_ids, header_ids = utils.read_zone_ids(input_file.path, has_id_header=input_file.has_id_header)
        except (OSError, ValueError) as error:
            logger.warning("Unable to read zone IDs from %s.", input_file.path, exc_info=error)
            return False
        if common_ids is None:
            common_ids = set(row_ids)
            # dict.fromkeys gets a deduplicated list with the same ordering as row_ids
            zone_id_order = list(dict.fromkeys(row_ids))
        else:
            common_ids.intersection_update(row_ids)
        if header_ids is not None:
            common_ids.intersection_update(header_ids)

    if not common_ids:
        logger.warning("Unable to initialize the zone ID store: no common zone IDs were found.")
        return False

    store = IdStore.from_zone_ids(
        [zone_id for zone_id in zone_id_order if zone_id in common_ids],
        zone_source="intersection of full-zone input files",
        allow_extra_ids=allow_extra_zone_ids,
    )
    ZoneIdStoreSingleton.set_instance(store)

    logger.info("Done.")
    return True
