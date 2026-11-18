import logging
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import numpy.typing as npt

from ikob.datasource import SegsSource, read_csv_from_config
from ikob.utils import URBANIZATION_GRADE_ID_STORE

logger = logging.getLogger(__name__)


INCOME_LEVELS = ("laag", "middellaag", "middelhoog", "hoog")
CAR_PT_TYPES = (
    ("GratisAuto", "OV"),
    ("GratisAuto", "GratisOV"),
    ("Auto", "GratisOV"),
    ("Auto", "OV"),
    ("GeenAuto", "GratisOV"),
    ("GeenAuto", "OV"),
    ("GeenRijbewijs", "GratisOV"),
    ("GeenRijbewijs", "OV"),
)
NUM_GROUPS_PER_INCOME_CLASS = len(CAR_PT_TYPES)


def _validate_car_possession_segs(
    with_car_segs: npt.NDArray[np.integer],
    no_car_segs: npt.NDArray[np.integer],
    no_license_segs: npt.NDArray[np.integer],
    income_levels: Sequence[str],
):
    """
    Validate that WelAuto, GeenAuto, and GeenRijbewijs sum to 100
    for each urbanization grade and income class

    These three categories should represent the complete population (those with a car,
    those without a car but with a license, and those without a license), so they must
    sum to 100%.

    Since the percentages are rounded to integers, a valid sum may equal either 99 or 100.

    Args:
        with_car_segs: WelAuto SEGS data (urbanization grades x income classes)
        no_car_segs: GeenAuto SEGS data (urbanization grades x income classes)
        no_license_segs: GeenRijbewijs SEGS data (urbanization grades x income classes)
        income_levels: List of income level names for logging
    """
    for urb_idx in range(len(with_car_segs)):
        for income_idx in range(len(income_levels)):
            total = (
                with_car_segs[urb_idx][income_idx]
                + no_car_segs[urb_idx][income_idx]
                + no_license_segs[urb_idx][income_idx]
            )
            if total != 99 and total != 100:  # Allow rounding errors
                logger.warning(
                    f"SEGS data validation warning: For urbanization grade {urb_idx + 1}, "
                    f"income class '{income_levels[income_idx]}', "
                    f"WelAuto + GeenAuto + GeenRijbewijs = {total} (expected ~100). "
                    f"Values: WelAuto={with_car_segs[urb_idx][income_idx]}, "
                    f"GeenAuto={no_car_segs[urb_idx][income_idx]}, "
                    f"GeenRijbewijs={no_license_segs[urb_idx][income_idx]}. "
                    f"This may lead to incorrect distribution calculations."
                )


