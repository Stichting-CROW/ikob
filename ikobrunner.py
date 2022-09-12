import subprocess
import sys
import os
from tkinter import *
from tkinter import filedialog, messagebox
from config import widgets
from ConfiguratieDefinitie import *
from ikobconfig import loadConfig


pythonexe = sys.executable
stappen = (
  ("Ervaren reistijd berekenen uit tijd en kosten", "skimsberekenen"),
  ("Verdeling van de groepen over de buurten of zones", "Verdelingovergroepen"),
  ("Gewichten (reistijdvervalscurven) voor auto, OV, fiets en E-fiets apart", "Gewichtenberekenenenkelscenarios"),
  ("Maximum gewichten van meerdere modaliteiten", "Gewichtenberekenencombis"),
  ("Bereikbaarheid arbeidsplaatsen voor inwoners", "Ontplooiingsmogelijkhedenechteinwoners"),
  ("Potentie bereikbaarheid voor bedrijven en instellingen", "Potentiebedrijven"),
  ("Concurrentiepositie voor bereik arbeidsplaatsen", "Concurrentieomarbeidsplaatsen"),
  ("Concurrentiepositie voor bedrijven qua bereikbaarheid", "Concurrentieominwoners")
)

PAD = {'padx': 5, 'pady': 5}
IPAD = {'ipadx': 5, 'ipady': 5 }

### User interface

class ConfigApp(Tk):
  def __init__(self):
    super().__init__()
    self.title('IKOB Runner')
    self._project = ''
    self._checks = [BooleanVar(value=True) for _ in stappen]
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
    labels = [ x[0] for x in stappen ]
    self.widgets.extend(widgets.checklistWidget(F1, "Stappen", labels, self._checks, row=1, itemsperrow=1))
    B = Button(master=F1, text='Start', command=self.cmdRun)
    B.grid(row=2, column=2, sticky='ew', **PAD)
    self.widgets.append(B)

  def cmdRun(self):
    self._project = self._configvar.get()
    thisscript = os.path.realpath(__file__)
    scriptdir = os.path.dirname(thisscript)
    try:
      for i, stap in enumerate(stappen):
        if self._checks[i].get():
          print(f'Uitvoeren van stap: {stap[0]}.')
          script = os.path.join(scriptdir, f'{stap[1]}.{self.runmode}')
          if self.runmode == 'exe':
            result = subprocess.call(f'{script} \"{self._project}\"', shell=True)
          else:
            result = subprocess.call(f'{pythonexe} {script} \"{self._project}\"', shell=True)
          if result!=0:
            messagebox.showerror(title='FOUT', message=f'Python gaf fout code: {result} in stap {stap[0]}.')
            return
        else:
          print(f'Stap {stap[0]} wordt overgeslagen.')
    except BaseException as err:
      messagebox.showerror(title='FOUT', message=f'Fout in Stap {stap[0]}: {err}')
    else:
      messagebox.showinfo(title='Gereed', message='Alle stappen zijn succesvol uitegevoerd.')

  def cmdLaadProject(self):
    filename = filedialog.askopenfilename(title='Kies een .json project bestand.', filetypes=[('project file', '.json')])
    if filename:
      try:
        read_config = loadConfig(filename)
      except ValueError:
        messagebox.showerror(title='Fout', message=f'Het bestand bevat geen geldige configuratie.')
      except IOError:
        messagebox.showerror(title='Fout', message=f'Het bestand kan niet worden geladen.')


### Main
def main():
  App = ConfigApp()
  App.mainloop()


if __name__ == '__main__':
  main()