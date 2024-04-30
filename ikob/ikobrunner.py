import subprocess
import pathlib
import sys
from tkinter import Tk, Frame, BooleanVar, StringVar
from tkinter import Button
from tkinter import filedialog, messagebox
from config import widgets

# from ConfiguratieDefinitie import *
from ikobconfig import loadConfig


# fmt: off
stappen = (
    ( "Gegeneraliseerde reistijd berekenen uit tijd en kosten", "Ervarenreistijdberekenen",),
    ( "Verdeling van de groepen over de buurten of zones", "Verdelingovergroepen"),
    ( "Gewichten (reistijdvervalscurven) voor auto, OV, fiets en E-fiets apart", "Gewichtenberekenenenkelscenarios",),
    ( "Maximum gewichten van meerdere modaliteiten", "Gewichtenberekenencombis"),
    ( "Bereikbaarheid arbeidsplaatsen voor inwoners", "Ontplooiingsmogelijkhedenechteinwoners",),
    ( "Potentie bereikbaarheid voor bedrijven en instellingen", "Potentiebedrijven"),
    ( "Concurrentiepositie voor bereik arbeidsplaatsen", "Concurrentieomarbeidsplaatsen",),
    ( "Concurrentiepositie voor bedrijven qua bereikbaarheid", "Concurrentieominwoners"),
)
# fmt: on

PAD = {"padx": 5, "pady": 5}
IPAD = {"ipadx": 5, "ipady": 5}


def run_mode(script_path):
    python_name = pathlib.Path(sys.executable).stem
    script_name = pathlib.Path(script_path).stem
    return "exe" if python_name == script_name else "py"


def run_scripts(project_file, skip_steps):
    """
    Run through all steps for a given project.
    Tests are skipped if skip_steps is set.
    Yields the current step and corresponding return code.
    """
    scriptdir = pathlib.Path(__file__).parent

    mode = run_mode(__file__)
    exe = sys.executable if mode == "py" else ""

    for stap, skip in zip(stappen, skip_steps):
        if skip:
            continue

        description, script = stap
        script = scriptdir.joinpath(f"{script}.{mode}")
        cmd = f"{exe} \"{script}\" \"{project_file}\""

        result = subprocess.run(cmd, shell=True, check=True)
        yield stap, result.returncode


# User interface


class ConfigApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("IKOB Runner")
        self._checks = [BooleanVar(value=True) for _ in stappen]
        self._configvar = StringVar()
        self.create_widgets()
        self.runmode = run_mode(__file__)

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
                if result != 0:
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
