import argparse
import logging
import os
import re
import sys
import tkinter as tk
import traceback
from dataclasses import asdict
from enum import StrEnum
from tkinter import filedialog, messagebox

import yaml

from ikob.gui.configuration_definition import (
    FILENAME_FIELD_NAME,
    IkobConfig,
)
from ikob.gui.gui_builder import IkobGui

logger = logging.getLogger(__name__)

# Interface: load/save config files.

yaml.SafeDumper.add_multi_representer(
    StrEnum,
    yaml.representer.SafeRepresenter.represent_str,
)


def _project_filename(project_name, make_safe=True):
    """
    Doe een 'veilige' suggestie voor een bestandsnaam gebaseerd op een
    door de gebruiker opgegeven naam van een project.
    """
    filename, ext = os.path.splitext(project_name)
    if ext != ".yaml":
        filename = project_name
    if make_safe:
        filename = re.sub(r"[^\w\s]", "", filename)
        filename = re.sub(r"\s+", "_", filename)
    return filename + ".yaml"


def get_config_from_args(project=None):
    """
    Leest een configuratiebestand die is opgegeven in de 'command line'.
    Resultaat: Een geldige, ingeladen configuratie.
    Fouten: IOError - Als het opgegeven bestand niet bestaat of niet geopend kon worden.
            ValueError - Als het opgegeven bestand geen geldige configuratie bevat.
    """
    if project:
        return load_config(project)

    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=str, help="Het .json project bestand.")
    args = parser.parse_args()
    return load_config(args.project)


def load_config(filename):
    config = None
    try:
        with open(filename) as file:
            yaml_dict = yaml.safe_load(file)
            config = IkobConfig(**yaml_dict)
    except BaseException as e:
        raise IOError(f"Kan niet lezen uit: '{filename}' with error:\n'{e}'.")

    # This is a bit of an ugly hack that should be fixed
    setattr(config, FILENAME_FIELD_NAME, os.path.splitext(os.path.basename(filename))[0])
    return config


def saveConfig(filename: str, config: IkobConfig):
    try:
        with open(filename, "w") as file:
            yaml.dump(asdict(config), file, indent=2, default_flow_style=False, Dumper=yaml.SafeDumper)
    except BaseException as e:
        raise IOError(f"Kan configuratie niet wegschrijven naar: {filename}.", e)


# User interface


class ConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IKOB configuratie")
        self.gui_builder = IkobGui()
        self._widgets = self.gui_builder.build_tk_interface(
            self,
            new_cmd=self._new_project_cmd,
            load_cmd=self._load_project_cmd,
            save_cmd=self._save_project_cmd,
        )

    def _new_project_cmd(self):
        self.gui_builder.reset_gui()

    def _load_project_cmd(self):
        filename = filedialog.askopenfilename(
            title="Kies een .yaml project bestand.",
            filetypes=[("project file", ".yaml"), ("Project file", ".json")],
        )
        if filename:
            try:
                read_config = load_config(filename)
            except ValueError:
                messagebox.showerror(
                    title="Fout",
                    message="Het bestand bevat geen geldige configuratie.",
                )
            except IOError:
                messagebox.showerror(title="Fout", message="Het bestand kan niet worden geladen.")
            else:
                self.gui_builder.load_config_in_gui(read_config)

    def _save_project_cmd(self):
        config = self.gui_builder.get_config_from_gui()
        filename = filedialog.asksaveasfilename(
            title="Kies een .yaml project bestand.",
            initialfile=_project_filename(config.project.name),
            filetypes=[("project file", ".yaml")],
        )

        # The filename remains empty when the dialog is cancelled.
        if filename == "":
            return

        filename = _project_filename(filename, make_safe=False)
        try:
            saveConfig(filename, config)
        except BaseException:
            logger.error(traceback.format_exc())
            messagebox.showerror(title="Fout", message="Het bestand kan niet worden opgeslagen.")
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

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s \t -  %(message)s",
    )
    logger.info("starting app")

    App = ConfigApp()
    App.mainloop()


if __name__ == "__main__":
    main()
