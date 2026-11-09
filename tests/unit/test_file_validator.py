from unittest.mock import ANY, Mock, call

import numpy as np
import pytest

from ikob.config import validate
from ikob.config.validate import FileValidator


@pytest.fixture
def config():
    return {
        "project": {
            "motief": {
                "reizende populatie": "segs/population.csv",
                "bestemmingsplaatsen": "segs/destinations.csv",
            },
            "verstedelijkingsscenario": "2023",
        },
        "skims": {"dagsoort": ["Ochtend", "Restdag"]},
        "geavanceerd": {"parkeerkosten": {"gebruiken": False}},
    }


@pytest.mark.parametrize("failed_stage", [None, "hubs", "segs", "motive", "skims"])
def test_validate_input_files_runs_all_stages(config, monkeypatch, caplog, failed_stage):
    validator = FileValidator(config)
    stages = Mock()
    for name in ("hubs", "segs", "motive", "skims"):
        getattr(stages, name).return_value = name != failed_stage
    monkeypatch.setattr(validate.Hubs, "validate", stages.hubs)
    monkeypatch.setattr(validator, "_segs_files_validation", stages.segs)
    monkeypatch.setattr(validator, "_motive_files_validation", stages.motive)
    monkeypatch.setattr(validator, "_skims_files_validation", stages.skims)

    assert validator.validate_input_files() is (failed_stage is None)

    assert stages.mock_calls == [call.hubs(config), call.segs(), call.motive(), call.skims()]
    assert ("Unable to run ikob" in caplog.text) is (failed_stage is not None)


@pytest.mark.parametrize("failed_file", [None, "CBS_autos_per_huishouden", "GeenRijbewijs"])
def test_segs_validation_checks_all_files(config, monkeypatch, caplog, failed_file):
    source = Mock()

    def read(filename, **kwargs):
        if filename == failed_file:
            raise OSError("Cannot read SEGS file")

    source.read.side_effect = read
    factory = Mock(return_value=source)
    monkeypatch.setattr(validate, "SegsSource", factory)

    assert FileValidator(config)._segs_files_validation() is (failed_file is None)

    factory.assert_called_once_with(config)
    assert source.read.call_args_list == [
        call("CBS_autos_per_huishouden"),
        call("Stedelijkheidsgraad"),
        call("GeenRijbewijs", id_store=ANY),
        call("GeenAuto", id_store=ANY),
        call("WelAuto", id_store=ANY),
        call("Voorkeuren", id_store=ANY),
        call("VoorkeurenGeenAuto", id_store=ANY),
    ]
    if failed_file is not None:
        assert failed_file in caplog.text
        assert "Cannot read SEGS file" in caplog.text
    else:
        assert not caplog.records


@pytest.mark.parametrize(
    "population, expected",
    [(np.zeros((2, 4)), True), (np.zeros((2, 3)), False), (OSError("Cannot read motive file"), False)],
    ids=["valid", "wrong-income-columns", "read-error"],
)
def test_motive_validation_checks_both_files(config, monkeypatch, caplog, population, expected):
    source = Mock()

    def read(filename, **kwargs):
        if filename == "population.csv":
            if isinstance(population, Exception):
                raise population
            return population
        return np.zeros((2, 4))

    source.read.side_effect = read
    monkeypatch.setattr(validate, "SegsSource", Mock(return_value=source))

    assert FileValidator(config)._motive_files_validation() is expected

    assert source.read.call_args_list == [
        call("population.csv", scenario="2023"),
        call("destinations.csv", scenario="2023"),
    ]
    assert ("population.csv" in caplog.text) is (not expected)


@pytest.mark.parametrize(
    "parking_times, expected",
    [
        (np.zeros((2, 2)), True),
        (np.zeros((2, 1)), False),
        (OSError("Cannot read parking times"), False),
    ],
    ids=["valid", "invalid-shape", "read-error"],
)
def test_skims_validation_checks_parking_times(config, monkeypatch, caplog, parking_times, expected):
    source = Mock()
    if isinstance(parking_times, Exception):
        source.read_parking_times.side_effect = parking_times
    else:
        source.read_parking_times.return_value = parking_times

    monkeypatch.setattr(validate, "SkimsSource", Mock(return_value=source))

    assert FileValidator(config)._skims_files_validation() is expected


@pytest.mark.parametrize(
    "parking_costs, use_costs, expected",
    [
        (np.zeros(2), True, True),
        (np.zeros((2, 2)), True, False),
        (OSError("Cannot read parking costs"), False, True),
        (OSError("Cannot read parking costs"), True, False),
    ],
    ids=["disabled", "valid", "invalid-shape", "read-error"],
)
def test_skims_validation_checks_parking_costs(config, monkeypatch, caplog, parking_costs, use_costs, expected):
    config["geavanceerd"]["parkeerkosten"]["gebruiken"] = use_costs
    source = Mock()
    source.read_parking_times.return_value = np.zeros((2, 2))
    costs_reader = Mock()
    if isinstance(parking_costs, Exception):
        costs_reader.side_effect = parking_costs
    else:
        costs_reader.return_value = parking_costs

    monkeypatch.setattr(validate, "SkimsSource", Mock(return_value=source))
    monkeypatch.setattr(validate, "read_csv_from_config", costs_reader)

    assert FileValidator(config)._skims_files_validation() is expected

    if use_costs:
        costs_reader.assert_called_once_with(config, key="geavanceerd", id="parkeerkosten")
    else:
        costs_reader.assert_not_called()


def test_skims_validation_continues_with_next_period_after_read_error(config, monkeypatch, caplog):
    source = Mock()
    source.read_parking_times.return_value = np.zeros((2, 2))
    source.read.side_effect = [OSError("Cannot read skim"), *[np.zeros((2, 2))] * 5]
    monkeypatch.setattr(validate, "SkimsSource", Mock(return_value=source))

    assert FileValidator(config)._skims_files_validation() is False

    assert source.read.call_args_list == [
        call("Auto_Tijd", "Ochtend"),
        call("Auto_Tijd", "Restdag"),
        call("Auto_Afstand", "Restdag"),
        call("Fiets_Tijd", "Restdag"),
        call("Fiets_Afstand", "Restdag", default=ANY),
        call("OV_Tijd", "Restdag"),
    ]
    assert "Cannot read skim" in caplog.text
