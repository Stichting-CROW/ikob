import logging
from dataclasses import field, is_dataclass
from enum import StrEnum
from typing import Any

# The config uses pydantic dataclasses so that they can be built from nested dictionaries.
from pydantic.dataclasses import dataclass

from ikob.gui.gui_config_classes import (
    GUI_ITEM_FACTORY_KEY,
    GUI_LABEL_KEY,
    GuiConfigItem,
    GuiDataType,
)

logger = logging.getLogger(__name__)


def gui_field(label: str, data_type: GuiDataType, default: str | list[str] | float = "", items=[], unit="") -> Any:
    return field(
        default_factory=lambda: default,
        metadata={
            GUI_ITEM_FACTORY_KEY: lambda: GuiConfigItem(
                label=label,
                data_type=data_type,
                default=default,
                items=items,
                unit=unit,
            )
        },
    )


def gui_section(label: str, config_class) -> Any:
    assert is_dataclass(config_class()), "Gui sections should have a data class as value"
    return field(default_factory=config_class, metadata={GUI_LABEL_KEY: label})


@dataclass
class PathConfig:
    skims_directory: str = gui_field("Basis directory (input)", GuiDataType.DIRECTORY, default="skims")
    segs_directory: str = gui_field("SEGS directory (input)", GuiDataType.DIRECTORY, default="SEGS")
    output_directory: str = gui_field("Output directory ", GuiDataType.DIRECTORY, default="output")


class Motive(StrEnum):
    WORK = "work"
    DAILY_GROCERIES = "daily_groceries"
    EDUCATION = "education"
    SOCIAL_RECREATIONAL = "social_recreational"


class IncomeGroup(StrEnum):
    LOW = "low"
    MEDIUM_LOW = "medium_low"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"


class PartOfDay(StrEnum):
    MORNING_RUSH = "morning_rush"
    EVENING_RUSH = "evening_rush"
    OFF_PEAK = "off_peak"


FILENAME_FIELD_NAME = "__FILENAME__"


class NoCarKind(StrEnum):
    NO_CAR = "no_car"
    NO_LICENSE = "no_license"


@dataclass
class ProjectConfig:
    name: str = gui_field("Project name", default="Project 1", data_type=GuiDataType.TEXT)
    urbanization_scenario: str = gui_field(
        "The urbanization scenario (SEGS subdirectory) to use", data_type=GuiDataType.TEXT
    )
    pricing_regime: str = gui_field(
        "The name of the pricing regimes, used to distinguish output of different runs of the same project",
        default="Basis",
        data_type=GuiDataType.TEXT,
    )
    paths: PathConfig = gui_section("Paths", PathConfig)
    motives: list[Motive] = gui_field(
        "Travel motives to consider",
        GuiDataType.CHECKLIST,
        default=Motive.WORK,
        items=list(Motive),
    )
    use_e_bike: bool = gui_field("Use E-bikes in computation", GuiDataType.CHECKBOX)
    income_groups: list[IncomeGroup] = gui_field(
        "Income groups to consider",
        GuiDataType.CHECKLIST,
        default=list(IncomeGroup),
        items=list(IncomeGroup),
    )


@dataclass
class PTCosts:
    base_fare_cent: float = gui_field(
        "Base fare",
        GuiDataType.NUMBER,
        default=75,
        unit="Eurocent",
    )
    cent_per_km: float = gui_field(
        "Variable costs",
        GuiDataType.NUMBER,
        default=12,
        unit="Eurocent/km",
    )
    use_price_cap: bool = gui_field("Use a price cap for a public transport trip", GuiDataType.CHECKBOX)
    price_cap: float = gui_field("The value of the pricecap", GuiDataType.NUMBER, default=9999, unit="Eurocent")


@dataclass
class ICECarCosts:
    cent_per_km: float = gui_field("Variable costs", GuiDataType.NUMBER, unit="Eurocent/km", default=16)
    km_charge: float = gui_field("Additional km charge", GuiDataType.NUMBER, unit="Eurocent/km")


@dataclass
class EVCarCosts:
    cent_per_km: float = gui_field("Variable costs", GuiDataType.NUMBER, unit="Eurocent/km", default=5)
    km_charge: float = gui_field("Additional km charge", GuiDataType.NUMBER, unit="Eurocent/km")


@dataclass
class NoCarCosts:
    no_car_euro_per_min: float = gui_field(
        "Shared car time costs (for non car owners with a drivers license)",
        GuiDataType.NUMBER,
        unit="Euro/min",
        default=0.05,
    )
    no_car_euro_per_km: float = gui_field(
        "Shared car distance costs (for non car owners with a drivers license)",
        GuiDataType.NUMBER,
        default=0.33,
        unit="Euro/km",
    )

    no_license_euro_per_min: float = gui_field(
        "Taxi time costs (for non car owners with no drivers license)",
        GuiDataType.NUMBER,
        unit="Euro/min",
        default=0.40,
    )
    no_license_euro_per_km: float = gui_field(
        "Taxi distance costs (for non car owners with no drivers license)",
        GuiDataType.NUMBER,
        default=2.40,
        unit="Euro/km",
    )


@dataclass
class ElectricVehicleDistribution:
    low: float = gui_field("Low", GuiDataType.NUMBER, unit="%")
    medium_low: float = gui_field("Medium low", GuiDataType.NUMBER, unit="%")
    medium_high: float = gui_field("Medium high", GuiDataType.NUMBER, unit="%")
    high: float = gui_field("High", GuiDataType.NUMBER, unit="%")

    def get_percentage(self, income_group: IncomeGroup):
        # this is to allow grabbing the percentage dynamically
        # TODO: in config validation it should be validated that all income groups are present as fields
        return getattr(self, income_group)


