
from tkinter import *
from tkinter import ttk
from ikob.config.widgets import *

### Buid a config dictionary from the template

def _empty_value(valtype):
  if valtype == 'number':
    return 0
  elif (valtype == 'text'
    or valtype == 'file'
    or valtype == 'directory'
    or valtype == 'choice'):
      return ''
  elif valtype == 'check':
    return False
  elif valtype == 'checklist':
    return []
  return None

def _default_value(leaf):
  if 'default' in leaf:
    return leaf['default']
  elif leaf['type'] == 'choice':
    return leaf['items'][0]
  else:
    return _empty_value(leaf['type'])

def _get_value(leaf):
  value = None
  if 'tkvar' in leaf:
    valtype = leaf['type']
    valvar = None
    valitems = None
    if 'tkvar' in leaf:
      valvar = leaf['tkvar']
    if 'items' in leaf:
      valitems = leaf['items']
    if valtype == 'checklist':
      value = []
      for i, var in enumerate(valvar):
        if var.get():
          value.append(valitems[i])
    else:
      value = valvar.get()
  else:
    value = _default_value(leaf)
  return value

def buildConfigDict(template):
  """
  Bouw een configuratie dictionary vanuit een definitie
  structuur (eventueel met TkVariablen).
  """
  config = {}
  for key in set(template.keys()):
    if key != 'label':
      if type(template[key]) == dict:
        if 'type' in template[key]:
          config[key] = _get_value(template[key])
        else:
          config[key] = buildConfigDict(template[key])
      else:
        config[key] = template[key]
  return config


def addTkVarsTemplate(template):
  """
  Voeg tkvars toe aan een template
  """
  for key in set(template.keys()):
    if key != 'label':
      if type(template[key]) == dict:
        if 'type' in template[key]:
          var = None
          leaf = template[key]
          valtype = leaf['type']
          if valtype == 'number':
            var = DoubleVar(value=_default_value(leaf))
          elif (valtype == 'text'
            or valtype == 'file'
            or valtype == 'directory'
            or valtype == 'choice'):
              var = StringVar(value=_default_value(leaf))
          elif valtype == 'checkbox':
            var = BooleanVar(value=_default_value(leaf))
          elif valtype == 'checklist':
            deflist = _default_value(leaf)
            var = [ BooleanVar(value=(item in deflist)) for item in leaf['items']]
          if var:
            template[key]['tkvar'] = var
          else:
            print(f'FOUT? template[{key}] = {leaf}')
        else:
          addTkVarsTemplate(template[key])


def setTkVars(template, config):
  """
  Plaats the waarden van een configuratie in in TkVariablen.
  """
  for key in template:
    if key in config:
      if type(config[key]) is dict:
        setTkVars(template[key], config[key])
      else:
        if 'type' in template[key]:
          valtype = template[key]['type']
          if valtype == 'checklist':
            values = config[key]
            for i, item in enumerate(template[key]['items']):
              template[key]['tkvar'][i].set(item in values)
          else:
            template[key]['tkvar'].set(config[key])
    else:
      # TODO: handle missing key?
      pass


def _addWidgets(master, template):
  widgets = []
  row = 0
  for key in template:
    if key != 'label':
      if type(template[key]) == dict:
        if 'type' in template[key]:
          leaf = template[key]
          vartype = leaf['type']
          label = key
          unit = ''
          items = []
          if 'label' in leaf:
            label = leaf['label']
          if 'unit' in leaf:
            unit = leaf['unit']
          if 'items' in leaf:
            items = leaf['items']
          var = leaf['tkvar']
          if vartype == 'number':
            widgets.extend(numberWidget(master, label, unit, var, row=row))
          elif vartype == 'text':
            widgets.extend(textWidget(master, label, var, row=row))
          elif vartype == 'file':
            widgets.extend(pathWidget(master, label, var, row=row, file=True))
          elif vartype == 'directory':
            widgets.extend(pathWidget(master, label, var, row=row))
          elif vartype == 'choice':
            widgets.extend(choiceWidget(master, label, items, unit, var, row=row))
          elif vartype == 'checkbox':
            widgets.extend(checkboxWidget(master, label, var, row=row))
          elif vartype == 'checklist':
            widgets.extend(checklistWidget(master, label, items, var, row=row))
          else:
            dummy = Label(master=master, text="Dummy")
            dummy.grid(row=row, column=0)
            widgets.append(dummy)
          row = row + 1
        else:
          label = key
          if 'label' in template[key]:
            label = template[key]['label']
          frame = LabelFrame(master=master, text=label, borderwidth=2)
          frame.columnconfigure((1), weight=1)
          frame.grid(row=row, column=0, columnspan=3, sticky='ew', **PAD)
          widgets.append(frame)
          _addWidgets(frame, template[key])
          row = row + 1
  return widgets

def buildTkInterface(root, tkvartemplate, cmdNew=None, cmdLoad=None, cmdSave=None):
  notebook = ttk.Notebook(root)
  widgets = [ notebook ]
  for key in tkvartemplate:
    if type(tkvartemplate[key]) == dict:
      tab = ttk.Frame(notebook)
      tab.columnconfigure((1), weight=1)
      label = key
      if 'label' in tkvartemplate[key]:
        label = tkvartemplate[key]['label']
      notebook.add(tab, text=label)
      widgets.append(tab)
      widgets.extend(_addWidgets(tab, tkvartemplate[key]))
  notebook.pack(expand=True, fill="both")
  # Add load/save/new buttons.
  BF = Frame()
  BF.pack(expand=True, fill=X, ipadx=5, ipady=5)
  BS = Button(master=BF, text='Opslaan ...', command=cmdSave)
  BS.pack(side=RIGHT, padx=10, ipadx=10)
  BL = Button(master=BF, text='Laden ...', command=cmdLoad)
  BL.pack(side=LEFT, padx=10, ipadx=10)
  BN = Button(master=BF, text='Nieuw', command=cmdNew)
  BN.pack(side=LEFT, padx=10, ipadx=10)
  widgets.extend([BF, BS, BL, BN])
  return widgets
