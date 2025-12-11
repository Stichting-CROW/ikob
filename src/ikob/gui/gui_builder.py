# ruff: noqa: F403,F405
import tkinter as tk
from tkinter import ttk

from ikob.gui.widget_factory import WidgetFactory

# Build a config dictionary from the template


class GuiBuilder:
    """Gui and config builder, the widgets have state for the file dialogs, otherwise stateless."""

    def __init__(self):
        self.widget_factory = WidgetFactory()

    def build_tk_interface(self, root, tk_template, new_cmd, load_cmd, save_cmd):
        notebook = ttk.Notebook(root)
        widgets: list[tk.Widget] = [notebook]
        for key in tk_template:
            if not isinstance(tk_template[key], dict):
                continue

            tab = ttk.Frame(notebook)
            tab.columnconfigure((1), weight=1)
            label = key
            if "label" in tk_template[key]:
                label = tk_template[key]["label"]
            notebook.add(tab, text=label)
            widgets.append(tab)
            widgets.extend(self._add_widgets(tab, tk_template[key]))

        notebook.pack(expand=True, fill="both")
        # Add load/save/new buttons.
        frame = tk.Frame()
        frame.pack(expand=True, fill=tk.X, ipadx=5, ipady=5)

        save_button = tk.Button(master=frame, text="Opslaan ...", command=save_cmd)
        save_button.pack(side=tk.RIGHT, padx=10, ipadx=10)

        load_button = tk.Button(master=frame, text="Laden ...", command=load_cmd)
        load_button.pack(side=tk.LEFT, padx=10, ipadx=10)

        new_button = tk.Button(master=frame, text="Nieuw", command=new_cmd)
        new_button.pack(side=tk.LEFT, padx=10, ipadx=10)

        widgets.extend([frame, save_button, load_button, new_button])

        return widgets

    @staticmethod
    def build_config_dict(template):
        """
        Build a config dictionary from the template
        """
        config = {}
        for key in set(template.keys()):
            if key != "label":
                if isinstance(template[key], dict):
                    if "type" in template[key]:
                        config[key] = GuiBuilder._get_value(template[key])
                    else:
                        config[key] = GuiBuilder.build_config_dict(template[key])
                else:
                    config[key] = template[key]
        return config

    def add_tk_vars_template(self, template):
        """
        Add tkvars to a template
        """
        for key in set(template.keys()):
            if key == "label":
                continue
            if not isinstance(template[key], dict):
                continue
            if "type" not in template[key]:
                self.add_tk_vars_template(template[key])
                continue

            var = None
            leaf = template[key]
            leaf_type = leaf["type"]
            if leaf_type == "number":
                var = tk.DoubleVar(value=self._default_value(leaf))  # type: ignore
            elif leaf_type == "text" or leaf_type == "file" or leaf_type == "directory" or leaf_type == "choice":
                var = tk.StringVar(value=self._default_value(leaf))  # type: ignore
            elif leaf_type == "checkbox":
                var = tk.BooleanVar(value=self._default_value(leaf))  # type: ignore
            elif leaf_type == "checklist":
                default_list = self, self._default_value(leaf)
                var = [tk.BooleanVar(value=(item in default_list)) for item in leaf["items"]]
            if var:
                template[key]["tkvar"] = var
            else:
                print(f"FOUT? template[{key}] = {leaf}")

    def set_tk_vars(self, template, config):
        """
        Set the value of a config item in tkvars
        """
        for key in template:
            if key not in config:
                # handle missing key?
                continue
            if isinstance(config[key], dict):
                self.set_tk_vars(template[key], config[key])
                continue

            if "type" not in template[key]:
                continue

            leaf_type = template[key]["type"]
            if leaf_type == "checklist":
                values = config[key]
                for i, item in enumerate(template[key]["items"]):
                    template[key]["tkvar"][i].set(item in values)
            else:
                template[key]["tkvar"].set(config[key])

    @staticmethod
    def _empty_value(leaf_type):
        if leaf_type == "number":
            return 0
        elif leaf_type == "text" or leaf_type == "file" or leaf_type == "directory" or leaf_type == "choice":
            return ""
        elif leaf_type == "check":
            return False
        elif leaf_type == "checklist":
            return []
        return None

    @staticmethod
    def _default_value(leaf):
        if "default" in leaf:
            return leaf["default"]
        elif leaf["type"] == "choice":
            return leaf["items"][0]
        else:
            return GuiBuilder._empty_value(leaf["type"])

    @staticmethod
    def _get_value(leaf):
        value = None
        if "tkvar" in leaf:
            leaf_type = leaf["type"]
            leaf_tkvar = leaf["tkvar"]
            leaf_items = leaf["items"] if "items" in leaf else None
            if leaf_type == "checklist":
                value = []
                assert leaf_items is not None, "When the type of the tk leaf is a checklist it's expected to have items"

                for i, var in enumerate(leaf_tkvar):
                    if var.get():
                        value.append(leaf_items[i])
            else:
                value = leaf_tkvar.get()
        else:
            value = GuiBuilder._default_value(leaf)
        return value

    def _add_widgets(self, master, template):
        widgets = []
        row = 0
        for key in template:
            if key == "label":
                continue
            if not isinstance(template[key], dict):
                continue

            if "type" in template[key]:
                leaf = template[key]
                leaf_type = leaf["type"]
                label = key
                unit = ""
                items = []
                if "label" in leaf:
                    label = leaf["label"]
                if "unit" in leaf:
                    unit = leaf["unit"]
                if "items" in leaf:
                    items = leaf["items"]
                var = leaf["tkvar"]
                if leaf_type == "number":
                    widgets.extend(self.widget_factory.number_widget(master, label, unit, var, row=row))
                elif leaf_type == "text":
                    widgets.extend(self.widget_factory.text_widget(master, label, var, row=row))
                elif leaf_type == "file":
                    widgets.extend(self.widget_factory.path_widget(master, label, var, row=row, file=True))
                elif leaf_type == "directory":
                    widgets.extend(self.widget_factory.path_widget(master, label, var, row=row))
                elif leaf_type == "choice":
                    widgets.extend(self.widget_factory.choice_widget(master, label, items, unit, var, row=row))
                elif leaf_type == "checkbox":
                    widgets.extend(self.widget_factory.checkbox_widget(master, label, var, row=row))
                elif leaf_type == "checklist":
                    widgets.extend(self.widget_factory.checklist_widget(master, label, items, var, row=row))
                else:
                    dummy = tk.Label(master=master, text="Dummy")
                    dummy.grid(row=row, column=0)
                    widgets.append(dummy)
                row = row + 1
            else:
                label = key
                if "label" in template[key]:
                    label = template[key]["label"]
                frame = tk.LabelFrame(master=master, text=label, borderwidth=2)
                frame.columnconfigure((1), weight=1)
                frame.grid(
                    row=row,
                    column=0,
                    columnspan=3,
                    sticky="ew",
                    padx=self.widget_factory.PADX,
                    pady=self.widget_factory.PADY,
                )
                widgets.append(frame)
                self._add_widgets(frame, template[key])
                row = row + 1
        return widgets
