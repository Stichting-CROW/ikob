#!/usr/bin/env python3
import argparse
import logging
import sys
import threading
from tkinter import BooleanVar, Button, Frame, StringVar, Tk, Widget, filedialog, messagebox

from ikob.combined_weights import calculate_combined_weights
from ikob.competition import assemble_competition_outputs, competition_on_citizens, competition_on_destinations
from ikob.config import widgets
from ikob.datasource import DataSource, DataType
from ikob.distribute_over_groups import distribute_population_over_groups
from ikob.generalized_travel_time import generalized_travel_time
from ikob.ikobconfig import get_config_from_args, load_config
from ikob.reachable_destinations import assemble_destination_outputs, calculate_reachable_destinations
from ikob.reachable_population import assemble_population_outputs, calculate_reachable_population
from ikob.single_weights import calculate_single_weights, calculate_single_weights_on_demand

logger = logging.getLogger(__name__)


def run_scripts(
    project_file,
    skip_steps: list[bool] | None = None,
    write_weights: bool = False,
    write_travel_time: bool = False,
    write_intermediate_results: bool = False,
):
    """
    Run through all steps for a given project.

    Process one income class through all selected stages before releasing its matrices.
    Assemble cross-income output tables from the retained result vectors afterwards.

    For details about the all the steps taken see documentation/IKOB-algorithm.pdf.
    In de docstring of each specific step the relevant section of the documentation is referenced.
    documentation/IKOB-documentation-partially-outdated.pdf is partially outdated, but might still provide some insight into the code.
    Do note that at the very least naming has changed and output is not written to disk after each step any more.

    Args:
        project_file: The path to a JSON project config
        skip_steps: A list of bools to skip that index step
        write_weights: Write out weights results (slow for large projects)
        write_travel_time: Write out travel time results (slow for large projects)
        write_intermediate_results: Write intermediate results so that a future run can continue on steps computed by this run.
                                    These intermediate results do not contain useful end results.
    """
    logger.info("Reading project file: %s.", project_file)
    config, valid = get_config_from_args(project_file)

    if not valid:
        raise ValueError("Invalid input files, see console warnings.")

    logger.info("Starting simulations...")
    if not skip_steps:
        skip_steps = [False] * 8

    if not skip_steps[1]:
        distribute_population_over_groups(config)

    reachable_destinations = DataSource(config, DataType.DESTINATIONS)
    reachable_population = DataSource(config, DataType.ORIGINS)
    competition_destinations = DataSource(config, DataType.COMPETITION)
    competition_citizens = DataSource(config, DataType.COMPETITION)

    # Run all steps for a particular income group before continuing with the next
    # This saves on memory usage since the matrices for one income group can be cleaned up when continuing with the next
    for income in ["laag", "middellaag", "middelhoog", "hoog"]:
        logger.info("Processing income class: %s", income)
        _run_income(
            config,
            income,
            skip_steps,
            reachable_destinations,
            reachable_population,
            competition_destinations,
            competition_citizens,
            write_weights=write_weights,
            write_travel_time=write_travel_time,
            write_intermediate_results=write_intermediate_results,
        )

    # Since we run the steps per income group, we cannot assemble results that combine income groups during the normal steps
    if not skip_steps[4]:
        assemble_destination_outputs(config, reachable_destinations)
    if not skip_steps[5]:
        assemble_population_outputs(config, reachable_population)
    if not skip_steps[6]:
        assemble_competition_outputs(config, competition_destinations, citizens=False)
    if not skip_steps[7]:
        assemble_competition_outputs(config, competition_citizens, citizens=True)

    logger.info("All simulations are completed. Writing output to disk...")
    for source in [reachable_destinations, reachable_population, competition_citizens, competition_destinations]:
        source.store(write_intermediate_results)
    DataSource.write_output_md(config)


def _run_income(
    config,
    income,
    skip_steps,
    reachable_destinations,
    reachable_population,
    competition_destinations,
    competition_citizens,
    *,
    write_weights,
    write_travel_time,
    write_intermediate_results,
):
    single_weights: DataSource | None = None
    if not skip_steps[0] and not skip_steps[2]:
        # Combine step 0 and 2 in one to avoid having intermediate results in memory if possible
        single_weights, travel_time = calculate_single_weights_on_demand(
            config, write_travel_time, selected_income=income
        )
    elif not skip_steps[0]:
        # if step 0 is not skipped, but step 2 is, compute the travel time as normal
        travel_time = generalized_travel_time(config, write_travel_time=write_travel_time, selected_income=income)
    else:
        # if step 0 is skipped as well, we create an empty data source that will read from disk
        travel_time = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME, has_zone_id_header=True)

    if skip_steps[2]:
        single_weights = DataSource(config, DataType.WEIGHTS, has_zone_id_header=True)
    elif skip_steps[0]:
        # if we do not skip step 2, but we did skip 0, then the travel time must be available
        # otherwise we cannot compute the single weights from the travel time result
        if travel_time is None:
            raise RuntimeError("Travel-time data is unavailable while step 0 is skipped.")
        single_weights = calculate_single_weights(config, travel_time, selected_income=income)

    if single_weights is None:
        raise RuntimeError("Single weights are unavailable for the selected pipeline steps.")

    if not skip_steps[3]:
        combined_weights = calculate_combined_weights(
            config, single_weights, write_weights=write_weights, selected_income=income
        )
    else:
        combined_weights = DataSource(config, DataType.WEIGHTS, has_zone_id_header=True)

    if not skip_steps[4]:
        calculate_reachable_destinations(
            config, single_weights, combined_weights, selected_income=income, results=reachable_destinations
        )

    if not skip_steps[5]:
        calculate_reachable_population(
            config, single_weights, combined_weights, selected_income=income, results=reachable_population
        )

    if not skip_steps[6]:
        competition_on_destinations(
            config,
            single_weights,
            combined_weights,
            reachable_destinations,
            selected_income=income,
            results=competition_destinations,
        )

    if not skip_steps[7]:
        competition_on_citizens(
            config,
            single_weights,
            combined_weights,
            reachable_population,
            selected_income=income,
            results=competition_citizens,
        )

    if write_weights:
        single_weights.store(write_intermediate_results)
        combined_weights.store(write_intermediate_results)
    if write_travel_time and travel_time is not None:
        travel_time.store(write_intermediate_results)


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
        except BaseException as err:  # noqa: BLE001
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
            except OSError:
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
        run_scripts(args.project)
        logger.info("Alle steps successfully executed.")


if __name__ == "__main__":
    main()
