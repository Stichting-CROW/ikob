#!/usr/bin/env python3
import argparse
import json
import logging
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from ikob.config import build, validate
from ikob.configuration_definition import (
    default_config,
    default_configuration_definition,
    project_name,
)
from ikob.zone_ids import initialize_zone_id_store

logger = logging.getLogger(__name__)

# Interface: load/save config files.


def _project_filename(project_name, make_safe=True):
    """
    Doe een 'veilige' suggestie voor een bestandsnaam gebaseerd op een
    door de gebruiker opgegeven naam van een project.
    """
    filename, ext = os.path.splitext(project_name)
    if ext != ".json":
        filename = project_name
    if make_safe:
        filename = re.sub(r"[^\w\s]", "", filename)
        filename = re.sub(r"\s+", "_", filename)
    return filename + ".json"


def get_config_from_args(project=None, validate_files: bool = True, allow_extra_zone_ids: bool = True):
    """Load a project, prepare its zone store, and validate its inputs.

    Returns the configuration and whether input validation succeeded.
    """
    if not project:
        parser = argparse.ArgumentParser()
        parser.add_argument("project", type=str, help="Het .json project bestand.")
        args = parser.parse_args()
        project = args.project

    config, valid = load_config(project, validate_files=validate_files, allow_extra_zone_ids=allow_extra_zone_ids)
    return config, valid


def load_config(filename, *, validate_files: bool, allow_extra_zone_ids: bool = True):
    """Read and migrate a configuration without reading its input data or preparing runtime state.

    Validates the files in the config based on input flags.
    """
    try:
        with open(filename) as json_file:
            config = json.load(json_file)
    except BaseException as e:  # noqa: BLE001
        raise OSError(f"Kan niet lezen uit: '{filename}' with error:\n'{e}'.")

    if not validate.validate_config(config):
        msg = "Loaded config file: '%s' is incompatible with current IKOB."
        logger.warning(msg, filename)

        config = validate.try_fix_incompatible_configuration(config)

        if validate.validate_config(config):
            msg = "Automatically recovered from incompatible config file."
            logger.info(msg)
        else:
            msg = "Configuration has irrecoverable incompatible format."
            logger.error(msg)
            raise ValueError(msg)

    config["__filename__"] = os.path.splitext(os.path.basename(filename))[0]

    valid = True
    if validate_files:
        valid = initialize_zone_id_store(config, allow_extra_zone_ids=allow_extra_zone_ids)
        if valid:
            valid = validate.FileValidator(config).validate_input_files()
    return config, valid


def save_config(filename, config):
    """Save the configuration, reporting input problems as warnings rather than save failures."""
    try:
        if "__filename__" in config:
            del config["__filename__"]
        with open(filename, "w") as json_file:
            json.dump(config, json_file, indent=2)
    except BaseException as e:
        logger.error(f"Kan configuratie niet wegschrijven naar: {filename}.", exc_info=e)
        raise OSError(f"Kan configuratie niet wegschrijven naar: {filename}.")

    try:
        logger.info(f"Config written to {filename}. Starting config validation.")
        config["__filename__"] = os.path.splitext(os.path.basename(filename))[0]
        config_is_valid = initialize_zone_id_store(config)
        if config_is_valid:
            config_is_valid = validate.FileValidator(config).validate_input_files()
        del config["__filename__"]
    except BaseException as e:
        logger.error(f"Unexpected Error during config validation: {filename}.", exc_info=e)
        config_is_valid = False

    return config_is_valid


# User interface


class ConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IKOB configuratie")
        self.add_variables()
        self.create_widgets()

    def add_variables(self):
        self._template = default_configuration_definition()
        build.addTkVarsTemplate(self._template)

    def create_widgets(self):
        self._widgets = build.buildTkInterface(
            self,
            self._template,
            cmdNew=self.new_project_cmd,
            cmdLoad=self.load_project_cmd,
            cmdSave=self.save_project_cmd,
        )

    def new_project_cmd(self):
        build.setTkVars(self._template, default_config())

    def load_project_cmd(self):
        filename = filedialog.askopenfilename(
            title="Kies een .json project bestand.",
            filetypes=[("project file", ".json")],
        )
        if filename:
            try:
                read_config, _ = load_config(filename, validate_files=False)
            except ValueError:
                messagebox.showerror(
                    title="Fout",
                    message="Het bestand bevat geen geldige configuratie.",
                )
            except OSError:
                messagebox.showerror(title="Fout", message="Het bestand kan niet worden geladen.")
            else:
                build.setTkVars(self._template, read_config)

    def save_project_cmd(self):
        config = build.buildConfigDict(self._template)
        filename = filedialog.asksaveasfilename(
            title="Kies een .json project bestand.",
            initialfile=_project_filename(project_name(config)),
            filetypes=[("project file", ".json")],
        )

        # The filename remains empty when the dialog is cancelled.
        if filename == "":
            return

        filename = _project_filename(filename, make_safe=False)
        config_is_valid = True
        try:
            config_is_valid = save_config(filename, config)
        except OSError:
            messagebox.showerror(title="Fout", message="Het bestand kan niet worden opgeslagen.")
        else:
            if not config_is_valid:
                messagebox.showwarning(
                    title="Opgeslagen", message="Configuratie opgeslagen met waarschuwingen. Zie console."
                )
            else:
                messagebox.showinfo(title="Opgeslagen", message="Configuratie opgeslagen.")


def main():
    parser = argparse.ArgumentParser(prog="ikobconfig", description="Launch the IKOB config GUI.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display logging messages over stdout.",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s -  %(message)s"
        )

    if not validate.validateTemplate(default_configuration_definition()):
        messagebox.showerror(
            title="Fout",
            message="De standaard configuratiedefinitie is niet geldig: Kijk in ConfiguratieDefinitie.py",
        )
        sys.exit(1)
    App = ConfigApp()
    App.mainloop()


if __name__ == "__main__":
    main()
