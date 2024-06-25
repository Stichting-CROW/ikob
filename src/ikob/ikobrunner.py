import logging
from tkinter import Tk, Frame, BooleanVar, StringVar
from tkinter import Button
from tkinter import filedialog, messagebox
from ikob.config import widgets

# from ConfiguratieDefinitie import *
from ikob.ikobconfig import loadConfig, getConfigFromArgs

from ikob.Ervarenreistijdberekenen import ervaren_reistijd_berekenen
from ikob.Verdelingovergroepen import verdeling_over_groepen
from ikob.Gewichtenberekenenenkelscenarios import gewichten_berekenen_enkel_scenarios
from ikob.Gewichtenberekenencombis import gewichten_berekenen_combis
from ikob.Ontplooiingsmogelijkhedenechteinwoners import ontplooingsmogelijkheden_echte_inwoners
from ikob.Potentiebedrijven import potentie_bedrijven
from ikob.concurrentie import concurrentie_om_arbeidsplaatsen
from ikob.concurrentie import concurrentie_om_inwoners
from ikob.datasource import DataSource

logger = logging.getLogger(__name__)


def run_scripts(project_file, skip_steps=None):
    """
    Run through all steps for a given project.
    Steps are skipped if skip_steps is set.
    """
    logger.info("Reading project file: %s.", project_file)
    config = getConfigFromArgs(project_file)
    datasource = DataSource(config, config['__filename__'])

    if not skip_steps:
        skip_steps = [False] * 8

    if not skip_steps[0]:
        ervaren_reistijd_berekenen(config, datasource)

    if not skip_steps[1]:
        verdeling_over_groepen(config, datasource)

    if not skip_steps[2]:
        gewichten_berekenen_enkel_scenarios(config, datasource)

    if not skip_steps[3]:
        gewichten_berekenen_combis(config, datasource)

    if not skip_steps[4]:
        ontplooingsmogelijkheden_echte_inwoners(config, datasource)

    if not skip_steps[5]:
        potentie_bedrijven(config, datasource)

    if not skip_steps[6]:
        concurrentie_om_arbeidsplaatsen(config, datasource)

    if not skip_steps[7]:
        concurrentie_om_inwoners(config, datasource)


# User interface


class ConfigApp(Tk):
    PAD = {"padx": 5, "pady": 5}
    IPAD = {"ipadx": 5, "ipady": 5}

    stappen = (
            "Gegeneraliseerde reistijd berekenen uit tijd en kosten",
            "Verdeling van de groepen over de buurten of zones",
            "Gewichten (reistijdvervalscurven) voor auto, OV, fiets en E-fiets apart",
            "Maximum gewichten van meerdere modaliteiten",
            "Bereikbaarheid arbeidsplaatsen voor inwoners",
            "Potentie bereikbaarheid voor bedrijven en instellingen",
            "Concurrentiepositie voor bereik arbeidsplaatsen",
            "Concurrentiepositie voor bedrijven qua bereikbaarheid")

    def __init__(self):
        super().__init__()
        self.title("IKOB Runner")
        self._checks = [BooleanVar(value=True) for _ in self.stappen]
        self._configvar = StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.widgets = []
        F1 = Frame()
        F1.pack(expand=1, fill="both", **self.PAD)
        self.widgets.extend(
            widgets.pathWidget(F1, "Project", self._configvar, file=True)
        )
        self.widgets.append(F1)
        labels = [stap for stap in self.stappen]
        self.widgets.extend(
            widgets.checklistWidget(
                F1, "Stappen", labels, self._checks, row=1, itemsperrow=1
            )
        )
        B = Button(master=F1, text="Start", command=self.cmdRun)
        B.grid(row=2, column=2, sticky="ew", **self.PAD)
        self.widgets.append(B)

    def cmdRun(self):
        project_file = self._configvar.get()

        # Skip the test when its _not_ selected.
        skip_steps = [not check.get() for check in self._checks]

        try:
            run_scripts(project_file, skip_steps)
        except BaseException as err:
            msg = f"An error occured: {err}"
            messagebox.showerror(title="FOUT", message=msg)
        else:
            msg = "Alle stappen zijn succesvol uitegevoerd."
            messagebox.showinfo(title="Gereed", message=msg)

    def cmdLaadProject(self):
        filename = filedialog.askopenfilename(
            title="Kies een .json project bestand.",
            filetypes=[("project file", ".json")],
        )
        if filename:
            try:
                _ = loadConfig(filename)
            except ValueError:
                messagebox.showerror(
                    title="Fout",
                    message="Het bestand bevat geen geldige configuratie.",
                )
            except IOError:
                messagebox.showerror(
                    title="Fout", message="Het bestand kan niet worden geladen."
                )


def main():
    App = ConfigApp()
    App.mainloop()


if __name__ == "__main__":
    main()
