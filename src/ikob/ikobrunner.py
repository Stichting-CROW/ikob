import argparse
import logging
import sys
import threading
import traceback
from tkinter import BooleanVar, Button, Frame, StringVar, Tk, Widget, filedialog, messagebox

from ikob.combined_weights import calculate_combined_weights
from ikob.competition import competition_on_citizens, competition_on_destinations
from ikob.config import validate, widgets
from ikob.datasource import DataSource, DataType
from ikob.distribute_over_groups import distribute_population_over_groups
from ikob.generalized_travel_time import generalized_travel_time
from ikob.ikobconfig import get_config_from_args, load_config
from ikob.reachable_destinations import reachable_destinations
from ikob.reachable_population import reachable_population
from ikob.single_weights import calculate_single_weights

logger = logging.getLogger(__name__)


def run_scripts(project_file, skip_steps: list[bool] | None = None, write_weights: bool = False):
    """
    Run through all steps for a given project.

    For details about the all the steps taken see documentation/IKOB-algorithm.pdf.
    In de docstring of each specific step the relevant section of the documentation is referenced.
    documentation/IKOB-documentation-partially-outdated.pdf is partially outdated, but might still provide some insight into the code.
    Do note that at the very least naming has changed and output is not written to disk after each step any more.

    Args:
        project_file: the path to a JSON project config
        skip_steps: a list of bools to skip that index step
        write_weights: skip writing out weights results
    """
    logger.info("Reading project file: %s.", project_file)
    config = get_config_from_args(project_file)

    valid = validate.FileValidator(config).validate_input_files()
    if not valid:
        raise ValueError("Invalid input files, see console warnings.")

    logger.info("Starting simulations...")
    if not skip_steps:
        skip_steps = [False] * 8

    if not skip_steps[0]:
        travel_time = generalized_travel_time(config)
    else:
        travel_time = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME)

    if not skip_steps[1]:
        # TODO: Pass temporary SEGS output as arguments too.
        distribute_population_over_groups(config)

    if not skip_steps[2]:
        single_weights = calculate_single_weights(config, travel_time)
    else:
        single_weights = DataSource(config, DataType.WEIGHTS)

    if not skip_steps[3]:
        combined_weights = calculate_combined_weights(config, single_weights)
    else:
        combined_weights = DataSource(config, DataType.WEIGHTS)

    if not skip_steps[4]:
        opportunities = reachable_destinations(config, single_weights, combined_weights)
    else:
        opportunities = DataSource(config, DataType.DESTINATIONS)

    if not skip_steps[5]:
        origins = reachable_population(config, single_weights, combined_weights)
    else:
        origins = DataSource(config, DataType.ORIGINS)

    if not skip_steps[6]:
        competition_destinations = competition_on_destinations(config, single_weights, combined_weights, origins)
    else:
        competition_destinations = DataSource(config, DataType.COMPETITION)

    if not skip_steps[7]:
        competition_citizens = competition_on_citizens(config, single_weights, combined_weights, opportunities)
    else:
        competition_citizens = DataSource(config, DataType.COMPETITION)

    logger.info("All simulations are completed.")

    # TODO: For now all files are written to disk to assert their contents in
    # end-to-end testing. Ultimately only files that are essential outputs
    # should persist.
    logger.info("Writing output to disk...")
    sources_to_save = [travel_time, opportunities, origins, competition_citizens, competition_destinations]
    if write_weights:
        sources_to_save.extend([single_weights, combined_weights])

    for container in sources_to_save:
        container.store()

    DataSource.write_output_md(config)


# User interface
class ConfigApp(Tk):
    PAD_X = 5
    PAD_Y = 5

    stappen = (
        "Gegeneraliseerde reistijd berekenen uit tijd en kosten",
        "Verdeling van de groepen over de buurten of zones",
        "Gewichten (reistijdvervalscurven) voor auto, OV, fiets en E-fiets apart",
        "Maximum gewichten van meerdere modaliteiten",
        "Bereikbaarheid arbeidsplaatsen voor inwoners",
        "Potentie bereikbaarheid voor bedrijven en instellingen",
        "Concurrentiepositie voor bereik arbeidsplaatsen",
        "Concurrentiepositie voor bedrijven qua bereikbaarheid",
    )

    def __init__(self):
        super().__init__()
        self.title("IKOB Runner")
        self._checks = [BooleanVar(value=True) for _ in self.stappen]
        self._configvar = StringVar()
        self.run_button = None
        self.create_widgets()

    def create_widgets(self):
        self.widgets: list[Widget] = []

        frame = Frame()
        frame.pack(expand=1, fill="both", padx=self.PAD_X, pady=self.PAD_Y)

        self.widgets.extend(widgets.pathWidget(frame, "Project", self._configvar, file=True))
        self.widgets.append(frame)

        labels = [stap for stap in self.stappen]
        self.widgets.extend(widgets.checklistWidget(frame, "Stappen", labels, self._checks, row=1, itemsperrow=1))

        button = Button(master=frame, text="Start", command=lambda: threading.Thread(target=self.run_cmd).start())
        button.grid(row=2, column=2, sticky="ew", padx=self.PAD_X, pady=self.PAD_Y)
        self.run_button = button
        self.widgets.append(button)

    def run_cmd(self):
        project_file = self._configvar.get()

        # Skip the test when its _not_ selected.
        skip_steps = [not check.get() for check in self._checks]

        # Disable the run button while the scripts are running
        # to prevent users launching many run_scripts instances.
        if self.run_button is None:
            raise ValueError("attempt to disable run button, but run button is None.")
        self.run_button.configure(state="disabled")

        try:
            run_scripts(project_file, skip_steps, write_weights=False)
        except BaseException as err:
            msg = f"An error occurred: {err}"
            messagebox.showerror(title="FOUT", message=msg)
        else:
            msg = "Alle stappen zijn succesvol uitgevoerd."
            messagebox.showinfo(title="Gereed", message=msg)

        # After success/error the run button can be re-enabled.
        self.run_button.configure(state="active")

    def cmdLaadProject(self):
        filename = filedialog.askopenfilename(
            title="Kies een .json project bestand.",
            filetypes=[("project file", ".json")],
        )
        if filename:
            try:
                _ = load_config(filename)
            except ValueError:
                messagebox.showerror(
                    title="Fout",
                    message="Het bestand bevat geen geldige configuratie.",
                )
            except IOError:
                messagebox.showerror(title="Fout", message="Het bestand kan niet worden geladen.")


def main():
    parser = argparse.ArgumentParser(prog="ikobrunner", description="Launch the IKOB runner GUI.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display logging messages over stdout.",
    )
    parser.add_argument(
        "-p",
        "--project",
        help="Optional path to the project to execute. No Gui is shown if provided, and every ikob step is executed.",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s \t -  %(message)s"
        )
    if not args.project:
        App = ConfigApp()
        App.mainloop()
    else:
        try:
            run_scripts(args.project)
        except BaseException:
            logger.error(traceback.format_exc())
        else:
            logger.info("Alle steps successfully executed.")


if __name__ == "__main__":
    main()
