import filecmp
import logging
import pathlib
import shutil

import pandas as pd
import pytest

from ikob.ikobrunner import run_scripts

logger = logging.getLogger(__name__)


def file_to_frame(path: pathlib.Path) -> pd.DataFrame:
    if path.suffix == ".xlsx":
        return pd.read_excel(path)

    if path.suffix == ".csv":
        try:
            return pd.read_csv(path, dtype=float, header=None)
        except ValueError:
            return pd.read_csv(path, dtype=float)


def is_equal_excel_csv(result: pathlib.Path, reference: pathlib.Path) -> bool:
    """Compare Excel/CSV files up to numerical tolerances."""
    result_frame = file_to_frame(result)
    reference_frame = file_to_frame(reference)

    try:
        pd.testing.assert_frame_equal(result_frame, reference_frame,
                                      rtol=1e-5, atol=1e-8)
        return True
    except AssertionError as err:
        logger.warning(f"File {result} differs from reference:\n{err}")
        return False


def is_equal_file(result: pathlib.Path, reference: pathlib.Path) -> bool:
    """Compare if two files are the same.

    For Excel (.xlsx) and CSV (.csv) files a specialised comparison
    is used to allow for some numerical tolerances to exist between
    both files.
    """
    if result.suffix != reference.suffix:
        logger.warning(f"File {result} and {reference} have different suffix.")
        return False

    if result.suffix in [".xlsx", ".csv"]:
        return is_equal_excel_csv(result, reference)

    return filecmp.cmp(result, reference, shallow=False)


def same_directory(dcmp: filecmp.dircmp) -> bool:
    """Recursively compare directories for differing files."""

    # File is only present in one of the directory trees.
    if dcmp.left_only or dcmp.right_only:
        msg = (
            "Result and reference directories contain different files:"
            f"{dcmp.left_only}, {dcmp.right_only}"
        )
        logger.warning(msg)
        return False

    for filepath in dcmp.diff_files:
        result = pathlib.Path(dcmp.left) / filepath
        reference = pathlib.Path(dcmp.right) / filepath
        if not is_equal_file(result, reference):
            return False

    # Recursively compare directories.
    for sub_dcmp in dcmp.subdirs.values():
        if not same_directory(sub_dcmp):
            return False

    return True


def compare_directories(result, reference) -> bool:
    assert result.is_dir(), f"Result directory {result} should exist."
    assert reference.is_dir(), f"Reference directory {result} should exist."
    return same_directory(filecmp.dircmp(result, reference))


def remove_directory(dir: pathlib.Path):
    if dir.exists() and dir.is_dir():
        shutil.rmtree(dir)


@pytest.mark.parametrize("case", ["vlaanderen", "eindhoven-500"])
def test_end_to_end(case):
    test_dir = pathlib.Path("tests")
    project_dir = test_dir.joinpath(case).resolve()
    project = project_dir.joinpath(f"{case}.json")

    suffixes = ["resultaten", "basis", "tussenresultaten"]
    compare_dirs = [project_dir / case / s for s in suffixes]

    # Delete old results if still present
    for result_dir in compare_dirs:
        remove_directory(result_dir)

    # End-to-end test should not skip any steps: all scripts should pass.
    run_scripts(project, write_weights=True)

    for result_dir in compare_dirs:
        reference_dir = project_dir / "reference" / result_dir.stem
        assert compare_directories(result_dir, reference_dir)

    # Clean up files if test succeeds
    for result_dir in compare_dirs:
        remove_directory(result_dir)
