import filecmp
import logging
import pathlib
import shutil

import pandas as pd

from ikob.ikobrunner import run_scripts

logger = logging.getLogger(__name__)


def _file_to_frame(path: pathlib.Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        try:
            return pd.read_csv(path, header=None, index_col="zone")
        except ValueError:
            return pd.read_csv(path, index_col="zone")
    raise ValueError(f"Calling file to frame with unknown extension {path.suffix}. Must be .csv")


def _is_equal_csv(result: pathlib.Path, reference: pathlib.Path) -> bool:
    """Compare CSV files up to numerical tolerances."""
    result_frame = _file_to_frame(result)
    reference_frame = _file_to_frame(reference)

    try:
        pd.testing.assert_frame_equal(result_frame, reference_frame, rtol=1e-5)
        return True
    except AssertionError as err:
        logger.warning(f"File {result} differs from reference:\n{err}")
        return False


def _is_equal_file(result: pathlib.Path, reference: pathlib.Path) -> bool:
    """Compare if two files are the same.

    For CSV (.csv) files a specialized comparison
    is used to allow for some numerical tolerances to exist between
    both files.
    """
    if result.suffix != reference.suffix:
        logger.warning(f"File {result} and {reference} have different suffix.")
        return False

    if result.suffix in [".csv"]:
        return _is_equal_csv(result, reference)

    return filecmp.cmp(result, reference, shallow=False)


def _same_directory(dcmp: filecmp.dircmp, allow_too_many_results: bool = False) -> bool:
    """Recursively compare directories for differing files."""
    same = True
    # File is only present in one of the directory trees.
    result_files_only = dcmp.left_only
    reference_files_only = dcmp.right_only
    if reference_files_only or (result_files_only and not allow_too_many_results):
        msg = f"Files only in result: {result_files_only}\nFiles only in reference: {reference_files_only}"
        logger.warning(msg)
        same = False

    for filepath in dcmp.diff_files:
        result = pathlib.Path(dcmp.left) / filepath
        reference = pathlib.Path(dcmp.right) / filepath
        if not _is_equal_file(result, reference):
            same = False

    # Recursively compare directories.
    for sub_dcmp in dcmp.subdirs.values():
        if not _same_directory(sub_dcmp, allow_too_many_results=allow_too_many_results):
            same = False

    return same


def compare_directories(result, reference, allow_too_many_results: bool = False) -> bool:
    assert result.is_dir(), f"Result directory {result} should exist."
    assert reference.is_dir(), f"Reference directory {result} should exist."
    return _same_directory(filecmp.dircmp(result, reference), allow_too_many_results=allow_too_many_results)


def remove_directory(dir: pathlib.Path):
    if dir.exists() and dir.is_dir():
        shutil.rmtree(dir)


def test_end_to_end():
    test_dir = pathlib.Path("tests")
    project_dir = test_dir.joinpath("vlaanderen").resolve()
    project = project_dir.joinpath("vlaanderen.json")

    suffixes = ["resultaten", "basis", "tussenresultaten"]
    compare_dirs = [project_dir / "vlaanderen" / s for s in suffixes]

    # Delete old results if still present
    remove_directory(project_dir / "vlaanderen")

    # End-to-end test should not skip any steps: all scripts should pass.
    run_scripts(project, write_weights=True)

    for result_dir in compare_dirs:
        reference_dir = project_dir / "reference" / result_dir.stem
        assert compare_directories(result_dir, reference_dir)

    # Clean up files if test succeeds
    remove_directory(project_dir / "vlaanderen")


def test_end_to_end_skipping_steps():
    test_dir = pathlib.Path("tests")
    project_dir = test_dir.joinpath("vlaanderen").resolve()
    project = project_dir.joinpath("vlaanderen.json")

    suffixes = ["resultaten", "basis", "tussenresultaten"]
    compare_dirs = [project_dir / "vlaanderen" / s for s in suffixes]

    # Delete old results if still present
    remove_directory(project_dir / "vlaanderen")

    for i in range(8):
        skip_steps = [*[True] * i, *[False] * (8 - i)]
        logger.warning(skip_steps)
        run_scripts(project, skip_steps=skip_steps, write_weights=True, write_intermediate_results=True)

        for result_dir in compare_dirs:
            reference_dir = project_dir / "reference" / result_dir.stem
            # Allow too many results to account for the intermediate results that we need to write out
            # to continue from any step
            assert compare_directories(result_dir, reference_dir, allow_too_many_results=True)

    # Clean up files if test succeeds
    remove_directory(project_dir / "vlaanderen")
