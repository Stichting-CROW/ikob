from ikob.ikobrunner import stappen, run_scripts
import pathlib
import pytest
import filecmp
import shutil
import pandas as pd


def file_to_frame(path: pathlib.Path) -> pd.DataFrame:
    if path.suffix == ".xlsx":
        return pd.read_excel(path)

    if path.suffix == ".csv":
        try:
            return pd.read_csv(path, dtype=float, header=None)
        except ValueError:
            return pd.read_csv(path, dtype=float)


def is_equal_file(dcmp: filecmp.dircmp, file: pathlib.Path) -> bool:
    """Compare reportedly differing files with some tolerance slack.

    The Excel and CSV files in the reference set are first directly
    compared, ignoring any numerical tolerances, which fail when
    floating point data is stored. This reevaluates the file equality
    by comparing their DataFrame representations up to a given relative
    and absolute tolerances.
    """
    result = pathlib.Path(dcmp.left).joinpath(file)
    reference = pathlib.Path(dcmp.right).joinpath(file)

    # Only reevaluate Excel/CSV files.
    if file.suffix not in [".xlsx", ".csv"]:
        return False

    result_frame = file_to_frame(result)
    reference_frame = file_to_frame(reference)

    try:
        pd.testing.assert_frame_equal(result_frame, reference_frame,
                                      rtol=1e-5, atol=1e-8)
        return True
    except AssertionError as err:
        print(f"File {result} differs from reference:\n{err}")
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
