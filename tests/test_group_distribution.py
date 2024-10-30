import logging

from ikob.ikobconfig import getConfigFromArgs
from ikob.group_distribution import distribute_over_groups

logger = logging.getLogger(__name__)


def test_group_distribution():
    """Data set showing division by zero in group_distribution calculations.

    This input configuration ``eb-eindhoven.json`` ran into division by
    zero problems within ``group_distribution`` that were not encountered
    in other end-to-end tests. In specific, this example does show 0.0/0.0
    divisions resulting in ``nan`` rather than ``inf`` (which were covered).
    """
    project_file = "tests/eb-eindhoven/eb-eindhoven.json"
    logger.info("Reading project file: %s.", project_file)
    config = getConfigFromArgs(project_file)
    distribute_over_groups(config)
