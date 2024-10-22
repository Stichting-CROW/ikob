import argparse
import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

from ikob.config import build, validate
from ikob.configuration_definition import (default_config,
                                           default_configuration_definition,
                                           project_name, validate_config)

# Interface: load/save config files.


def _projectFilename(projectname, make_safe=True):
    """
    Doe een 'veilige' suggestie voor een bestandsnaam gebaseerd op een
    door de gebruiker opgegeven naam van een project.
    """
    filename, ext = os.path.splitext(projectname)
    if ext != ".json":
        filename = projectname
    if make_safe:
        filename = re.sub(r"[^\w\s]", "", filename)
        filename = re.sub(r"\s+", "_", filename)
    return filename + ".json"


def getConfigFromArgs(project=None):
    """
    Leest een configuratiebestand die is opgegeven in de 'command line'.
    Resultaat: Een geldige, ingeladen configuratie.
    Fouten: IOError - Als het opegeven bestand niet bestaat of niet geopend kon worden.
            ValueError - Als het opgegeven bestand geen geldige configuratie bevat.
    """
    if project:
        return loadConfig(project)

    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=str, help="Het .json project bestand.")
    args = parser.parse_args()
    return loadConfig(args.project)


def loadConfig(filename):
    config = None
    try:
        with open(filename) as json_file:
            config = json.load(json_file)
    except BaseException:
        raise IOError(f"Kan niet lezen uit: {filename}.")
    if config:
        if not validate_config(config):
            raise ValueError("Configuratie heeft een incompatibel formaat.")
        config["__filename__"] = os.path.splitext(
            os.path.basename(filename))[0]
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
        self.add_variables()
        self.create_widgets()

    def add_variables(self):
        self._template = default_configuration_definition()
        build.addTkVarsTemplate(self._template)

    def create_widgets(self):
        self._widgets = build.buildTkInterface(
            self,
            self._template,
            cmdNew=self.cmdNieuwProject,
            cmdLoad=self.cmdLaadProject,
            cmdSave=self.cmdOpslaanProject,
        )

    def cmdNieuwProject(self):
        build.setTkVars(self._template, default_config())

    def cmdLaadProject(self):
        filename = filedialog.askopenfilename(
            title="Kies een .json project bestand.",
            filetypes=[("project file", ".json")],
        )
        if filename:
            try:
                read_config = loadConfig(filename)
            except ValueError:
                messagebox.showerror(
                    title="Fout",
                    message="Het bestand bevat geen geldige configuratie.",
                )
            except IOError:
                messagebox.showerror(
                    title="Fout", message="Het bestand kan niet worden geladen.")
            else:
                build.setTkVars(self._template, read_config)

    def cmdOpslaanProject(self):
        config = build.buildConfigDict(self._template)
        filename = filedialog.asksaveasfilename(
            title="Kies een .json project bestand.",
            initialfile=_projectFilename(project_name(config)),
            filetypes=[("project file", ".json")],
        )
        filename = _projectFilename(filename, make_safe=False)
        try:
            saveConfig(filename, config)
        except BaseException:
            messagebox.showerror(
                title="Fout", message="Het bestand kan niet worden opgeslagen."
            )
        else:
            messagebox.showinfo(
                title="Opgeslagen",
                message="Configuratie opgeslagen.")


def main():
    if not validate.validateTemplate(default_configuration_definition()):
        messagebox.showerror(
            title="Fout",
            message="De standaard configuratiedefinitie is niet geldig: Kijk in ConfiguratieDefinitie.py",
        )
        exit(1)
    App = ConfigApp()
    App.mainloop()


if __name__ == "__main__":
    main()
