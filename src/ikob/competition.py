import logging
from dataclasses import replace
from pathlib import Path

import numpy as np
import numpy.typing as npt

from ikob import utils
from ikob.combined_weights import load_weight_matrix, weight_matrix_request
from ikob.datasource import DataKey, DataSource, DataType, SegsSource
from ikob.distribute_over_groups import CAR_PT_TYPES, INCOME_LEVELS, NUM_GROUPS_PER_INCOME_CLASS
from ikob.output_tables import assemble_income_tables

logger = logging.getLogger(__name__)


def compute_income_distributions(citizens_or_destinations: npt.NDArray[np.integer]):
    totals = citizens_or_destinations.sum(axis=1, keepdims=True)
    return np.divide(
        citizens_or_destinations,
        totals,
        out=np.zeros_like(citizens_or_destinations, dtype=utils.FLOAT_DTYPE),
        where=totals > 0,
    )


def competition_on_destinations(
    config,
    single_weights: DataSource,
    combined_weights: DataSource,
    origins: DataSource,
    *,
    selected_income: str | None = None,
    results: DataSource | None = None,
) -> DataSource:
    """
    For every zone it's determined if the zone has a (dis)advantage compared to other zones in reaching destinations.

    Corresponds to section D6 in the IKOB-algorithm.pdf.

    D6 defines a competition factor residents that discounts
    destinations with many competing residents.

    If a selected income is given, the full results cannot be assembled directly as they include overviews of
    competition across all income groups. The caller will have to call assemble_destination_outputs on the final datasource
    containing results for all income groups.
    """
    logger.info("Starting step: Compute competition on destinations")
    return competition(
        config,
        single_weights,
        combined_weights,
        origins,
        citizens=False,
        selected_income=selected_income,
        results=results,
    )


def competition_on_citizens(
    config,
    single_weights: DataSource,
    combined_weights: DataSource,
    origins: DataSource,
    *,
    selected_income: str | None = None,
    results: DataSource | None = None,
) -> DataSource:
    """
    For every zone it's determined if the zone has a (dis)advantage compared to other zones in attracting citizens.

    Corresponds to section D7 in the IKOB-algorithm.pdf.

    D7 is the "mirror" of D6: it defines a competition factor for jobs/destinations that discounts
    origins with many competing jobs/destinations.

    If a selected income is given, the full results cannot be assembled directly as they include overviews of
    competition across all income groups. The caller will have to call assemble_destination_outputs on the final datasource
    containing results for all income groups.
    """
    logger.info("Starting step: Compute competition on citizens")
    return competition(
        config,
        single_weights,
        combined_weights,
        origins,
        citizens=True,
        selected_income=selected_income,
        results=results,
    )


