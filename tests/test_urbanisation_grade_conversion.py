import pathlib

import numpy as np
import pytest

from ikob.datasource import read_parking_times
from ikob.ikobconfig import getConfigFromArgs
from ikob.urbanisation_grade_to_parking_times import \
    urbanisation_grade_to_parking_times
from ikob.utils import read_csv_int


def test_stedelijkheid_converter():
    segs_dir = pathlib.Path("tests/vlaanderen/SEGS")
    reference = read_csv_int(segs_dir / "Parkeerzoektijd.csv")
    stedelijkheid = read_csv_int(segs_dir / "Stedelijkheidsgraad.csv")
    parkeerzoektijden = urbanisation_grade_to_parking_times(stedelijkheid)
    assert np.all(parkeerzoektijden == reference)


def test_generate_parkeerzoektijden():
    case = "vlaanderen"
    project_dir = pathlib.Path("tests") / case
    project_file = project_dir.joinpath(f"{case}.json")
    reference = read_csv_int(project_dir / "SEGS" / "Parkeerzoektijd.csv")

    # Read test file on disk given in configurationf file.
    config = getConfigFromArgs(project_file)
    assert np.all(reference == read_parking_times(config))

    # Remove path from config and fall back to expected location.
    del config["skims"]["parkeerzoektijden_bestand"]
    assert np.all(reference == read_parking_times(config))

    # Set config to unkown path, trigger conversion on the fly.
    config["skims"]["parkeerzoektijden_bestand"] = "unset"
    assert np.all(reference == read_parking_times(config))


def test_assert_failed_parkeerzoektijden_conversion():
    case = "vlaanderen"
    project_dir = pathlib.Path("tests") / case
    project_file = project_dir.joinpath(f"{case}.json")

    # Overwrite SEGS directory to trigger failure in converting
    # parkeerzoektijden as stedelijkheidsgraag is not present.
    config = getConfigFromArgs(project_file)
    config["skims"]["parkeerzoektijden_bestand"] = "unset"
    config["project"]["paden"]["segs_directory"] = "unset"

    with pytest.raises(AssertionError):
        _ = read_parking_times(config)
