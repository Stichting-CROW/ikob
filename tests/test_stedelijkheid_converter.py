import pathlib
import numpy as np

import pytest
from ikob.datasource import DataSource
from ikob.ikobconfig import getConfigFromArgs
from ikob.Routines import csvintlezen
from ikob.stedelijkheidsgraad_to_parkeerzoektijden import (
    stedelijkheidfile_to_parkeerzoektijdenfile,
)

from tests.test_end_to_end import is_equal_file


def test_stedelijkheid_converter(tmp_path):
    input = pathlib.Path("tests/vlaanderen/SEGS/Stedelijkheidsgraad.csv")
    reference = pathlib.Path("tests/vlaanderen/SEGS/Parkeerzoektijd.csv")
    result = tmp_path.with_suffix(".csv")

    stedelijkheidfile_to_parkeerzoektijdenfile(input, tmp_path)
    assert is_equal_file(result, reference)


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
