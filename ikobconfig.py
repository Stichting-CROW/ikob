import argparse
import json
import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

DAGSOORTEN = [ 'Ochtendspits', 'Restdag', 'Avondspits' ]
MOTIEVEN = [ 'werk', 'overig' ]
ASPECTEN = [ 'Tijd', 'Kosten' ]

def defaultConfig():
  """
  Dit is de standaard configuratie zoals gebruikt door IKOB
  """
  return {
    'projectnaam': 'Project 1',
    'paden': {
      'invoer_skims_directory': 'skims',
      'uitvoer_directory': 'uitvoer'
    },
    'skims': {
      'benader_kosten': True,
      'dagsoort': DAGSOORTEN,
      'motieven': MOTIEVEN,
      'aspect': ASPECTEN,
      'TVOMwerk': {
        'hoog': 4,
        'middelhoog': 6,
        'middellaag': 9,
        'laag': 12
      },
      'TVOMoverig': {
        'hoog': 4.8,
        'middelhoog': 7.25,
        'middellaag': 10.9,
        'laag': 15.5
      },
      'varkosten': 0.16,
      'kmheffing': 0,
      'varkostenga': {
        'GeenAuto': 0.33,
        'GeenRijbewijs': 2.40
      },
      'tijdkostenga': {
        'GeenAuto': 0.01,
        'GeenRijbewijs': 0.40
      }
    }
  }