def distribute_population_over_groups(config):
    """
    Distribute the population in each zone over a number of 'groups'

    These groups refer to slices of the population who's mobility should be computed in their own way.
    These groups are defined by:
    - income class
    - the level of access to a car (e.g. no car, no drivers license)
    - the presence of a free modality (e.g. a free (company) car, or free public transport)

    These group definitions are stored as strings. For example:
    - WelAuto_GratisOV_middelhoog has a car, free public transport, and a medium-high income.
    - GeenAuto_laag has no car, a driver's license, and a low income.

    Corresponds to section B in IKOB-algorithm.pdf

    This step does not work with a data source like the other steps, but instead writes the result to file.
    """
    logger.info("Starting step: Distribute groups over zones")

    project_config = config["project"]
    verdeling_config = config["verdeling"]
    advanced_config = config["geavanceerd"]

    # Ophalen van instellingen
    scenario = project_config["verstedelijkingsscenario"]
    artificial = advanced_config["kunstmab"]["gebruiken"]
    # This seems to be Table 5 of IKOB-algorithm.pdf, although this uses a flat percentage for all urbanization grades
    free_pt_percentage = verdeling_config["GratisOVpercentage"]
    motive_name = project_config["motief"]["naam"]
    traveling_population_path = Path(project_config["motief"]["reizende populatie"])

    # Vaste waarden
    segs_source = SegsSource(config)

    car_possessions_per_household_segs = segs_source.read("CBS_autos_per_huishouden")
    urbanization_grade_segs = segs_source.read("Stedelijkheidsgraad")
    # Decrement one to account for zero-based indexing later on.
    urbanization = [int(sgg) - 1 for sgg in urbanization_grade_segs]

    # See table 4 of section B in IKOB-algorithm.pdf for the source
    free_car_per_income = [0, 0.02, 0.175, 0.275]
    min_car_possession = car_possessions_per_household_segs

    if artificial:
        artificial_car_possession_segs = read_csv_from_config(config, key="geavanceerd", id="kunstmab", type_caster=int)
        min_car_possession = list(map(min, car_possessions_per_household_segs, artificial_car_possession_segs))

    # Read SEGS input files. See tables 1-3 of IKOB-algorithm.pdf
    no_license_segs = segs_source.read("GeenRijbewijs", id_store=URBANIZATION_GRADE_ID_STORE)
    no_car_segs = segs_source.read("GeenAuto", id_store=URBANIZATION_GRADE_ID_STORE)
    with_car_segs = segs_source.read("WelAuto", id_store=URBANIZATION_GRADE_ID_STORE)

    # Validate that the car possession data is consistent
    _validate_car_possession_segs(with_car_segs, no_car_segs, no_license_segs, INCOME_LEVELS)

    header = []
    total_survey = []
    survey_per_income_class = []

    def add_group(
        zone_index: int, income: str, car_pt_types: tuple[str, str], share: float, car_owner_share: float
    ) -> None:
        expected_types = CAR_PT_TYPES[len(total_survey[zone_index]) % NUM_GROUPS_PER_INCOME_CLASS]
        if car_pt_types != expected_types:
            raise ValueError(f"Expected car/PT types {expected_types}, got {car_pt_types}")
        total_survey[zone_index].append(share)
        survey_per_income_class[zone_index].append(car_owner_share)
        if zone_index == 0:
            car_type, pt_type = car_pt_types
            # This renaming scheme is to keep output headers equal to old code
            car_label = "WelAuto" if car_type == "Auto" else car_type
            pt_label = "_GratisOV" if pt_type == "GratisOV" else ""
            header.append(f"{car_label}{pt_label}_{income}")

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)

    citizens_totals = np.sum(traveling_population, axis=1)

    # Avoid division by zero by inserting ones. Afterwards, make
    # sure to zero out entries that would have been divided by zero.
    citizens_totals[citizens_totals == 0] = 1
    income_distributions = traveling_population / citizens_totals[:, None]
    income_distributions[citizens_totals == 0][:] = 0

    for i, income_distribution in enumerate(income_distributions):
        total_survey.append([])
        survey_per_income_class.append([])
        # First determine theoretical car and possessions.
        # See Step 1 in section B of IKOB-algorithm.pdf

        # Car possession per income class (with_car) is computed from the theoretical car possession (with_car_share_theoretical) using a correction factor
        # based on zone statistics on actual car possession per household and the theoretical car possession based on the income distribution and urbanization grade.
        # First the correction factor is computed, then car possessions is computed per income class.

        car_possession_share = []
        for id, wc in zip(income_distribution, with_car_segs[urbanization[i]]):
            car_possession_share.append(id * wc / 100)
        car_possession_shares = sum(car_possession_share)

        # Determine if car possessions are lower.
        car_possession_correction = 1
        if min_car_possession[i] > 0 and min_car_possession[i] / 100 < car_possession_shares:
            car_possession_correction = (min_car_possession[i] / 100) / car_possession_shares

        # Car possessions, license possessions, income classes.
        for i_income, income in enumerate(INCOME_LEVELS):
            with_car_share_theoretical = with_car_segs[urbanization[i]][i_income] / 100
            with_car = with_car_share_theoretical * car_possession_correction
            if car_possession_correction != 1:
                no_car_correction = (1 - with_car) / (1 - with_car_share_theoretical)
            else:
                no_car_correction = 1

            no_car_with_license = no_car_segs[urbanization[i]][i_income] / 100 * no_car_correction
            no_license = no_license_segs[urbanization[i]][i_income] / 100 * no_car_correction

            # Step 2/3 of section B of IKOB-algorithm.pdf
            # Also computes free pt data
            income_share = income_distribution[i_income]

            free_car = with_car * free_car_per_income[i_income]
            no_free_car = with_car - free_car
            free_car_share = free_car * (1 - free_pt_percentage) * income_share
            add_group(i, income, ("GratisAuto", "OV"), free_car_share, free_car_share / with_car)

            free_car_and_pt_share = free_car * free_pt_percentage * income_share
            add_group(i, income, ("GratisAuto", "GratisOV"), free_car_and_pt_share, free_car_and_pt_share / with_car)

            free_pt_share = no_free_car * free_pt_percentage * income_share
            add_group(i, income, ("Auto", "GratisOV"), free_pt_share, free_pt_share / with_car)

            car_share = no_free_car * (1 - free_pt_percentage) * income_share
            add_group(i, income, ("Auto", "OV"), car_share, car_share / with_car)

            no_car_free_pt_share = no_car_with_license * free_pt_percentage * income_share
            add_group(i, income, ("GeenAuto", "GratisOV"), no_car_free_pt_share, 0)

            no_car_share = no_car_with_license * (1 - free_pt_percentage) * income_share
            add_group(i, income, ("GeenAuto", "OV"), no_car_share, 0)

            no_license_free_pt_share = no_license * free_pt_percentage * income_share
            add_group(i, income, ("GeenRijbewijs", "GratisOV"), no_license_free_pt_share, 0)

            no_license_share = no_license * (1 - free_pt_percentage) * income_share
            add_group(i, income, ("GeenRijbewijs", "OV"), no_license_share, 0)

    segs_source.write_csv(
        survey_per_income_class,
        "Verdeling_over_groepen",
        scenario=scenario,
        group=motive_name,
        modifier="alleen_autobezit",
        header=header,
    )
    segs_source.write_csv(total_survey, "Verdeling_over_groepen", scenario=scenario, group=motive_name, header=header)
