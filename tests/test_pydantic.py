import json
import pathlib
import pytest

from dataclasses import dataclass
from enum import Enum
from typing import Literal
from pathlib import Path
from pydantic import BaseModel, Field


class Motive(str, Enum):
    Work = "werk"


class IncomeGroup(str, Enum):
    Laag = ("laag",)
    MiddelLaag = ("middellaag",)
    MiddelHoog = ("middelhoog",)
    Hoog = "hoog"


class Paths(BaseModel):
    segs_directory: Path
    skims_directory: Path
    output_directory: Path


class Project(BaseModel):
    name: str = Field(validation_alias="naam")
    regime: Literal["Basis"] = Field(validation_alias="beprijzingsregime")
    paths: Paths = Field(validation_alias="paden")
    scenario: int = Field(validation_alias="verstedelijkingsscenario")
    motives: list[Motive] = Field(validation_alias="motieven")
    # FIXME: This has been replaced to a checkbox, so just a bool.
    use_ebike: list[str] = Field(validation_alias="fiets of E-fiets")
    income_groups: list[IncomeGroup] = Field(validation_alias="welke_inkomensgroepen")


@dataclass
class FuelCost:
    variable_cost: float = Field(validation_alias="variabele kosten")
    road_pricing: float = Field(validation_alias="kmheffing")


@dataclass
class VariableCostsNoCar:
    no_car: float = Field(validation_alias="GeenAuto")
    no_license: float = Field(validation_alias="GeenRijbewijs")


@dataclass
class PriceCap:
    used: bool = Field(validation_alias="gebruiken")
    value: float = Field(validation_alias="getal")


@dataclass
class PublicTransportCostFile:
    used: bool = Field(validation_alias="gebruiken")


@dataclass
class PublicTransportCosts:
    cost_per_km: float = Field(validation_alias="kmkosten")
    start_rate: float = Field(validation_alias="starttarief")


class DayKind(str, Enum):
    RestDag = "Restdag"


@dataclass
class TimeCostsNoCar:
    no_car: float = Field(validation_alias="GeenAuto")
    no_license: float = Field(validation_alias="GeenRijbewijs")


class Skims(BaseModel):
    fossil_car_cost: FuelCost = Field(validation_alias="Kosten auto fossiele brandstof")
    electric_car_cost: FuelCost = Field(validation_alias="Kosten elektrische auto")
    variable_kost_no_car: VariableCostsNoCar = Field(validation_alias="varkostenga")
    price_cap: PriceCap = Field(validation_alias="pricecap")
    public_transport_cost_file: PublicTransportCostFile = Field(validation_alias="OV kostenbestand")
    parking_times_file: Path = Field(validation_alias="parkeerzoektijden_bestand")
    public_transport_costs: PublicTransportCosts = Field(validation_alias="OV kosten")
    day_kinds: list[DayKind] = Field(validation_alias="dagsoort")
    time_costs_no_car: TimeCostsNoCar = Field(validation_alias="tijdkostenga")


@dataclass
class DataFile:
    path: Path = Field(validation_alias="bestand")
    used: bool = Field(validation_alias="gebruiken")


class Group(str, Enum):
    AllGroups = "alle groepen"


class Advanced(BaseModel):
    artificial_car_possension_file: DataFile = Field(validation_alias="kunstmab")
    additional_cost_file: DataFile = Field(validation_alias="additionele_kosten")
    parking_cost_file: DataFile = Field(validation_alias="parkeerkosten")
    groups: list[Group] = Field(validation_alias="welke_groepen")


@dataclass
class ChainHub:
    hub_name: str = Field(validation_alias="naam hub")
    used: bool = Field(validation_alias="gebruiken")


class Chains(BaseModel):
    chains: ChainHub = Field(validation_alias="chains")
    destination_file: DataFile = Field(validation_alias="bestemmingslijst")


@pytest.mark.parametrize("case", ["vlaanderen"])
def test_pydantic(case):
    test_dir = pathlib.Path("tests")
    project_dir = test_dir.joinpath(case).resolve()
    project = project_dir.joinpath(f"{case}.json")

    with open(project) as json_file:
        config = json.load(json_file)

    Project.model_validate(config["project"])
    Skims.model_validate(config["skims"])
    Advanced.model_validate(config["geavanceerd"])
    Chains.model_validate(config["ketens"])

    assert False
