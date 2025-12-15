import logging
import tkinter as tk
from dataclasses import fields, is_dataclass
from tkinter import ttk

from ikob.gui.configuration_definition import IkobConfig
from ikob.gui.gui_config_classes import (
    GUI_ITEM_FACTORY_KEY,
    GUI_LABEL_KEY,
    GuiConfigError,
    GuiConfigItem,
    GuiDataType,
)
from ikob.gui.widget_factory import WidgetFactory

logger = logging.getLogger(__name__)


class IkobGui:
    """Gui and config builder. Uses the IkobConfig data class to build build the gui.

    IkobConfig is dataclass where each field has some metadata for the Gui.
    Fields are either:
        A config subsection, represented by a dataclass with a label
        A config item, represented by a field in dataclass with a GuiConfigItem

    The GuiBuilding first adds tk variables to the fields initialized with the initial value of the config item.
    Then the tk interface can be build. Widgets are created based on the type of field (subsection / config item)
    and on the different data types of the config items (text, checkbox etc.)

    The gui's edits will be made to the tk vars of the config items,
    these edits can be transferred to the data class
    and the defaults of the data class can also be restored to the gui.
    """

    def __init__(self):
        self._widget_factory = WidgetFactory()
        self._config = IkobConfig()
        self._add_tk_vars_to_config(self._config)

    def build_tk_interface(self, root: tk.Tk, new_cmd, load_cmd, save_cmd) -> list[tk.Widget]:
        """Build the tk widgets from the ikob config.

        Throws an error if the meta data of the config (used for the gui) is not as expected
        """
        notebook = ttk.Notebook(root)
        widgets: list[tk.Widget] = [notebook]
        for field in fields(self._config):
            metadata = field.metadata
            assert GUI_LABEL_KEY in metadata, (
                "All fields in IkobConfig are expected to be gui_sections (see gui_section())"
            )
            label = metadata[GUI_LABEL_KEY]

            tab = ttk.Frame(notebook)
            tab.columnconfigure((1), weight=1)

            notebook.add(tab, text=label)
            widgets.append(tab)

            gui_section = getattr(self._config, field.name)
            widgets.extend(self._add_widgets(tab, gui_section))

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

    def get_config_from_gui(self) -> IkobConfig:
        """
        return a populated IkobConfig class with the values from the gui
        """
        # Manually do a deep copy to a new IkobConfig instance.
        # The instance in self._config is internal and a deep copy does not work because of the tk gui items in there.
        return_config = IkobConfig()
        logger.info("Writing gui values to a config class")
        self._get_config_from_gui(self._config, return_config)
        return return_config

    def reset_gui(self):
        # Pass through to a recursive method
        logger.info("Resetting gui values to defaults")
        self._reset_gui_values_to_default(self._config)

    def load_config_in_gui(self, config_to_load):
        # Pass through to a recursive method
        logger.info("Loading existing config into gui")
        self._load_config_in_gui(self._config, config_to_load)

    def _load_config_in_gui(self, gui_section, config_section):
        assert is_dataclass(config_section), f"Cannot load config from non dataclass, type is {type(config_section)}"
        assert is_dataclass(gui_section), "Cannot load config to non dataclass"

        for gui_field in fields(gui_section):
            config_field = None
            for f in fields(config_section):
                if f.name == gui_field.name:
                    config_field = f
            if config_field is None:
                raise GuiConfigError(
                    f"Cannot load config to gui. Field {gui_field.name} present in gui but not in config to load."
                )

            gui_metadata = gui_field.metadata

            if GUI_ITEM_FACTORY_KEY in gui_metadata:
                # The field is a gui item
                # Get the value from the config field and load it in the gui item
                gui_item = GuiConfigItem.from_metadata(gui_section, gui_field)
                value = getattr(config_section, config_field.name)
                gui_item.set_gui_value(value)
            elif GUI_LABEL_KEY in gui_metadata:
                # The field is gui section
                logger.info("now looking at meta data with label ")
                logger.info(gui_metadata[GUI_LABEL_KEY])
                logger.info(f"Processing subsection at name {gui_field.name}")

                gui_subsection = getattr(gui_section, gui_field.name)
                config_subsection = getattr(config_section, gui_field.name)
                self._load_config_in_gui(gui_subsection, config_subsection)
            else:
                raise GuiConfigError(
                    f"The field {gui_field.name} has neither {GUI_ITEM_FACTORY_KEY} nor {GUI_LABEL_KEY} in it's metadata. "
                    "Unable to make make config gui."
                )

    def _get_config_from_gui(self, gui_section, config_section):
        assert is_dataclass(gui_section), "Cannot add gui values to non dataclass"

        for gui_field in fields(gui_section):
            config_field = None
            for f in fields(config_section):
                if f.name == gui_field.name:
                    config_field = f
            if config_field is None:
                raise GuiConfigError(
                    f"Cannot load config to gui. Field {gui_field.name} present in gui but not in config to load."
                )

            gui_metadata = gui_field.metadata

            if GUI_ITEM_FACTORY_KEY in gui_metadata:
                # The field is a gui item
                # Get the value from the gui and load it in the config
                gui_item = GuiConfigItem.from_metadata(gui_section, gui_field)
                value = gui_item.get_gui_value()
                setattr(config_section, config_field.name, value)
            elif GUI_LABEL_KEY in gui_metadata:
                # The field is gui section
                gui_subsection = getattr(gui_section, gui_field.name)
                config_subsection = getattr(config_section, gui_field.name)
                self._load_config_in_gui(gui_subsection, config_subsection)
            else:
                raise GuiConfigError(
                    f"The field {gui_field.name} has neither {GUI_ITEM_FACTORY_KEY} nor {GUI_LABEL_KEY} in it's metadata. "
                    "Unable to make make config gui."
                )

    def _reset_gui_values_to_default(self, gui_section):
        assert is_dataclass(gui_section), "Cannot reset gui values of non dataclass"
        for field in fields(gui_section):
            metadata = field.metadata
            if GUI_ITEM_FACTORY_KEY in metadata:
                # The field is a gui item
                gui_item = GuiConfigItem.from_metadata(gui_section, field)
                default_value = gui_item.default
                gui_item.set_gui_value(default_value)
            elif GUI_LABEL_KEY in metadata:
                # The field is gui section
                subsection = getattr(gui_section, field.name)
                self._reset_gui_values_to_default(subsection)
            else:
                raise GuiConfigError(
                    f"The field {field.name} has neither {GUI_ITEM_FACTORY_KEY} nor {GUI_LABEL_KEY} in it's metadata. "
                    "Unable to make make config gui."
                )

    def _add_tk_vars_to_config(self, gui_section):
        assert is_dataclass(gui_section), "Cannot add tk vars to non dataclass"

        for field in fields(gui_section):
            metadata = field.metadata
            if GUI_ITEM_FACTORY_KEY in metadata:
                # The field is a gui item
                gui_item = GuiConfigItem.from_metadata(gui_section, field)
                gui_item.build_and_set_tk_var()
            elif GUI_LABEL_KEY in metadata:
                # The field is gui section
                subsection = getattr(gui_section, field.name)
                self._add_tk_vars_to_config(subsection)
            else:
                raise GuiConfigError(
                    f"The field {field.name} has neither {GUI_ITEM_FACTORY_KEY} nor {GUI_LABEL_KEY} in it's metadata. "
                    "Unable to make make config gui."
                )

    def _add_widgets(self, master, gui_section) -> list[tk.Widget]:
        widgets = []
        row = 0
        for field in fields(gui_section):
            metadata = field.metadata
            if GUI_ITEM_FACTORY_KEY in metadata:
                # The field is a gui item
                gui_item = GuiConfigItem.from_metadata(gui_section, field)
                widgets.extend(self._get_widget_for_item(master, gui_item, row))
            elif GUI_LABEL_KEY in metadata:
                # The field is a gui section
                label = metadata[GUI_LABEL_KEY]
                frame = tk.LabelFrame(master=master, text=label, borderwidth=2)
                frame.columnconfigure((1), weight=1)
                frame.grid(
                    row=row,
                    column=0,
                    columnspan=3,
                    sticky="ew",
                    padx=self._widget_factory.PADX,
                    pady=self._widget_factory.PADY,
                )
                widgets.append(frame)
                subsection = getattr(gui_section, field.name)
                self._add_widgets(frame, subsection)
            else:
                raise GuiConfigError(
                    f"The field {field.name} has neither {GUI_ITEM_FACTORY_KEY} nor {GUI_LABEL_KEY} in it's metadata. "
                    "Unable to make make config gui."
                )
            row = row + 1

        return widgets

    def _get_widget_for_item(self, master, config_item: GuiConfigItem, row: int) -> list[tk.Widget]:
        label = config_item.label
        unit = config_item.unit
        items = config_item.items
        tkvar = config_item.tkvar

        if config_item.data_type == GuiDataType.NUMBER:
            return self._widget_factory.number_widget(master, label, unit, tkvar, row=row)
        elif config_item.data_type == GuiDataType.TEXT:
            return self._widget_factory.text_widget(master, label, tkvar, row=row)
        elif config_item.data_type == GuiDataType.FILE:
            return self._widget_factory.path_widget(master, label, tkvar, row=row, file=True)
        elif config_item.data_type == GuiDataType.DIRECTORY:
            return self._widget_factory.path_widget(master, label, tkvar, row=row)
        elif config_item.data_type == GuiDataType.CHECKBOX:
            return self._widget_factory.checkbox_widget(master, label, tkvar, row=row)
        elif config_item.data_type == GuiDataType.CHECKLIST:
            return self._widget_factory.checklist_widget(master, label, items, tkvar, row=row)
        else:
            logger.warning("Adding a dummy label to the gui, is this intentional?")
            dummy = tk.Label(master=master, text="Dummy")
            dummy.grid(row=row, column=0)
            return [dummy]
