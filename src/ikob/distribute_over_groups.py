import itertools
import logging
from pathlib import Path

import numpy as np
import numpy.typing as npt

from ikob import utils
from ikob.datasource import SegsSource, read_csv_from_config

logger = logging.getLogger(__name__)


def _validate_car_possession_segs(
    with_car_segs: npt.NDArray[np.integer],
    no_car_segs: npt.NDArray[np.integer],
    no_license_segs: npt.NDArray[np.integer],
    income_levels: list[str],
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
    - preference for a specific modality
    - the level of access to a car (e.g. no car, no drivers license)
    - the presence of a free modality (e.g. a free (company) car, or free public transport)

    These group definitions are stored as strings. For example:
    - WelAuto_GratisOV_middelhoog is the slice of the population with car, with free public transport, and a medium-high income (people with free pt always have pt as their preferred modality.
    - GeenAuto_vkFiets_laag is the slice of the population with no car, a preference for transport by bike, and a low income.

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
    income_levels = ["laag", "middellaag", "middelhoog", "hoog"]
    preferences = ["Auto", "Neutraal", "Fiets", "OV"]
    preferences_no_car = ["Neutraal", "Fiets", "OV"]
    kinds = ["GratisAuto", "WelAuto", "GeenAuto", "GeenRijbewijs"]

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
        min_car_possession = list(
            itertools.starmap(min, zip(car_possessions_per_household_segs, artificial_car_possession_segs))
        )

    # Read SEGS input files. See tables 1-3 of IKOB-algorithm.pdf
    no_license_segs = segs_source.read("GeenRijbewijs")
    no_car_segs = segs_source.read("GeenAuto")
    with_car_segs = segs_source.read("WelAuto")

    # Validate that the car possession data is consistent
    _validate_car_possession_segs(with_car_segs, no_car_segs, no_license_segs, income_levels)

    # Tables 6-7 of IKOB-algorithm.pdf
    preferences_segs = segs_source.read("Voorkeuren")
    preferences_no_car_segs = segs_source.read("VoorkeurenGeenAuto")

    header = []
    for ink in income_levels:
        for srt in kinds:
            if srt == "GratisAuto":
                header.append(f"{srt}_{ink}")
                header.append(f"{srt}_GratisOV_{ink}")
            elif srt == "WelAuto":
                header.append(f"{srt}_GratisOV_{ink}")
                for vk in preferences:
                    header.append(f"{srt}_vk{vk}_{ink}")
            else:
                header.append(f"{srt}_GratisOV_{ink}")
                for vkg in preferences_no_car:
                    header.append(f"{srt}_vk{vkg}_{ink}")

    total_survey = []
    total_car_possession_survey = []
    survey_per_income_class = []

    free_car = []
    no_free_car = []
    no_car_with_license = []

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)

    citizens_totals = np.sum(traveling_population, axis=1)

    # Avoid division by zero by inserting ones. Afterwards, make
    # sure to zero out entries that would have been divided by zero.
    citizens_totals[citizens_totals == 0] = 1
    income_distributions = traveling_population / citizens_totals[:, None]
    income_distributions[citizens_totals == 0][:] = 0

    for i, income_distribution in enumerate(income_distributions):
        total_survey.append([])
        total_car_possession_survey.append([])
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
            car_possession_shares = min_car_possession[i] / 100

        # Car possessions, license possessions, income classes.
        for i_income in range(len(income_levels)):
            with_car_share_theoretical = with_car_segs[urbanization[i]][i_income] / 100
            with_car = with_car_share_theoretical * car_possession_correction
            if car_possession_correction != 1:
                no_car_correction = (1 - with_car) / (1 - with_car_share_theoretical)
            else:
                no_car_correction = 1

            no_car_with_license = no_car_segs[urbanization[i]][i_income] / 100 * no_car_correction
            no_license = no_license_segs[urbanization[i]][i_income] / 100 * no_car_correction

            # Step 2 of section B of IKOB-algorithm.pdf
            # Also computes free pt data
            income_share = income_distribution[i_income]

            free_car = with_car * free_car_per_income[i_income]
            no_free_car = with_car - free_car
            free_car_share = free_car * (1 - free_pt_percentage) * income_share
            total_survey[i].append(free_car_share)
            survey_per_income_class[i].append(free_car_share / with_car)

            free_car_and_pt_share = free_car * free_pt_percentage * income_share
            total_survey[i].append(free_car_and_pt_share)
            survey_per_income_class[i].append(free_car_and_pt_share / with_car)

            free_pt_share = no_free_car * free_pt_percentage * income_share
            total_survey[i].append(free_pt_share)
            survey_per_income_class[i].append(free_pt_share / with_car)

            # Step 3 of section B of IKOB-algorithm.pdf
            for i_preference in range(len(preferences)):
                share_preference = (
                    no_free_car * (1 - free_pt_percentage) * preferences_segs[urbanization[i]][i_preference] / 100
                )
                preference_share = share_preference * income_share
                total_survey[i].append(preference_share)
                survey_per_income_class[i].append(preference_share / with_car)

            no_car_free_pt_share = no_car_with_license * free_pt_percentage * income_share
            total_survey[i].append(no_car_free_pt_share)
            survey_per_income_class[i].append(0)

            for i_preference in range(len(preferences_no_car)):
                share_preference = (
                    no_car_with_license
                    * (1 - free_pt_percentage)
                    * preferences_no_car_segs[urbanization[i]][i_preference]
                    / 100
                )
                preference_share = share_preference * income_share
                total_survey[i].append(preference_share)
                survey_per_income_class[i].append(0)

            no_license_free_pt_share = no_license * free_pt_percentage * income_share
            total_survey[i].append(no_license_free_pt_share)
            survey_per_income_class[i].append(0)

            for i_preference in range(len(preferences_no_car)):
                share_preference = (
                    no_license * (1 - free_pt_percentage) * preferences_no_car_segs[urbanization[i]][i_preference] / 100
                )
                preference_share = share_preference * income_share
                total_survey[i].append(preference_share)
                survey_per_income_class[i].append(0)

    logger.debug("Total car possessions: %s", total_car_possession_survey)
    segs_source.write_csv(
        survey_per_income_class,
        "Verdeling_over_groepen",
        scenario=scenario,
        group=motive_name,
        modifier="alleen_autobezit",
        header=header,
        index=utils.CsvIndex.zone_index(len(total_survey)),
    )
    segs_source.write_csv(
        total_survey,
        "Verdeling_over_groepen",
        scenario=scenario,
        group=motive_name,
        header=header,
        index=utils.CsvIndex.zone_index(len(total_survey)),
    )
