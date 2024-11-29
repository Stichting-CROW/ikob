import logging
import pathlib

from test_end_to_end import compare_directories, remove_directory

from ikob.group_distribution import distribute_over_groups
from ikob.ikobconfig import getConfigFromArgs

logger = logging.getLogger(__name__)


def test_group_distribution():
    """Data set showing division by zero in group_distribution calculations.

    This input configuration ``eb-eindhoven.json`` ran into division by
    zero problems within ``group_distribution`` that were not encountered
    in other end-to-end tests. In specific, this example does show 0.0/0.0
    divisions resulting in ``nan`` rather than ``inf`` (which were covered).
    """
    case = "eb-eindhoven"
    project_dir = pathlib.Path(f"tests/{case}/")
    config = getConfigFromArgs(project_dir / f"{case}.json")

    distribute_over_groups(config)

    msg = "Result and reference directories are not equal."
    result_dir = project_dir / case
    reference_dir = project_dir / "reference"
    assert compare_directories(result_dir, reference_dir), msg

    # Clean up files if test succeeds
    remove_directory(result_dir)
