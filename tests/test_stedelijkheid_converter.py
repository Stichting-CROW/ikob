from ikob.stedelijkheidsgraad_to_parkeerzoektijden import (
    stedelijkheidfile_to_parkeerzoektijdenfile,
)

from tests.test_end_to_end import is_equal_file

import pathlib


def test_stedelijkheid_converter(tmp_path):
    input = pathlib.Path("tests/vlaanderen/SEGS/Stedelijkheidsgraad.csv")
    reference = pathlib.Path("tests/vlaanderen/SEGS/Parkeerzoektijd.csv")
    result = tmp_path.with_suffix(".csv")

    stedelijkheidfile_to_parkeerzoektijdenfile(input, tmp_path)
    assert is_equal_file(result, reference)
