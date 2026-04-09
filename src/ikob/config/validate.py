### Validate the template

import logging
from pathlib import Path

import numpy as np

from ikob import utils
from ikob.chain_generator import Hubs
from ikob.configuration_definition import default_config, default_configuration_definition
from ikob.datasource import SegsSource, SkimsSource, read_csv_from_config, read_parking_times

logger = logging.getLogger(__name__)


class FileValidator:
    def __init__(self, config):
        self.config = config

    def validate_input_files(self):
        logger.info("validating input files")
        num_zones, valid = self._skims_files_validation()
        if valid:
            valid &= self._motive_files_validation(num_zones)
            valid &= self._chain_files_validation(num_zones)

        if not valid:
            # This is only an error when we are trying to run ikob right now when loading / saving config a warning is good.
            logger.warning(
                "Unable to run ikob with the current config + input directory.",
            )
        return valid

    def _chain_files_validation(self, num_zones):
        valid = True
        if self.config["ketens"]["chains"]["gebruiken"]:
            try:
                hubs_raw = read_csv_from_config(self.config, key="ketens", id="chains", has_index_column=False)

            except Exception as e:
                logger.warning("A problem occurred while attempting to load the hub file: \n", exc_info=e)
                return False

            if not Hubs.validate(hubs_raw):
                logger.warning("A problem occurred while validating hub data")
                valid = False

        if self.config["ketens"]["bestemmingslijst"]["gebruiken"]:
            try:
                destination_list = read_csv_from_config(
                    self.config, key="ketens", id="bestemmingslijst", type_caster=int, has_index_column=False
                )

            except Exception as e:
                logger.warning("A problem occurred while attempting to load the hub destination list: \n", exc_info=e)
                return False

            for destination_zone in destination_list:
                if not 1 <= destination_zone <= num_zones:
                    logger.warning(
                        f"Destination zone {destination_zone} in hub destination list is not between 1 and the total number of zones {num_zones}"
                    )
                    valid = False
        return valid

    def _skims_files_validation(self):
        part_of_day = self.config["skims"]["dagsoort"]

        skims_dir = self.config["project"]["paden"]["skims_directory"]
        skims_reader = SkimsSource(skims_dir)
        parking_costs = self.config["geavanceerd"]["parkeerkosten"]["gebruiken"]

        num_zones = -1

        try:
            parking_times = read_parking_times(self.config)
            if parking_costs:
                parking_cost_array = read_csv_from_config(self.config, key="geavanceerd", id="parkeerkosten")
            else:
                parking_cost_array = utils.zeros(len(parking_times))
        except Exception as e:
            logger.warning(
                "A problem occurred while attempting to load the skims files: \n",
                exc_info=e,
            )
            return num_zones, False

        all_valid = True
        for pod in part_of_day:
            try:
                car_time_matrix = skims_reader.read("Auto_Tijd", pod)
                car_distance_matrix = skims_reader.read("Auto_Afstand", pod)
                bike_time_matrix = skims_reader.read("Fiets_Tijd", pod)
                bike_distance_matrix = skims_reader.read("Fiets_Afstand", pod, default=bike_time_matrix)
                pt_time_matrix = skims_reader.read("OV_Tijd", pod)
            except Exception as e:
                logger.warning(
                    "A problem occurred while attempting to load the skims files: \n",
                    exc_info=e,
                )
                return num_zones, False

            num_zones, valid = self._check_size_assumptions(
                car_time_matrix,
                car_distance_matrix,
                bike_time_matrix,
                bike_distance_matrix,
                pt_time_matrix,
                parking_cost_array,
                parking_times,
                old_num_zones=num_zones,
            )
            all_valid &= valid
            if not valid:
                logger.warning(f"Invalid skims files for part of day {pod}")

        return num_zones, all_valid

    def _check_size_assumptions(
        self,
        car_time_matrix: np.ndarray,
        car_distance_matrix: np.ndarray,
        bike_time_matrix: np.ndarray,
        bike_distance_matrix: np.ndarray,
        pt_time_matrix: np.ndarray,
        parking_cost_array: np.ndarray,
        parking_times: np.ndarray | list[list[int]],
        old_num_zones: int,
    ) -> tuple[int, bool]:
        """The shapes of all skims matrices should be the same, and equal to the number of zones in both dimensions

        The skims arrays are expected to have the number of zones as length"""
        if not (
            car_time_matrix.shape
            == car_distance_matrix.shape
            == bike_time_matrix.shape
            == bike_distance_matrix.shape
            == pt_time_matrix.shape
            and pt_time_matrix.shape[0] == pt_time_matrix.shape[1]
        ):
            logger.warning(
                "The shapes of all skims matrices should be the same, and equal to the number of zones in both dimensions"
            )
            logger.warning(
                "Shapes of the skims matrices:\n"
                f"car time matrix: {car_distance_matrix.shape}\n"
                f"car distance matrix: {car_distance_matrix.shape}\n"
                f"bike time matrix: {bike_time_matrix.shape}\n"
                f"bike distance matrix: {bike_distance_matrix.shape}\n"
                f"pt time matrix: {pt_time_matrix}"
            )
            return -1, False

        num_zones = len(pt_time_matrix)
        if not len(parking_cost_array) == num_zones:
            logger.warning(f"The parking costs is expected to be of length equal to the number of zones, {num_zones}")
            return num_zones, False

        if not (len(parking_times) == num_zones and len(parking_times[0]) == 2):
            logger.warning(
                "The parking times array is expected to contain 2 values for each zone (the arrival search time and the departure search time). "
                f"The expected shape is (shape {(num_zones, 2)}), but found shape ({len(parking_times)}, {len(parking_times[0])})"
            )
            return num_zones, False

        if old_num_zones != -1:
            if not num_zones == old_num_zones:
                logger.warning("The number of zones should be the same for different parts of the day")
                return num_zones, False

        return num_zones, True

    def _motive_files_validation(self, num_zones):
        motive = self.config["project"]["motief"]
        scenario = self.config["project"]["verstedelijkingsscenario"]

        traveling_population_path = Path(motive["reizende populatie"])
        destinations_path = Path(motive["bestemmingsplaatsen"])

        segs_source = SegsSource(self.config)

        valid = True
        valid &= self._is_valid_motive_file(segs_source, traveling_population_path.name, scenario, num_zones)
        valid &= self._is_valid_motive_file(segs_source, destinations_path.name, scenario, num_zones)
        return valid

    def _is_valid_motive_file(self, segs_source: SegsSource, filename, scenario, num_zones):
        try:
            content = segs_source.read(filename, scenario=scenario)
        except Exception as e:
            logger.warning(
                "A problem occurred while attempting to load the motive's traveling population files: \n",
                exc_info=e,
            )
            return False
        expected_shape = (num_zones, 4)
        if content.shape != expected_shape:
            logger.warning(
                f"The content of {filename} should have shape {expected_shape} (#zones x #income_classes), but has shape {content.shape}"
            )
            return False
        return True


