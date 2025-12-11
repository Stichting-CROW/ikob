import argparse
import json
import logging
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from ikob.configuration_definition import (
    default_config,
    default_configuration_definition,
    project_name,
    try_fix_incompatible_configuration,
    validate_config,
)
from ikob.gui.gui_builder import GuiBuilder
from ikob.gui.template_validator import TemplateValidator

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
        with open(filename) as json_file:
            config = json.load(json_file)
    except BaseException as e:
        raise IOError(f"Kan niet lezen uit: '{filename}' with error:\n'{e}'.")
    if config:
        if not validate_config(config):
            msg = "Loaded config file: '%s' is incompatible with current IKOB."
            logger.warning(msg, filename)

            config = try_fix_incompatible_configuration(config)

            if validate_config(config):
                msg = "Automatically recovered from incompatible config file."
                logger.info(msg)
            else:
                msg = "Configuration has irrecoverable incompatible format."
                logger.error(msg)
                raise ValueError(msg)

        config["__filename__"] = os.path.splitext(os.path.basename(filename))[0]
    return config


def saveConfig(filename, config):
    try:
        with open(filename, "w") as json_file:
            json.dump(config, json_file, indent=2)
    except BaseException:
        raise IOError(f"Kan configuratie niet wegschrijven naar: {filename}.")
    return True


# User interface


class ConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IKOB configuratie")
        self.gui_builder = GuiBuilder()
        self.add_variables()
        self.create_widgets()

    def add_variables(self):
        self._template = default_configuration_definition()
        self.gui_builder.add_tk_vars_template(self._template)

    def create_widgets(self):
        self._widgets = self.gui_builder.build_tk_interface(
            self,
            self._template,
            new_cmd=self.new_project_cmd,
            load_cmd=self.load_project_cmd,
            save_cmd=self.save_project_cmd,
        )

    def new_project_cmd(self):
        self.gui_builder.set_tk_vars(self._template, default_config())

    def load_project_cmd(self):
        filename = filedialog.askopenfilename(
            title="Kies een .json project bestand.",
            filetypes=[("project file", ".json")],
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
                self.gui_builder.set_tk_vars(self._template, read_config)

    def save_project_cmd(self):
        config = self.gui_builder.build_config_dict(self._template)
        filename = filedialog.asksaveasfilename(
            title="Kies een .json project bestand.",
            initialfile=_project_filename(project_name(config)),
            filetypes=[("project file", ".json")],
        )

        # The filename remains empty when the dialog is cancelled.
        if filename == "":
            return

        filename = _project_filename(filename, make_safe=False)
        try:
            saveConfig(filename, config)
        except BaseException:
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

    if args.verbose:
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s -  %(message)s"
        )

    if not TemplateValidator.validate_template(default_configuration_definition()):
        messagebox.showerror(
            title="Fout",
            message="De standaard configuratiedefinitie is niet geldig: Kijk in ConfiguratieDefinitie.py",
        )
        exit(1)
    App = ConfigApp()
    App.mainloop()


if __name__ == "__main__":
    main()
