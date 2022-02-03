import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

PAD = {'padx': 5, 'pady': 5}
IPAD = {'ipadx': 5, 'ipady': 5 }

def textWidget(master, label, var, row=0):
  L = Label(master=master, text=f'{label}:')
  L.grid(row=row, column=0, sticky='w', **PAD)
  E = Entry(master=master, textvariable=var, width=40)
  E.grid(row=row, column=1, columnspan=2, sticky='ew', **PAD)
  return [L, E]


def numberWidget(master, label, unit, var, row=0):
  L = Label(master=master, text=f'{label}:')
  L.grid(row=row, column=0, sticky='w', **PAD)
  E = Entry(master=master, textvariable=var, justify=RIGHT)
  E.grid(row=row, column=1, sticky='ew', **PAD)
  U = Label(master=master, text=f'{unit}')
  U.grid(row=row, column=2, sticky='w', **PAD)
  return [L, E]


def checkboxWidget(master, label, var, row=0, column=0, cspan=3):
  C = Checkbutton(master=master, text=label, variable=var)
  C.grid(row=row, column=column, columnspan=cspan, sticky='w', padx=8)
  return [C]


# Hold a 'sane' start if we have no idea what to pick.
_LastDir = os.getcwd()
_LastFile = os.getcwd()

def _browseFile(var):
  global _LastFile
  initpath = _LastFile
  if len(var.get()) > 0:
    initpath = var.get()
  selectedfile = filedialog.askopenfilename(initialdir=initpath, title='Kies een bestand.')
  if selectedfile:
    var.set(selectedfile)
    _LastFile = selectedfile
  

def _browseDir(var):
  global _LastDir
  initpath = _LastDir
  if len(var.get()) > 0:
    initpath = var.get()
  selectedpath = filedialog.askdirectory(initialdir=initpath, title='Kies een directory')
  if selectedpath:
    var.set(selectedpath)
    _LastDir = selectedpath


def pathWidget(master, label, var, row=0, file=False):
  L = Label(master=master, text=f'{label}:')
  L.grid(row=row, column=0, sticky='w', **PAD)
  E = Entry(master=master, textvariable=var, width=40)
  E.grid(row=row, column=1, sticky='ew', **PAD)
  if file:
    B = Button(master=master, text='...', command=lambda:_browseFile(var))
  else:
    B = Button(master=master, text='...', command=lambda:_browseDir(var))
  B.grid(row=row, column=2, sticky='ew', **PAD)
  return [ L, E, B ]


def checklistWidget(master, label, items, vars, row=0):
  F = LabelFrame(master=master, text=label, borderwidth=2, padx=5)
  F.grid(row=row, column=0, columnspan=3, sticky='ew', **PAD)
  w = [ F ]
  for i, item in enumerate(items):
     w.extend(checkboxWidget(F, item, vars[i], row=int(i/4), column=i%4, cspan=1))
  return w


def choiceWidget(master, label, items, unit, var, row=0):
  L = Label(master=master, text=f'{label}:')
  L.grid(row=row, column=0, sticky='w', **PAD)
  CB = ttk.Combobox(master = master, textvariable=var)
  CB.config(values=items)
  CB.grid(row=row, column=1, sticky='ew', **PAD)
  if len(items)>0 and len(var.get())==0:
    var.set(items[0])
  U = Label(master=master, text=f'{unit}')
  U.grid(row=row, column=2, sticky='w', **PAD)
  return [ L, CB ]


def optionalFileWidget(master, label, checklabel, filelabel, checkvar, filevar, row=0):
  F = LabelFrame(master=master, text=label, borderwidth=2, padx=5)
  F.grid(row=row, column=0, columnspan=3, sticky='ew', **PAD)
  w = [ F ]
  w.extend(checkboxWidget(F, checklabel, checkvar, row=0))
  w.extend(pathWidget(F, filelabel, filevar, row=1, file=True))
  return w

if __name__ == '__main__':
  """
  Test code
  """
  def sel():
    selection = "You selected the option " + str(var.get())
    label.config(text = selection)

  root= Tk()
  widgets = []

  N1 = ttk.Notebook(root)
  T1 = ttk.Frame(N1)
  N1.add(T1, text='Tab 1')
  
  var = IntVar()

  F1 = LabelFrame(master=T1, text="Frame", borderwidth=4)
  widgets.append(F1)
  R1 = Radiobutton(F1, text="Option 1", variable=var, value=12,
                    command=sel)
  widgets.append(R1)
  R2 = Radiobutton(F1, text="Option 2", variable=var, value=34,
                    command=sel)
  widgets.append(R2)
  R3 = Radiobutton(F1, text="Option 3", variable=var, value=56,
                    command=sel)
  widgets.append(R3)
  label = Label(F1, text="You selected the option 00")
  widgets.append(label)

  for i in widgets:
    i.pack(anchor=W, **PAD)


  T2 = ttk.Frame(N1)
  N1.add(T2, text='Tab 2')

  var2 = StringVar()
  widgets.extend(textWidget(T2, 'Name', var2, row=0))
  var3 = DoubleVar()
  widgets.extend(numberWidget(T2, 'Number', 'm/s', var3, row=1))
  var4 = BooleanVar()
  widgets.extend(checkboxWidget(T2, "Check this.", var4, row=4))

  T3 = ttk.Frame(N1)
  N1.add(T3, text='Tab 3')

  var5 = StringVar()
  widgets.extend(pathWidget(T3, 'Path', var5, row=0))
  var6 = StringVar()
  widgets.extend(pathWidget(T3, 'File', var6, row=1, file=True))

  vars7 = [ BooleanVar(), BooleanVar(), BooleanVar() ]
  items = [ 'Check Item 1', 'Check Item 2', 'Check Item 3' ]
  widgets.extend(checklistWidget(T3, 'Check Items', items, vars7, row=2))

  var8 = StringVar()
  items = [ 'Option 1', 'Option 2', 'Option 3' ]
  widgets.extend(choiceWidget(T3, 'Pick one.', items, 'unit', var8, row=3))

  var9 = BooleanVar()
  var10 = StringVar()
  widgets.extend(optionalFileWidget(T3, 'Feature', 'Generate Data', 'Stored Data', var9, var10, row=4))

  N1.pack(expand=1, fill="both")

  root.mainloop()