def competition(
    config,
    single_weights: DataSource,
    combined_weights: DataSource,
    origins: DataSource,
    citizens: bool = True,
    *,
    selected_income: str | None = None,
    results: DataSource | None = None,
) -> DataSource:
    if citizens:
        msg = "Competition for citizens."
    else:
        msg = "Competition for destinations."
    logger.info(msg)

    project_config = config["project"]
    skims_config = config["skims"]
    distribution_config = config["verdeling"]
    part_of_days = skims_config["dagsoort"]
    advanced_config = config["geavanceerd"]

    scenario = project_config["verstedelijkingsscenario"]
    regimes = project_config["beprijzingsregime"]
    motive_name = project_config["motief"]["naam"]
    traveling_population_path = Path(project_config["motief"]["reizende populatie"])
    destinations_path = Path(project_config["motief"]["bestemmingsplaatsen"])
    car_possession_groups = advanced_config["welke_groepen"]
    electric_percentage = distribution_config["Percelektrisch"]

    modalities = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]

    segs_source = SegsSource(config)

    traveling_population = segs_source.read(traveling_population_path.name, scenario=scenario)
    destinations = segs_source.read(destinations_path.name, scenario=scenario)

    income_distributions = compute_income_distributions(traveling_population if citizens else destinations)
    subtopic_competition = "inwoners" if citizens else "bestemmingen"
    # Matches the suffix in potential_companies.py and employment_opportunities.py
    competition_filename_suffix = "Pot" if citizens else "Ontpl"
    competitions = results if results is not None else DataSource(config, DataType.COMPETITION)

    if citizens:
        citizens_or_destinations = traveling_population
    else:
        citizens_or_destinations = destinations

    for car_possession_group in car_possession_groups:
        distribution_matrix = segs_source.read(
            "Verdeling_over_groepen",
            type_caster=utils.FLOAT_DTYPE,
            scenario=scenario,
            group=motive_name,
            modifier="alleen_autobezit" if car_possession_group == "alleen autobezit" else "",
            has_id_column=True,
        )

        for part_of_day in part_of_days:
            for i_income_group, income_group in enumerate(INCOME_LEVELS):
                K = electric_percentage.get(income_group) / 100

                if selected_income is not None and income_group != selected_income:
                    continue
                general_possibility_totals = []

                for modality in modalities:
                    key = DataKey(
                        utils.INCOME_VECTOR_RESULT_ID,
                        part_of_day=part_of_day,
                        motive=motive_name,
                        modality=modality,
                        income=income_group,
                        car_possession_group=car_possession_group,
                    )
                    reach = origins.get(key)

                    # Section D6/D7: `reach` is the previously computed reachability used as denominator.
                    # - citizens=False (D6 / competition_on_destinations): `reach` comes from D5 / reachable_population and is destination-side potential (how many
                    #   residents can reach each destination zone).
                    # - citizens=True  (D7 / competition_on_citizens): `reach` comes from D4 / reachable_destinations and is origin-side reachable opportunities
                    #   (how many jobs/places residents in an origin zone can reach).

                    competition_total = np.zeros(len(citizens_or_destinations), dtype=utils.FLOAT_DTYPE)
                    citizens_or_destinations_per_reach = citizens_or_destinations.T[i_income_group] / np.where(
                        reach > 0, reach, 1.0
                    )
                    # cache the matrix vector products, this is much more memory friendly than caching the matrix itself
                    competition_vectors_cache = {}

                    for i_group, car_pt_types in enumerate(
                        CAR_PT_TYPES, start=i_income_group * NUM_GROUPS_PER_INCOME_CLASS
                    ):
                        distribution = distribution_matrix[:, i_group]
                        income_distribution = income_distributions[:, i_income_group]

                        weights, weight_key, electric_key = weight_matrix_request(
                            single_weights,
                            combined_weights,
                            car_pt_types,
                            modality,
                            motive_name,
                            regimes,
                            part_of_day,
                            income_group,
                            K,
                        )
                        cache_key = (weights is combined_weights, weight_key, electric_key)

                        # Section D6/D7 competition term:
                        # Compute a scarcity/competition ratio per zone and propagate it through the origin-destination weights.
                        # - citizens=False (D6 / competition_on_destinations): `citizens_or_destinations` is $A_{ib}$ (jobs/places per
                        #   destination). Dividing by `reach` discounts destinations with many competing residents.
                        # - citizens=True  (D7 / competition_on_citizens): `citizens_or_destinations` is $I_{ih}$ (residents per
                        #   origin). Dividing by `reach` discounts origins with many reachable opportunities.
                        if cache_key not in competition_vectors_cache:
                            matrix = load_weight_matrix(weights, weight_key, electric_key, K)
                            competition_vectors_cache[cache_key] = matrix @ citizens_or_destinations_per_reach
                        competition = competition_vectors_cache[cache_key]

                        # aggregation to income-class level:
                        # We sum across all groups whose income level matches `income_group`.
                        # The `distribution` and `income_distribution` scaling makes this an income-class level
                        # score rather than a raw per-group score.
                        competition_total += (
                            competition * distribution / np.where(income_distribution > 0, income_distribution, 1)
                        )

                    key = DataKey(
                        id=utils.INCOME_VECTOR_RESULT_ID,
                        part_of_day=part_of_day,
                        subtopic=subtopic_competition,
                        income=income_group,
                        motive=motive_name,
                        modality=modality,
                        car_possession_group=car_possession_group,
                        is_intermediate=True,
                    )
                    competitions.set(key, competition_total)

                    general_possibility_totals.append(competitions.get(key))

                general_totals_transpose = utils.transpose(general_possibility_totals)
                key = DataKey(
                    id=f"{competition_filename_suffix}_conc",
                    part_of_day=part_of_day,
                    subtopic=subtopic_competition,
                    income=income_group,
                    motive=motive_name,
                    car_possession_group=car_possession_group,
                    header=modalities,
                )
                competitions.set(key, general_totals_transpose)

    if selected_income is None:
        assemble_competition_outputs(config, competitions, citizens=citizens)
    return competitions


def assemble_competition_outputs(config, competitions: DataSource, *, citizens: bool):
    project = config["project"]
    segs = SegsSource(config)
    population = segs.read(
        Path(project["motief"]["reizende populatie"]).name, scenario=project["verstedelijkingsscenario"]
    )
    destinations = segs.read(
        Path(project["motief"]["bestemmingsplaatsen"]).name, scenario=project["verstedelijkingsscenario"]
    )
    multiplier = population if citizens else destinations
    condition = destinations > 0 if citizens else population > 0
    prefix = "Pot" if citizens else "Ontpl"
    for key, values in assemble_income_tables(competitions, ["laag", "middellaag", "middelhoog", "hoog"]):
        # Rename the per income group result for output
        competitions.set(replace(key, id=f"{prefix}_conc"), values)
        # D6/D7 regional aggregation weights each zone by jobs (Ontpl) or residents (Pot).
        # Store the per-zone numerator contribution; regional summation and division happen later.

        # Sections D6/D7 of the algorithm region result is a population/destination-weighted average of reachability
        # Store the per-zone numerator contribution here. Regional summation and division by total population could happen later.
        competitions.set(replace(key, id=f"{prefix}_concproduct"), np.where(condition, values * multiplier, 0))
