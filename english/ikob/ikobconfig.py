import argparse
import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from config import *
from ConfigurationDefinition import *

### Interface: load/save config files.

def _projectFilename(projectname, make_safe = True):
  """
  Suggest a filename bases on the project name created
  by the user.
  """
  filename, ext = os.path.splitext(projectname)
  if ext != '.json':
    filename = projectname
  if make_safe:
    filename = re.sub(r'[^\w\s]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
  return filename+".json"


def getConfigFromArgs():
  """
  Reads a configuration file as specified in the 'command line'.
  Results: A valid, loaded configuration.
  Errors: IOError - If the specified file does not exist or cannor be opened.
          ValueError - If the specified file has no valid configuration.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('project', type=str, help='Het .json project bestand.')
  args = parser.parse_args()
  return loadConfig(args.project)


def loadConfig(filename):
  config = None
  try:
    with open(filename) as json_file:
      config = json.load(json_file)
  except:
    raise IOError(f'Cannot read from: {filename}.')
  if config:
    if not validateConfiguration(config):
      raise ValueError('Configuration has an incompatible format.')
    config['__filename__'] = os.path.splitext(os.path.basename(filename))[0]
  return config


def saveConfig(filename, config):
  try:
    with open(filename, 'w') as json_file:
      json.dump(config, json_file, indent = 2)
  except:
    raise IOError(f'Cannot save configuration to: {filename}.')
  return True

### User interface

class ConfigApp(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title('IKOB configuration')
    self.add_variables()
    self.create_widgets()

  def add_variables(self):
    self._template = DefaultConfigurationDefinition()
    build.addTkVarsTemplate(self._template)

  def create_widgets(self):
    self._widgets = build.buildTkInterface(self, self._template,
      cmdNew = self.cmdNewProject,
      cmdLoad = self.cmdLoadProject,
      cmdSave = self.cmdSaveProject)

  def cmdNewProject(self):
    build.setTkVars(self._template, DefaultConfiguration())

  def cmdLoadProject(self):
    filename = filedialog.askopenfilename(title='Choose a .json project file.', filetypes=[('project file', '.json')])
    if filename:
      try:
        read_config = loadConfig(filename)
      except ValueError:
        messagebox.showerror(title='error', message=f'The file has no valid configuration.')
      except IOError:
        messagebox.showerror(title='error', message=f'The file cannot be loaded.')
      else:
        build.setTkVars(self._template, read_config)

  def cmdSaveProject(self):
    config = build.buildConfigDict(self._template)
    filename = filedialog.asksaveasfilename(title='Choose a .json project file name.',
                                            initialfile=_projectFilename(projectName(config)),
                                            filetypes=[('project file', '.json')])
    filename = _projectFilename(filename, make_safe=False)
    try:
      saveConfig(filename, config)
    except:
      messagebox.showerror(title='Error', message=f'The file cannot be saved.')
    else:
      messagebox.showinfo(title='Saved', message=f'Configuration saved.')

### Main

def main():
  #homedir = os.path.expanduser('~/')
  #print(f'Home dir = {homedir}')
  if not validate.validateTemplate(DefaultConfigurationDefinition()):
    messagebox.showerror(title='Error', message='The Default ConfigurationDefinition is not valid: Inspect ConfigurationDefinition.py')
    exit(1)
  App = ConfigApp()
  App.mainloop()


if __name__ == '__main__':
  main()