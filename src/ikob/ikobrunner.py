import argparse
import logging
import sys
import threading
import traceback
from tkinter import BooleanVar, Button, Frame, StringVar, Tk, Widget, messagebox

from ikob.combined_weights import calculate_combined_weights
from ikob.competition import competition_on_citizens, competition_on_jobs
from ikob.datasource import DataSource, DataType
from ikob.deployment_opportunities import deployment_opportunities
from ikob.distribute_over_groups import distribute_over_groups
from ikob.generalized_travel_time import generalized_travel_time
from ikob.gui.widget_factory import WidgetFactory
from ikob.ikobconfig import get_config_from_args
from ikob.potential_companies import potential_companies
from ikob.single_weights import calculate_single_weights

logger = logging.getLogger(__name__)


def run_scripts(project_file, skip_steps: list[bool] | None = None, write_weights: bool = False):
    """
    Run through all steps for a given project.

    Args:
        project_file: the path to a JSON project config
        skip_steps: a list of bools to skip that index step
        write_weights: skip writing out weights results
    """
    logger.info("Reading project file: %s.", project_file)
    config = get_config_from_args(project_file)

    logger.info("Starting simulations...")
    if not skip_steps:
        skip_steps = [False] * 8

    if not skip_steps[0]:
        travel_time = generalized_travel_time(config)
    else:
        travel_time = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME)

    if not skip_steps[1]:
        # TODO: Pass temporary SEGS output as arguments too.
        distribute_over_groups(config)

    if not skip_steps[2]:
        single_weights = calculate_single_weights(config, travel_time)
    else:
        single_weights = DataSource(config, DataType.WEIGHTS)

    if not skip_steps[3]:
        combined_weights = calculate_combined_weights(config, single_weights)
    else:
        combined_weights = DataSource(config, DataType.WEIGHTS)

    if not skip_steps[4]:
        possibilities = deployment_opportunities(config, single_weights, combined_weights)
    else:
        possibilities = DataSource(config, DataType.DESTINATIONS)

    if not skip_steps[5]:
        origins = potential_companies(config, single_weights, combined_weights)
    else:
        origins = DataSource(config, DataType.ORIGINS)

    if not skip_steps[6]:
        competition_jobs = competition_on_jobs(config, single_weights, combined_weights, origins)
    else:
        competition_jobs = DataSource(config, DataType.COMPETITION)

    if not skip_steps[7]:
        competition_citizens = competition_on_citizens(config, single_weights, combined_weights, possibilities)
    else:
        competition_citizens = DataSource(config, DataType.COMPETITION)

    logger.info("All simulations are completed.")

    # TODO: For now all files are written to disk to assert their contents in
    # end-to-end testing. Ultimately only files that are essential outputs
    # should persist.
    logger.info("Writing output to disk...")
    sources_to_save = [travel_time, possibilities, origins, competition_citizens, competition_jobs]
    if write_weights:
        sources_to_save.extend([single_weights, combined_weights])

    for container in sources_to_save:
        container.store()


# User interface


class ConfigApp(Tk):
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
        self.widget_factory = WidgetFactory()
        self.run_button = None
        self.create_widgets()

    def create_widgets(self):
        self.widgets: list[Widget] = []

        frame = Frame()
        frame.pack(
            expand=1,
            fill="both",
            padx=self.widget_factory.PADX,
            pady=self.widget_factory.PADY,
        )

        self.widgets.extend(self.widget_factory.path_widget(frame, "Project", self._configvar, file=True))
        self.widgets.append(frame)

        labels = [stap for stap in self.stappen]
        self.widgets.extend(
            self.widget_factory.checklist_widget(frame, "Stappen", labels, self._checks, row=1, items_per_row=1)
        )

        button = Button(master=frame, text="Start", command=lambda: threading.Thread(target=self.run_cmd).start())
        button.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=self.widget_factory.PADX,
            pady=self.widget_factory.PADY,
        )
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
            logger.error(traceback.format_exc())
            messagebox.showerror(title="FOUT", message=msg)
        else:
            msg = "Alle stappen zijn succesvol uitgevoerd."
            messagebox.showinfo(title="Gereed", message=msg)

        # After success/error the run button can be re-enabled.
        self.run_button.configure(state="active")


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

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s \t -  %(message)s",
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
