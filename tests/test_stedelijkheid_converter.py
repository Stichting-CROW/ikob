import pathlib
import numpy as np

import pytest
from ikob.datasource import DataSource
from ikob.ikobconfig import getConfigFromArgs
from ikob.Routines import csvintlezen
from ikob.stedelijkheidsgraad_to_parkeerzoektijden import (
    stedelijkheid_to_parkeerzoektijd
)


def test_stedelijkheid_converter():
    segs_dir = pathlib.Path("tests/vlaanderen/SEGS")
    reference = csvintlezen(segs_dir / "Parkeerzoektijd.csv")
    stedelijkheid = csvintlezen(segs_dir / "Stedelijkheidsgraad.csv")
    parkeerzoektijden = stedelijkheid_to_parkeerzoektijd(stedelijkheid)
    assert np.all(parkeerzoektijden == reference)


def test_generate_parkeerzoektijden_datasource():
    case = "vlaanderen"
    project_dir = pathlib.Path("tests") / case
    project_file = project_dir.joinpath(f"{case}.json")
    reference = csvintlezen(project_dir / "SEGS" / "Parkeerzoektijd.csv")

    # Read test file on disk given in configurationf file.
    config = getConfigFromArgs(project_file)
    datasource = DataSource(config, config["__filename__"])
    assert np.all(reference == datasource.read_parkeerzoektijden())

    # Remove path from config and fall back to expected location.
    del config["skims"]["parkeerzoektijden_bestand"]
    datasource = DataSource(config, config["__filename__"])
    assert np.all(reference == datasource.read_parkeerzoektijden())

    # Set config to unkown path, trigger conversion on the fly.
    config["skims"]["parkeerzoektijden_bestand"] = "unset"
    datasource = DataSource(config, config["__filename__"])
    assert np.all(reference == datasource.read_parkeerzoektijden())


def test_assert_failed_parkeerzoektijden_conversion():
    case = "vlaanderen"
    project_dir = pathlib.Path("tests") / case
    project_file = project_dir.joinpath(f"{case}.json")

    # Overwrite SEGS directory to trigger failure in converting
    # parkeerzoektijden as stedelijkheidsgraag is not present.
    config = getConfigFromArgs(project_file)
    config["skims"]["parkeerzoektijden_bestand"] = "unset"
    config["project"]["paden"]["segs_directory"] = "unset"

    datasource = DataSource(config, config["__filename__"])
    with pytest.raises(AssertionError):
        _ = datasource.read_parkeerzoektijden()
