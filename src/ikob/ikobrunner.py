import logging
from tkinter import Tk, Frame, BooleanVar, StringVar
from tkinter import Button
from tkinter import filedialog, messagebox
from ikob.config import widgets

from ikob.ikobconfig import loadConfig, getConfigFromArgs
from ikob.datasource import DataType, DataSource

from ikob.generalised_travel_time import generalised_travel_time
from ikob.group_distribution import distribute_over_groups
from ikob.single_weights import calculate_single_weights
from ikob.combined_weights import calculate_combined_weights
from ikob.deployment_opportunities import deployment_opportunities
from ikob.possible_companies import possible_companies
from ikob.competition import competition_on_jobs
from ikob.competition import competition_on_citizens

logger = logging.getLogger(__name__)


def run_scripts(project_file, skip_steps=None):
    """
    Run through all steps for a given project.
    Steps are skipped if skip_steps is set.
    """
    logger.info("Reading project file: %s.", project_file)
    config = getConfigFromArgs(project_file)

    if not skip_steps:
        skip_steps = [False] * 8

    if not skip_steps[0]:
        travel_time = generalised_travel_time(config)
    else:
        travel_time = DataSource(config, DataType.ERVARENREISTIJD)

    if not skip_steps[1]:
        # TODO: Pass temporary SEGS output as arguments too.
        distribute_over_groups(config)

    if not skip_steps[2]:
        single_weights = calculate_single_weights(config, travel_time)
    else:
        single_weights = DataSource(config, DataType.GEWICHTEN)

    if not skip_steps[3]:
        combined_weights = calculate_combined_weights(config, single_weights)
    else:
        combined_weights = DataSource(config, DataType.GEWICHTEN)

    if not skip_steps[4]:
        possiblities = deployment_opportunities(config, single_weights, combined_weights)
    else:
        possiblities = DataSource(config, DataType.BESTEMMINGEN)

    if not skip_steps[5]:
        origins = possible_companies(config, single_weights, combined_weights)
    else:
        origins = DataSource(config, DataType.HERKOMSTEN)

    if not skip_steps[6]:
        competition_jobs = competition_on_jobs(config, single_weights, combined_weights, origins)
    else:
        competition_jobs = DataSource(config, DataType.CONCURRENTIE)

    if not skip_steps[7]:
        competition_citizens = competition_on_citizens(config, single_weights, combined_weights, possiblities)
    else:
        competition_citizens = DataSource(config, DataType.CONCURRENTIE)

    # TODO: For now all files are written to disk to assert their contents in
    # end-to-end testing. Ultimately only files that are essential outputs should persist.
    for container in [travel_time, single_weights, combined_weights, possiblities, origins, competition_citizens, competition_jobs]:
        container.store()


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