def validate_config(config, strict=True, log_lvl=logging.WARNING):
    """Validate a config dictionary."""
    return validateConfigWithTemplate(config, default_configuration_definition(), strict=strict, log_lvl=log_lvl)


def try_fix_incompatible_configuration(config):
    """Attempt to recover from incompatible configuration files.

    Some configuration changes can be automatically resolved to
    maintain backward compatibility.
    Adds default values to the config if they are missing.
    """
    fixers = [
        transfer_to_advanced_tab,
        transfer_to_chains_tab,
        fiets_checklist_to_checkbox,
        motieven_to_motief,
    ]

    default = default_config()
    for fixer in fixers:
        config = fixer(config)
        new_config = merge_configs(default, config)
        if validate_config(new_config, log_lvl=logging.INFO):
            logger.info("Auto fixed config")
            return new_config
    logger.warning("Could not auto fix configuration. Using provided config as-is.")
    return config


def merge_configs(default, custom):
    """Merge custom configuration with default configuration."""
    if isinstance(default, dict) and isinstance(custom, dict):
        result = default.copy()
        for key, value in custom.items():
            result[key] = merge_configs(default.get(key, {}), value)
        return result
    return custom if custom is not None else default


def transfer_to_advanced_tab(config):
    """Try to recover from missing "geavanceerd" configuration.

    Introduced in commit `6c6684c`.
    """
    logger.info('Trying to auto fix "geavanceerd" configuration entry.')

    # There is nothing to fix if the deprecated key is not present.
    if "verdeling" not in config:
        return config

    for key in ["kunstmab", "parkeerkosten", "additionele_kosten"]:
        if key not in config["verdeling"]:
            continue

        config["geavanceerd"][key] = config["verdeling"].pop(key)

    return config


def transfer_to_chains_tab(config):
    """Try to recover from missing "ketens" configuration.

    Introduced in commit `9bf0d1a`.
    """
    if "chains" in config:
        # Cannot fix: a translated entry is already present.
        return

    if "ketens" in config:
        # Cannot fix: ketens already present.
        return config

    logger.info('Trying to auto fix "ketens" configuration entry.')

    group = "ketens"
    config[group] = {}
    translation = {"ketens": "chains"}
    for key in ["ketens"]:
        config[group][translation[key]] = config["project"].pop(key)

    # Add missing bestemmingslijst entry.
    config[group]["bestemmingslijst"] = {
        "gebruiken": False,
        "bestand": "",
    }

    return config


def motieven_to_motief(config):
    if "motieven" in config["project"]:
        if config["project"]["motieven"] == ["werk"]:
            # This motief is the default new motive, so we can remove the motieven section and rely on the default
            del config["project"]["motieven"]
        else:
            logger.warning(
                "'motieven' defined in config other than the default 'werk' motief. Manually edit the config to use the new 'motief'"
            )
    return config