@dataclass
class SkimsConfig:
    parts_of_day: list[PartOfDay] = gui_field(
        "The parts of the day to consider",
        GuiDataType.CHECKLIST,
        default=list(PartOfDay),
        items=list(PartOfDay),
    )
    pt_costs: PTCosts = gui_section("Public transport costs", PTCosts)
    use_pt_costs_file: bool = gui_field(
        "Is there a separate file for public transport costs (overwrites the cost computation) ", GuiDataType.CHECKBOX
    )
    free_pt_percentage: float = gui_field(
        "Percentage of people with free public transport", GuiDataType.NUMBER, default=3, unit="%"
    )
    ice_costs: ICECarCosts = gui_section("Cost for an internal combustion engine vehicle", ICECarCosts)
    ev_costs: EVCarCosts = gui_section("Cost for an electric vehicle", EVCarCosts)
    ev_distribution: ElectricVehicleDistribution = gui_section(
        "Percentage of car owners with an electric vehicle",
        ElectricVehicleDistribution,
    )
    parking_search_time_file: str = gui_field("Parking search time file", GuiDataType.FILE)
    no_car_costs: NoCarCosts = gui_section("Car travel costs for non car owners", NoCarCosts)


@dataclass
class WorkTVOM:
    low: float = gui_field("Low", GuiDataType.NUMBER, default=4)
    medium_low: float = gui_field("Medium low", GuiDataType.NUMBER, default=6)
    medium_high: float = gui_field("Medium high", GuiDataType.NUMBER, default=9)
    high: float = gui_field("High", GuiDataType.NUMBER, default=12)

    def get_tvom(self, income_group: IncomeGroup):
        # this is to allow grabbing the tvom dynamically
        # TODO: in config validation it should be validated that all income groups are present as fields
        return getattr(self, income_group)


@dataclass
class OtherTVOM:
    low: float = gui_field("Low", GuiDataType.NUMBER, default=4.8, unit="Minutes/Euro")
    medium_low: float = gui_field("Medium low", GuiDataType.NUMBER, default=7.25, unit="Minutes/Euro")
    medium_high: float = gui_field("Medium high", GuiDataType.NUMBER, default=10.9, unit="Minutes/Euro")
    high: float = gui_field("High", GuiDataType.NUMBER, default=15.5, unit="Minutes/Euro")

    def get_tvom(self, income_group: IncomeGroup):
        # this is to allow grabbing the tvom dynamically
        # TODO: in config validation it should be validated that all income groups are present as fields
        return getattr(self, income_group)


@dataclass
class TVOMConfig:
    work_tvom: WorkTVOM = gui_section("Time value of money per income group, for work trips", WorkTVOM)
    other_tvom: OtherTVOM = gui_section("Time value of money per income group, for other trips", OtherTVOM)


@dataclass
class ChainsAndHubsConfig:
    # TODO: The meaning of these fields is not immediately clear
    use: bool = gui_field("Whether to use chains and hubs", GuiDataType.CHECKBOX)
    hub_file: str = gui_field("File containing the hubs", GuiDataType.FILE)
    hub_collection: str = gui_field("The name of the collection hubs", GuiDataType.TEXT)


@dataclass
class ArtificialCarOwnershipConfig:
    use: bool = gui_field("Whether to use artificial car ownership", GuiDataType.CHECKBOX)
    file: str = gui_field("File describing the artificial car ownership", GuiDataType.FILE)


@dataclass
class ParkingCostsConfig:
    use: bool = gui_field("Use parking costs. If not, parking is presumed to be free.", GuiDataType.CHECKBOX)
    file: str = gui_field("File describing the parking costs", GuiDataType.FILE)


@dataclass
class AdditionalCostsConfig:
    use: bool = gui_field("Whether there are any additional costs", GuiDataType.CHECKBOX)
    file: str = gui_field("File describing the additional costs", GuiDataType.FILE)


class CarOwnershipGroup(StrEnum):
    ALL_GROUPS = "all groups"
    CAR_OWNERS_ONLY = "car_owners_only"


@dataclass
class AdvancedConfig:
    artificial_car_ownership: ArtificialCarOwnershipConfig = gui_section(
        "Artificial car ownership (e.g. to simulate stricter parking norms)", ArtificialCarOwnershipConfig
    )
    parking_costs_cents: ParkingCostsConfig = gui_section("Parking costs", ParkingCostsConfig)
    additional_costs_cents: AdditionalCostsConfig = gui_section(
        "Additionele kosten, dit zijn extra kosten die gemaakt worden bij bijvoorbeeld een cordonheffing, "
        "waarbij voor sommige verplaatsingen wel extra kosten gelden en voor andere verplaatsingen niet. ",
        AdditionalCostsConfig,
    )
    # TODO: this requires further explanation
    car_ownership_groups: list[CarOwnershipGroup] = gui_field(
        "Which groups should be considered regarding car ownership",
        GuiDataType.CHECKLIST,
        default=CarOwnershipGroup.ALL_GROUPS,
        items=list(CarOwnershipGroup),
    )


@dataclass
class IkobConfig:
    # The top level config can only contain sections, shown as tabs in the gui
    project: ProjectConfig = gui_section("Project", ProjectConfig)
    skims: SkimsConfig = gui_section("Travel costs and time", SkimsConfig)
    tvom: TVOMConfig = gui_section("Time value of money", TVOMConfig)
    chains_and_hubs: ChainsAndHubsConfig = gui_section("Chains and hubs", ChainsAndHubsConfig)
    advanced: AdvancedConfig = gui_section("Advanced", AdvancedConfig)
