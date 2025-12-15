import logging
import tkinter as tk
from dataclasses import Field, dataclass
from enum import Enum
from typing import Literal, Sequence

logger = logging.getLogger(__name__)


class GuiConfigError(Exception): ...


GUI_LABEL_KEY = Literal["label"]
GUI_ITEM_FACTORY_KEY = Literal["gui_item_factory"]
GUI_ITEM_CACHE_ATTRIBUTE = Literal["__gui_item__"]


class GuiDataType(Enum):
    CHECKBOX = "checkbox"
    CHECKLIST = "checklist"
    DIRECTORY = "directory"
    FILE = "file"
    NUMBER = "number"
    TEXT = "text"


@dataclass
class GuiConfigItem:
    # The tkvar is added by the gui builder
    label: str
    data_type: GuiDataType
    default: str | bool | float | list[str]
    items: list[str]
    unit: str
    # Cannot be initialized yet because 'no default root window'
    # aka no tk application exists yet
    tkvar: tk.Variable | Sequence[tk.Variable] | None = None

    def __init__(
        self,
        label: str,
        data_type: GuiDataType,
        default: str | list[str] | bool | float = "",
        items: list[str] = [],
        unit: str = "",
    ):
        default_values: dict[GuiDataType, bool | int] = {GuiDataType.CHECKBOX: False, GuiDataType.NUMBER: 0}

        if not default:
            default = default_values.get(data_type, default)

        # When the gui item has multiple items (to choose from) and the default value is a singular value:
        # Make it a list
        if items and isinstance(default, str):
            default = [default]

        self.label = label
        self.data_type = data_type
        self.default = default
        self.items = items
        self.unit = unit

    @classmethod
    def from_metadata(cls, config_class, field: Field) -> "GuiConfigItem":
        """Build a gui config class from the meta data of a config field.

        Note: The internals of this method are slightly evil.
        This build the gui config item from the factory stored in the metadata.
        The gui config item is then cached for later used in a 'secret' config class attributed named <prefix><field_name>

        This is necessary because:
        The metadata of a field is set when a dataclass is defined, so every instance of the class has the same metadata.
        Were the metadata to contain the gui config item directly, the following problem would occur:
            If a dataclass is used reused throughout the config, all the gui items of that class would hold the same value.

        So instead the metadata only holds a factory to create the right gui item, and when the gui item is needed we create it from the factory.
        This gui item is then cached on the class _instance_, so each class instance has it's own gui items.
        """
        cached = getattr(config_class, str(GUI_ITEM_CACHE_ATTRIBUTE) + field.name, None)
        if cached is not None:
            return cached

        if GUI_ITEM_FACTORY_KEY not in field.metadata:
            raise GuiConfigError(
                "Attempting to build gui item from metadata, but {GUI_ITEM_FACTORY_KEY} is not present in metadata nor is the gui item cached"
            )

        gui_item = field.metadata[GUI_ITEM_FACTORY_KEY]()
        setattr(config_class, str(GUI_ITEM_CACHE_ATTRIBUTE) + field.name, gui_item)
        return gui_item

    def build_and_set_tk_var(self):
        """Build and add the tk var separately from the init because it requires a 'root window'.

        The root window is a tk application like the config App."""
        if self.tkvar is not None:
            raise GuiConfigError(f"Building tk variable for config item '{self.label}', but one already exists.")

        tk_var = None
        if self.data_type == GuiDataType.NUMBER:
            tk_var = tk.DoubleVar(value=self.default)  # type: ignore
        elif (
            self.data_type == GuiDataType.TEXT
            or self.data_type == GuiDataType.FILE
            or self.data_type == GuiDataType.DIRECTORY
        ):
            tk_var = tk.StringVar(value=self.default)  # type: ignore
        elif self.data_type == GuiDataType.CHECKBOX:
            tk_var = tk.BooleanVar(value=self.default)  # type: ignore
        elif self.data_type == GuiDataType.CHECKLIST:
            tk_var = [tk.BooleanVar(value=(item in self.default)) for item in self.items]  # type: ignore

        if not tk_var:
            raise GuiConfigError(f"Unable to compute a tkvar for gui config item with data type {self.data_type}.")
        self.tkvar = tk_var

    def get_gui_value(self):
        if self.data_type == GuiDataType.CHECKLIST:
            value = []
            for i, var in enumerate(self.tkvar):  # type: ignore
                if var.get():
                    value.append(self.items[i])
            return value
        else:
            return self.tkvar.get()  # type: ignore

    def set_gui_value(self, value):
        if self.data_type == GuiDataType.CHECKLIST:
            for i, var in enumerate(self.tkvar):  # type: ignore
                var.set(self.items[i] in value)
        else:
            self.tkvar.set(value)  # type: ignore


class GuiSection:
    def __init__(self, label: str, contents: "list[GuiSection | GuiConfigItem]"):
        self.label = label
        self.contents = contents


class GuiTemplate:
    def __init__(self, contents: list[GuiSection]):
        self.contents = contents
