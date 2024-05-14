from ikob.ikobrunner import stappen, run_scripts
import pathlib
import pytest
import filecmp
import shutil
import pandas as pd


def is_equal_excel_file(result, reference) -> bool:
    """Compare two xlsx files within numerical tolerances.

    The files are considered equal if their pandas.DataFrame representations
    are considered equal up to given relative and absolute tolerance differences.
    """
    result_frame = pd.read_excel(result)
    reference_frame = pd.read_excel(reference)
    # These match the defaults of assert_frame_equal.
    rtol = 1e-5
    atol = 1e-8
    try:
        pd.testing.assert_frame_equal(result_frame, reference_frame, rtol=rtol, atol=atol)
        return True
    except AssertionError as err:
        print(f"Excel file {result} differs from reference:\n{err}")
        return False


def is_equal_file(dcmp: filecmp.dircmp, file: pathlib.Path) -> bool:
    """Compare files in detail with filetype specific comparisons."""

    result = pathlib.Path(dcmp.left).joinpath(file)
    reference = pathlib.Path(dcmp.right).joinpath(file)

    if file.suffix == ".xlsx":
        return is_equal_excel_file(result, reference)

    return False


def same_directory(dcmp: filecmp.dircmp) -> bool:
    """Recursively compare directories for differing files."""

    # File is only present in one of the directory trees.
    if dcmp.left_only or dcmp.right_only:
        return False

    for filepath in dcmp.diff_files:
        if not is_equal_file(dcmp, pathlib.Path(filepath)):
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


@pytest.mark.parametrize("case", ["vlaanderen"])
def test_end_to_end(case):
    test_dir = pathlib.Path("tests")
    project_dir = test_dir.joinpath(case).resolve()
    project = project_dir.joinpath(f"{case}.json")

    suffixes = ["Resultaten", "Basis"]
    compare_dirs = [project_dir / case / s for s in suffixes]

    # Delete old results if still present
    for result_dir in compare_dirs:
        remove_directory(result_dir)

    # End-to-end test should not skip any steps: all scripts should pass.
    skip_tests = [False for _ in stappen]
    for step, result in run_scripts(project, skip_tests):
        assert result is None, f"Step {step} should pass."

    for result_dir in compare_dirs:
        reference_dir = project_dir / "reference" / result_dir.stem
        assert compare_directories(result_dir, reference_dir)

    # Clean up files if test succeeds
    for result_dir in compare_dirs:
        remove_directory(result_dir)