def fiets_checklist_to_checkbox(config):
    """Update decremented fiets checklist into checkbox."""

    fiets_of_efiets = config["project"]["fiets of E-fiets"]
    is_deprecated = isinstance(fiets_of_efiets, list)

    if not is_deprecated:
        return config

    # Since chancing the configuration from a checklist into a
    # checkbox, selecting multiple entries are no longer supported,
    # so multiple entries are not attempted to be fixed.
    if len(fiets_of_efiets) > 1:
        return config

    is_enabled = fiets_of_efiets == ["E-fiets"]
    config["project"]["fiets of E-fiets"] = {"E-fiets": is_enabled}
    return config


def _validateDefaultType(valtype, defvalue):
    defvaluetype = type(defvalue)
    if defvaluetype is dict:
        return False
    if (
        valtype == "text" or valtype == "file" or valtype == "directory" or valtype == "choice"
    ) and defvaluetype is not str:
        return False
    if valtype == "number" and not (defvaluetype is float or defvaluetype is int):
        return False
    if (valtype == "checklist") and defvaluetype is not list:
        return False
    if (valtype == "checkbox") and defvaluetype is not bool:
        return False
    return True


def validateTemplate(template):
    for key in set(template.keys()):
        t = template[key]
        if key == "label":
            continue
        if type(t) is not dict:
            print("Het 'type' veld mist.")
            return False
        if "type" in t:
            valtype = t["type"]
            if valtype == "checklist" or valtype == "choice":
                if "items" not in t:
                    print(f"Items is verplicht voor type '{valtype}' in '{key}'.")
                    return False
                if len(t["items"]) < 1:
                    print(f"Geen opties in 'items' voor type '{valtype}' in '{key}'.")
                    return False
            if "range" in t:
                valrange = t["range"]
                if valtype != "number":
                    print(f"De 'range' optie wordt niet ondersteund voor type '{valtype}'.")
                    return False
                if type(valrange) is not list:
                    print(f"De 'range' moet worden opgegeven als een lijst in '{key}'.")
                    return False
                if len(valrange) != 2:
                    print(f"De 'range' moet precies twee waarden bevatten in '{key}'.")
                    return False
            if "default" in t:
                defvalue = t["default"]
                if not _validateDefaultType(type, defvalue):
                    print(f"Default waarde '{defvalue}' voor '{key}' past niet bij type '{valtype}'.")
                    return False
        else:
            return validateTemplate(template[key])
    return True


### Validate config


def _false(value, template):
    return False


def _validateText(value, template):
    if type(value) is not str:
        return False
    return True


def _validateNumber(value, template):
    if not (type(value) is float or type(value) is int):
        return False
    if "range" in template:
        if value < template.range[0] or value > template.range[1]:
            return False
    return True


def _validateItems(values, template):
    if type(values) is not list:
        return False
    for item in values:
        if item not in template["items"]:
            return False
    return True


def _validateBox(value, template):
    return value in [True, False]


def _validateChoice(value, template):
    if value not in template["items"]:
        return False
    return True


def validateConfigWithTemplate(config, template, strict=False, log_lvl=logging.WARNING):
    """
    Valideert een configuratie gegeven een template.
    Er wordt gekeken naar structuur en waarden van de bladen.
    Indien strict op False staat, dan is het toegestaan om in de config
    extra velden te hebben die niet in het template staan. In dat geval
    garandeert de validatie alleen dus de standaard velden. De overige
    waarden worden klakkeloos overgenomen.
    Resultaat: True - Configuratie klopt.
               False - Configuratie klopt niet.
    """
    templatekeys = [key for key in template.keys() if key != "label"]
    if not isinstance(config, dict):
        logger.log(log_lvl, "Validation failed: config is not a dictionary.")
        return False
    if strict and set(config.keys()) != set(templatekeys):
        logger.log(
            log_lvl,
            "Validation failed: config keys do not match template keys in strict mode. "
            f"Config keys not in template: {set(config.keys()) - set(templatekeys)}; "
            f"Template keys not in config: {set(templatekeys) - set(config.keys())}",
        )
        return False
    for key in templatekeys:
        if not strict:
            if key not in config:
                logger.log(log_lvl, f"Validation failed: key '{key}' is missing in config but present in template.")
                return False
        if "type" in template[key]:
            check = {
                "text": _validateText,
                "number": _validateNumber,
                "directory": _validateText,
                "file": _validateText,
                "checkbox": _validateBox,
                "checklist": _validateItems,
                "choice": _validateChoice,
            }
            if not check.get(template[key]["type"], _false)(config[key], template[key]):
                logger.log(
                    log_lvl,
                    f"Validation failed for key '{key}' with value '{config[key]}' and template '{template[key]}'",
                )
                return False
        elif type(template[key]) is dict:
            if not validateConfigWithTemplate(config[key], template[key], strict=strict, log_lvl=log_lvl):
                return False
    return True
