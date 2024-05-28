import logging
from tkinter import Tk, Frame, BooleanVar, StringVar
from tkinter import Button
from tkinter import filedialog, messagebox
from config import widgets

# from ConfiguratieDefinitie import *
from ikobconfig import loadConfig, getConfigFromArgs

from Ervarenreistijdberekenen import ervaren_reistijd_berekenen
from Verdelingovergroepen import verdeling_over_groepen
from Gewichtenberekenenenkelscenarios import gewichten_berekenen_enkel_scenarios
from Gewichtenberekenencombis import gewichten_berekenen_combis
from Ontplooiingsmogelijkhedenechteinwoners import ontplooingsmogelijkheden_echte_inwoners
from Potentiebedrijven import potentie_bedrijven
from Concurrentieomarbeidsplaatsen import concurrentie_om_arbeidsplaatsen
from Concurrentieominwoners import concurrentie_om_inwoners

logger = logging.getLogger(__name__)


# fmt: off
stappen = (
    ( "Gegeneraliseerde reistijd berekenen uit tijd en kosten", ervaren_reistijd_berekenen),
    ( "Verdeling van de groepen over de buurten of zones", verdeling_over_groepen),
    ( "Gewichten (reistijdvervalscurven) voor auto, OV, fiets en E-fiets apart", gewichten_berekenen_enkel_scenarios),
    ( "Maximum gewichten van meerdere modaliteiten", gewichten_berekenen_combis),
    ( "Bereikbaarheid arbeidsplaatsen voor inwoners", ontplooingsmogelijkheden_echte_inwoners),
    ( "Potentie bereikbaarheid voor bedrijven en instellingen", potentie_bedrijven),
    ( "Concurrentiepositie voor bereik arbeidsplaatsen", concurrentie_om_arbeidsplaatsen),
    ( "Concurrentiepositie voor bedrijven qua bereikbaarheid", concurrentie_om_inwoners),
)
# fmt: on

PAD = {"padx": 5, "pady": 5}
IPAD = {"ipadx": 5, "ipady": 5}


def run_scripts(project_file, skip_steps):
    """
    Run through all steps for a given project.
    Tests are skipped if skip_steps is set.
    Yields the current step and corresponding return code.
    """
    logger.info("Reading project file: %s.", project_file)
    config = getConfigFromArgs(project_file)

    for (description, method), skip in zip(stappen, skip_steps):
        if skip:
            logger.info("Skipping step: %s.", description)
            continue

        logger.info("Running step: %s.", description)
        result = method(config)
        yield description, result


# User interface


class ConfigApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("IKOB Runner")
        self._checks = [BooleanVar(value=True) for _ in stappen]
        self._configvar = StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.widgets = []
        F1 = Frame()
        F1.pack(expand=1, fill="both", **PAD)
        self.widgets.extend(
            widgets.pathWidget(F1, "Project", self._configvar, file=True)
        )
        self.widgets.append(F1)
        labels = [x[0] for x in stappen]
        self.widgets.extend(
            widgets.checklistWidget(
                F1, "Stappen", labels, self._checks, row=1, itemsperrow=1
            )
        )
        B = Button(master=F1, text="Start", command=self.cmdRun)
        B.grid(row=2, column=2, sticky="ew", **PAD)
        self.widgets.append(B)

    def cmdRun(self):
        project_file = self._configvar.get()

        # Skip the test when its _not_ selected.
        skip_steps = [not check.get() for check in self._checks]

        # Initialise step in case iterator fails before step is set.
        step = stappen[0]

        try:
            for step, result in run_scripts(project_file, skip_steps):
                if result is not None:
                    msg = f"Python gaf fout code: {result} in stap {step}.",
                    messagebox.showerror(title="FOUT", message=msg)
                    return
        except BaseException as err:
            msg = f"Fout in Stap {step}: {err}"
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
