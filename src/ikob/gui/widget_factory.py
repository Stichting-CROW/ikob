import os
import tkinter as tk
from tkinter import filedialog, ttk


class WidgetFactory:
    """Container for bunch of method that make various widgets for the gui.

    Not a util / stateless class because it keeps track of the last opened file / dir.
    """

    PADX = 5
    PADY = 5

    def __init__(self):
        self._last_dir = os.getcwd()
        self._last_file = os.getcwd()

    def text_widget(self, master, label_text: str, var, row=0) -> list[tk.Widget]:
        label = tk.Label(master=master, text=f"{label_text}:")
        label.grid(row=row, column=0, sticky="w", padx=self.PADX, pady=self.PADY)

        entry = tk.Entry(master=master, textvariable=var, width=40)
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", padx=self.PADX, pady=self.PADY)

        return [label, entry]

    def number_widget(self, master, label_text: str, unit_label_text: str, var, row=0) -> list[tk.Widget]:
        label = tk.Label(master=master, text=f"{label_text}:")
        label.grid(row=row, column=0, sticky="w", padx=self.PADX, pady=self.PADY)

        entry = tk.Entry(master=master, textvariable=var, justify=tk.RIGHT)
        entry.grid(row=row, column=1, sticky="ew", padx=self.PADX, pady=self.PADY)

        unit_label = tk.Label(master=master, text=f"{unit_label_text}")
        unit_label.grid(row=row, column=2, sticky="w", padx=self.PADX, pady=self.PADY)

        return [label, entry]

    def checkbox_widget(self, master, label, var, row=0, column=0, cspan=3) -> list[tk.Widget]:
        checkbutton = tk.Checkbutton(master=master, text=label, variable=var)
        checkbutton.grid(row=row, column=column, columnspan=cspan, sticky="w", padx=8)
        return [checkbutton]

    def _browse_file(self, var):
        global _LastFile
        init_path = self._last_file
        if len(var.get()) > 0:
            init_path = var.get()
        selected_file = filedialog.askopenfilename(initialdir=init_path, title="Kies een bestand.")
        if selected_file:
            var.set(selected_file)
            _LastFile = selected_file

    def _browse_dir(self, var):
        global _LastDir
        init_path = self._last_dir
        if len(var.get()) > 0:
            init_path = var.get()
        selected_path = filedialog.askdirectory(initialdir=init_path, title="Kies een directory")
        if selected_path:
            var.set(selected_path)
            _LastDir = selected_path

    def path_widget(self, master, label_text: str, var, row=0, file=False) -> list[tk.Widget]:
        label = tk.Label(master=master, text=f"{label_text}:")
        label.grid(row=row, column=0, sticky="w", padx=self.PADX, pady=self.PADY)

        entry = tk.Entry(master=master, textvariable=var, width=40)
        entry.grid(row=row, column=1, sticky="ew", padx=self.PADX, pady=self.PADY)

        if file:
            button = tk.Button(master=master, text="...", command=lambda: self._browse_file(var))
        else:
            button = tk.Button(master=master, text="...", command=lambda: self._browse_dir(var))
        button.grid(row=row, column=2, sticky="ew", padx=self.PADX, pady=self.PADY)

        return [label, entry, button]

    def checklist_widget(self, master, label, items, vars, row=0, items_per_row=4) -> list[tk.Widget]:
        frame = tk.LabelFrame(master=master, text=label, borderwidth=2, padx=5)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=self.PADX, pady=self.PADY)
        w: list[tk.Widget] = [frame]
        for i, item in enumerate(items):
            w.extend(
                self.checkbox_widget(
                    frame, item, vars[i], row=int(i / items_per_row), column=i % items_per_row, cspan=1
                )
            )
        return w

    def optional_file_widget(self, master, label, checklabel, filelabel, checkvar, filevar, row=0) -> list[tk.Widget]:
        frame = tk.LabelFrame(master=master, text=label, borderwidth=2, padx=5)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=self.PADX, pady=self.PADY)
        w: list[tk.Widget] = [frame]

        w.extend(self.checkbox_widget(frame, checklabel, checkvar, row=0))
        w.extend(self.path_widget(frame, filelabel, filevar, row=1, file=True))

        return w


if __name__ == "__main__":
    """
    Test code
    """

    def sel():
        selection = "You selected the option " + str(var.get())
        label.config(text=selection)

    root = tk.Tk()
    widgets = []
    widget_factor = WidgetFactory()

    N1 = ttk.Notebook(root)
    T1 = ttk.Frame(N1)
    N1.add(T1, text="Tab 1")

    var = tk.IntVar()

    F1 = tk.LabelFrame(master=T1, text="Frame", borderwidth=4)
    widgets.append(F1)
    R1 = tk.Radiobutton(F1, text="Option 1", variable=var, value=12, command=sel)
    widgets.append(R1)
    R2 = tk.Radiobutton(F1, text="Option 2", variable=var, value=34, command=sel)
    widgets.append(R2)
    R3 = tk.Radiobutton(F1, text="Option 3", variable=var, value=56, command=sel)
    widgets.append(R3)
    label = tk.Label(F1, text="You selected the option 00")
    widgets.append(label)

    for i in widgets:
        i.pack(anchor=tk.W, padx=widget_factor.PADX, pady=widget_factor.PADY)

    T2 = ttk.Frame(N1)
    N1.add(T2, text="Tab 2")

    var2 = tk.StringVar()
    widgets.extend(widget_factor.text_widget(T2, "Name", var2, row=0))
    var3 = tk.DoubleVar()
    widgets.extend(widget_factor.number_widget(T2, "Number", "m/s", var3, row=1))
    var4 = tk.BooleanVar()
    widgets.extend(widget_factor.checkbox_widget(T2, "Check this.", var4, row=4))

    T3 = ttk.Frame(N1)
    N1.add(T3, text="Tab 3")

    var5 = tk.StringVar()
    widgets.extend(widget_factor.path_widget(T3, "Path", var5, row=0))
    var6 = tk.StringVar()
    widgets.extend(widget_factor.path_widget(T3, "File", var6, row=1, file=True))

    vars7 = [tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()]
    items = ["Check Item 1", "Check Item 2", "Check Item 3"]
    widgets.extend(widget_factor.checklist_widget(T3, "Check Items", items, vars7, row=2))

    var9 = tk.BooleanVar()
    var10 = tk.StringVar()
    widgets.extend(
        widget_factor.optional_file_widget(T3, "Feature", "Generate Data", "Stored Data", var9, var10, row=4)
    )

    N1.pack(expand=1, fill="both")

    root.mainloop()
