import subprocess
import sys
import os
from tkinter import *
from tkinter import filedialog, messagebox
from config import widgets
from ConfigurationDefinition import *
from ikobconfig import loadConfig


pythonexe = sys.executable
steps = (
  ("Calculated generalised (experienced) travel time from time and costs", "Generalisedtimecalculation"),
  ("Distribution of groups over the neighbourhoods or zones", "Distributionofgroups"),
  ("Weights for single modalities with travel time decay functions", "Weightsingle"),
  ("Maximum weights over combination of modalities", "Weightcombis"),
  ("Accessibility deployment possibilities for inhabitants", "Deployment"),
  ("Potency for accessibility for companies and institutions", "Potentialcompanies"),
  ("Competitiveness for people in accessibility of deployment", "Competitionforjobs"),
  ("Competitiveness for companies and institutions in accessibility for people", "Competitionforpeople")
)

PAD = {'padx': 5, 'pady': 5}
IPAD = {'ipadx': 5, 'ipady': 5 }

### User interface

class ConfigApp(Tk):
  def __init__(self):
    super().__init__()
    self.title('IKOB Runner')
    self._project = ''
    self._checks = [BooleanVar(value=True) for _ in steps]
    self._configvar = StringVar()
    self.create_widgets()
    python_filename = os.path.splitext(os.path.basename(pythonexe))[0]
    script_filename = os.path.splitext(os.path.basename(__file__))[0]
    if python_filename == script_filename:
      # exe mode
      self.runmode = 'exe'
    else:
      # python mode
      self.runmode = 'py'



  def create_widgets(self):
    self.widgets = []
    F1 = Frame()
    F1.pack(expand=1, fill="both", **PAD)
    self.widgets.extend(widgets.pathWidget(F1, "Project", self._configvar, file=True))
    self.widgets.append(F1)
    labels = [ x[0] for x in steps ]
    self.widgets.extend(widgets.checklistWidget(F1, "Steps", labels, self._checks, row=1, itemsperrow=1))
    B = Button(master=F1, text='Start', command=self.cmdRun)
    B.grid(row=2, column=2, sticky='ew', **PAD)
    self.widgets.append(B)

  def cmdRun(self):
    self._project = self._configvar.get()
    thisscript = os.path.realpath(__file__)
    scriptdir = os.path.dirname(thisscript)
    try:
      for i, stap in enumerate(steps):
        if self._checks[i].get():
          print(f'Uitvoeren van stap: {stap[0]}.')
          script = os.path.join(scriptdir, f'{stap[1]}.{self.runmode}')
          print (script)
          if self.runmode == 'exe':
            result = subprocess.call(f'\"{script}\" \"{self._project}\"', shell=True)
          else:
            result = subprocess.call(f'\"{pythonexe}\" \"{script}\" \"{self._project}\"', shell=True)
          if result!=0:
            messagebox.showerror(title='ERROR', message=f'Python rised error code: {result} in step {stap[0]}.')
            return
        else:
          print(f'Step {stap[0]} is skipped.')
    except BaseException as err:
      messagebox.showerror(title='ERROR', message=f'ERROR in Step {stap[0]}: {err}')
    else:
      messagebox.showinfo(title='Finished', message='All steps are executed successfully.')

  def cmdLaadProject(self):
    filename = filedialog.askopenfilename(title='Choose a .json file.', filetypes=[('project file', '.json')])
    if filename:
      try:
        read_config = loadConfig(filename)
      except ValueError:
        messagebox.showerror(title='ERROR', message=f'The file contains no valid configuration.')
      except IOError:
        messagebox.showerror(title='ERROR', message=f'The file cannot be loaded.')


### Main
def main():
  App = ConfigApp()
  App.mainloop()


if __name__ == '__main__':
  main()