def getConfigFromArgs():
  """
  Reads the filename from script command-line and loads a config.
  Returns: A valid config dictionary.
  Throws: IOError if file could not be loaded, or 
          ValueError if the content is not a valid config.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('project', type=str, help='Het .json project bestand.')
  args = parser.parse_args()
  config = loadConfig(_projectFilename(args.project))
  if config:
    if not validateConfig(config):
      raise ValueError('Config has an incompatible format.')
  return config


def loadConfig(filename = 'defaults.json'):
  config = None
  try:
    with open(filename) as json_file:
      config = json.load(json_file)
  except:
    raise IOError(f'Could not read: {filename}.')
  return config


def saveConfig(filename, config):
  try:
    with open(filename, 'w') as json_file:
      json.dump(config, json_file, indent = 2)
  except:
    raise IOError(f'Could not write: {filename}.')
  return True


def _validateDict(this_dict, other_dict, strict = True):
  """
  Validate this_dict against other_dict by comparing keys and types.
  Optional: strict = True, requires both key sets to be exactly equal. 
            strict = False, allows _only_ this_dict to have additional keys.
  Returns True if both dicts contain the same keys (recursively)
  and all their values are of the same type.
  Note: Contents of lists are not checked.
  """
  if strict and set(this_dict.keys()) != set(other_dict.keys()):
    return False
  for key in set(other_dict.keys()):
    if not strict:
      if not key in this_dict:
        return False
    if type(this_dict[key]) != type(other_dict[key]):
      return False
    if type(this_dict[key]) is dict:
      return _validateDict(this_dict[key], other_dict[key], strict = strict)
  return True


def validateConfig(config, strict = True):
  """
  Validate if the config dict has all the (default) items.
  """
  return _validateDict(config, defaultConfig(), strict = strict)

def _projectFilename(projectname, make_safe = True):
  filename, ext = os.path.splitext(projectname)
  if ext != '.json':
    filename = projectname
  if make_safe:
    filename = re.sub(r'[^\w\s]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
  return filename+".json"

def _checkOptionList(master, text, items, variables, b_opts={}, i_opts={'padx':5}):
  frm_border = ttk.LabelFrame(master=master, text=text, borderwidth=2, **b_opts)
  for i,item in enumerate(items):
    ttk.Checkbutton(master=frm_border, text=item, variable=variables[i]).grid(row=i, column=0, sticky='nw', **i_opts)
  return frm_border

def _toItemList(tkvars, valueset):
  itemlist = []
  for i, item in enumerate(valueset):
    if tkvars[i].get():
      itemlist.append(item)
  return itemlist

def _fromItemList(tkvars, itemlist, valueset):
  for i, item in enumerate(valueset):
    tkvars[i].set(False)
    if item in itemlist:
      tkvars[i].set(True)
  return


class ConfigApp(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title('IKOB config')
    #self.geometry('300x80')

    # TK variablen
    self.projectname_var = tk.StringVar()
    self.skimsdirectory_var = tk.StringVar()
    self.outputdirectory_var = tk.StringVar()
    self.benader_kosten_var = tk.BooleanVar()
    self.dagsoort_vars = [tk.BooleanVar() for _ in DAGSOORTEN]
    self.motief_vars = [tk.BooleanVar() for _ in MOTIEVEN]
    self.aspect_vars = [tk.BooleanVar() for _ in ASPECTEN]
    # Vul variabelen met data
    self._config = defaultConfig()
    self._set_config()
    # GUI layout
    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=1)
    self.columnconfigure(2, weight=1)
    self.create_widgets()


  def cmd_browse(self, sv):
    initpath = os.getcwd()
    if len(sv.get()) > 0:
      initpath = sv.get()
    selectedpath = filedialog.askdirectory(initialdir = initpath, title = "Selecteer directory")
    if selectedpath:
      sv.set(selectedpath)

  def create_widgets(self):
    """
    Create the widgets layout for the config UI.
    """
    # universal grid padding
    padding = {'padx': 5, 'pady': 5}
    ipadding = {'ipadx': 5, 'ipady':5}

    # project name area
    frm_project = ttk.LabelFrame(text='Project', borderwidth=2)
    frm_project.pack(fill=tk.X, side=tk.TOP, expand=True, **padding)
    lbl_projectname = ttk.Label(master=frm_project, text='Project Naam:')
    ent_projectname = ttk.Entry(master=frm_project, textvariable=self.projectname_var, width=50)
    lbl_projectname.grid(row=0, column=0, sticky='e', **padding)
    ent_projectname.grid(row=0, column=1, sticky='ew', **padding)

    # 'paden' config area
    lbl_skimdir = ttk.Label(master=frm_project, text='Skims directory:')
    ent_skimdir = ttk.Entry(master=frm_project, textvariable=self.skimsdirectory_var, width=50)
    btn_skimdir_browse = ttk.Button(master=frm_project, text='Browse ...', command=lambda:self.cmd_browse(self.skimsdirectory_var))
    lbl_skimdir.grid(row=1, column=0, sticky='e', **padding)
    ent_skimdir.grid(row=1, column=1, **padding)
    btn_skimdir_browse.grid(row=1, column=2, sticky='ew', **padding)
    lbl_outdir = ttk.Label(master=frm_project, text='Uitvoer directory:')
    ent_outdir = ttk.Entry(master=frm_project, textvariable=self.outputdirectory_var, width=50)
    btn_outdir_browse = ttk.Button(master=frm_project, text='Browse ...', command=lambda:self.cmd_browse(self.outputdirectory_var))
    lbl_outdir.grid(row=2, column=0, sticky='e', **padding)
    ent_outdir.grid(row=2, column=1, **padding)
    btn_outdir_browse.grid(row=2, column=2, sticky='ew', **padding)

    # 'skims' config area
    frm_skims = ttk.LabelFrame(text='Skims', borderwidth=2)
    frm_skims.pack(fill=tk.X, expand=True, **padding)

    # checkboxes: Dagsoort
    opt_dagsoort = _checkOptionList(master=frm_skims, text='Dagsoort', items=DAGSOORTEN, variables=self.dagsoort_vars)
    opt_dagsoort.pack(fill=tk.Y, side=tk.LEFT, **padding)
    # checkboxes: Motieven
    opt_motieven = _checkOptionList(master=frm_skims, text='Motieven', items=MOTIEVEN, variables=self.motief_vars)
    opt_motieven.pack(fill=tk.Y, side=tk.LEFT, **padding)
    # checkboxes: Aspecten
    opt_aspecten = _checkOptionList(master=frm_skims, text='Aspecten', items=ASPECTEN, variables=self.aspect_vars)
    opt_aspecten.pack(fill=tk.Y, side=tk.LEFT, **padding)

    # checkbox: Benader OV Kosten
    frm_misc = ttk.LabelFrame(master=frm_skims, text='Overig')
    frm_misc.pack(fill=tk.Y, side=tk.LEFT, **padding)
    chk_benaderen = ttk.Checkbutton(master=frm_misc, text="Benader OV Kosten", variable=self.benader_kosten_var)
    chk_benaderen.grid(row=0, column=0, sticky='w', **padding)

    # Advanced:


    # command buttons: NIEUW, LADEN, OPSLAAN
    frm_buttons = ttk.Frame()
    frm_buttons.pack(fill=tk.X, **ipadding)
    btn_saveproject = ttk.Button(master=frm_buttons, text='Opslaan ...', command=self.cmd_save_project)
    btn_saveproject.pack(side=tk.RIGHT, padx=10, ipadx=10)
    btn_loadproject = ttk.Button(master=frm_buttons, text='Laden ...', command=self.cmd_load_project)
    btn_loadproject.pack(side=tk.LEFT, padx=10, ipadx=10)
    btn_newproject = ttk.Button(master=frm_buttons, text='Nieuw', command=self.cmd_new_project)
    btn_newproject.pack(side=tk.LEFT, padx=10, ipadx=10)


  def _get_config(self):
    # Collect data from GUI elements and fill config
    self._config['projectnaam'] = self.projectname_var.get()
    self._config['paden']['invoer_skims_directory'] = self.skimsdirectory_var.get()
    self._config['paden']['uitvoer_directory'] = self.outputdirectory_var.get()
    self._config['skims']['dagsoort']=_toItemList(self.dagsoort_vars, DAGSOORTEN)
    self._config['skims']['motieven']=_toItemList(self.motief_vars, MOTIEVEN)
    self._config['skims']['aspect']=_toItemList(self.aspect_vars, ASPECTEN)
    self._config['skims']['benader_kosten']=self.benader_kosten_var.get()
    # TODO: Add rest

  def _set_config(self):
    self.projectname_var.set(self._config['projectnaam'])
    self.skimsdirectory_var.set(self._config['paden']['invoer_skims_directory'])
    self.outputdirectory_var.set(self._config['paden']['uitvoer_directory'])
    _fromItemList(self.dagsoort_vars, self._config['skims']['dagsoort'], DAGSOORTEN)
    _fromItemList(self.motief_vars, self._config['skims']['motieven'], MOTIEVEN)
    _fromItemList(self.aspect_vars, self._config['skims']['aspect'], ASPECTEN)
    self.benader_kosten_var.set(self._config['skims']['benader_kosten'])
    # TODO: Add rest

  def cmd_new_project(self):
    self._config = defaultConfig()
    self._set_config()

  def cmd_load_project(self):
    filename = filedialog.askopenfilename(title='Kies een .json project bestand.', filetypes=[('project file', '.json')])
    print(f'filename={filename}')
    if filename:
      try:
        self._config = loadConfig(filename)
      except:
        messagebox.showerror(title='Fout', message=f'Het bestand {filename} kan niet worden geladen.')
      else:
        if validateConfig(self._config):
          self._set_config()
        else:
          messagebox.showerror(title='Fout', message=f'Het bestand {filename} bevat geen geldige configuratie.')

  def cmd_save_project(self):
    self._get_config()
    filename = filedialog.asksaveasfilename(title='Kies een .json project bestand.',
                                            initialfile=_projectFilename(self._config['projectnaam']),
                                            filetypes=[('project file', '.json')])
    try:
      saveConfig(filename, self._config)
    except:
      messagebox.showerror(title='Fout', message=f'Het bestand {filename} kan niet worden opgeslagen.')
    else:
      messagebox.showinfo(title='Opgeslagen', message=f'Project configuratie suksesvol opgeslagen in {filename}.')


def main():
  homedir = os.path.expanduser('~/')
  print(f'Home dir = {homedir}')


if __name__ == '__main__':
  app = ConfigApp()
  app.mainloop()