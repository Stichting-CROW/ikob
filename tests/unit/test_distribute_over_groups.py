import numpy as np
import pytest

from ikob.configuration_definition import DecayCurveName, TvomType
from tests.unit.conftest import SegsCapture


def _minimal_config():
    return {
        "__filename__": "pytest",
        "project": {
            "verstedelijkingsscenario": "2023",
            "motieven": ["werk"],
            "paden": {
                "segs_directory": "segs",
                "output_directory": "out",
                "skims_directory": "skims",
            },
            "motief": {
                "naam": "motive",
                "reizende populatie": "Beroepsbevolking_inkomensklasse",
                "bestemmingsplaatsen": "path",
                "TVOM": TvomType.WORK,
                "reistijdvervalscurve": DecayCurveName.WORK_AND_SOCIAL,
            },
        },
        "verdeling": {
            "GratisOVpercentage": 0.03,
        },
        "geavanceerd": {
            "kunstmab": {"gebruiken": False, "bestand": "unused.csv"},
        },
    }


def _expected_header(income_group: str) -> list[str]:
    return [
        f"GratisAuto_{income_group}",
        f"GratisAuto_GratisOV_{income_group}",
        f"WelAuto_GratisOV_{income_group}",
        f"WelAuto_vkAuto_{income_group}",
        f"WelAuto_vkNeutraal_{income_group}",
        f"WelAuto_vkFiets_{income_group}",
        f"WelAuto_vkOV_{income_group}",
        f"GeenAuto_GratisOV_{income_group}",
        f"GeenAuto_vkNeutraal_{income_group}",
        f"GeenAuto_vkFiets_{income_group}",
        f"GeenAuto_vkOV_{income_group}",
        f"GeenRijbewijs_GratisOV_{income_group}",
        f"GeenRijbewijs_vkNeutraal_{income_group}",
        f"GeenRijbewijs_vkFiets_{income_group}",
        f"GeenRijbewijs_vkOV_{income_group}",
    ]


def _expected_block(
    *,
    zone_index: int,
    income_index: int,
    segs: dict[tuple[str, str], np.ndarray],
    free_pt_percentage: float,
    scenario: str = "2023",
) -> np.ndarray:
    """Compute expected output values for one income class (e.g. 'laag') for one zone.

    This mirrors the calculations in `ikob.distribute_over_groups.distribute_over_groups`.
    It's not ideal that the test in part reimplements the same logic as the code under test, but still the tested code is significantly more obtuse.
    """

    # Fixed values from the implementation.
    free_car_per_income = [0, 0.02, 0.175, 0.275]
    preferences = ["Auto", "Neutraal", "Fiets", "OV"]
    preferences_no_car = ["Neutraal", "Fiets", "OV"]

    car_possessions_per_household = np.array(segs[("CBS_autos_per_huishouden", "")], dtype=float)
    urbanization_grade = np.array(segs[("Stedelijkheidsgraad", "")], dtype=int)
    urbanization = [int(sgg) - 1 for sgg in urbanization_grade]

    no_license_segs = np.array(segs[("GeenRijbewijs", "")], dtype=float)
    no_car_segs = np.array(segs[("GeenAuto", "")], dtype=float)
    with_car_segs = np.array(segs[("WelAuto", "")], dtype=float)
    preferences_segs = np.array(segs[("Voorkeuren", "")], dtype=float)
    preferences_no_car_segs = np.array(segs[("VoorkeurenGeenAuto", "")], dtype=float)
    citizens_per_class = np.array(segs[("Beroepsbevolking_inkomensklasse", scenario)], dtype=float)

    income_distribution_over_population = citizens_per_class[zone_index, :] / np.sum(citizens_per_class[zone_index, :])

    income_share_of_population = income_distribution_over_population[income_index]

    urb = urbanization[zone_index]
    # theoretical_car_possession = sum over income classes of (percentage_with_car_per_income_class * income_distribution_over_population)
    share_of_population_with_car = np.sum((with_car_segs[urb] / 100) * income_distribution_over_population)
    car_possessions_per_household = car_possessions_per_household[zone_index]

    # car_possession_per_income_class is computed from the theoretical car possession using a correction factor
    #   car_possession_per_income_class = theoretical_car_possession_per_income_class * (car_possession / theoretical_car_possession)

    # From the docs: if car_possessions_per_household / 100 < share_of_population_with_car:
    #   Then few households will have multiple cars and the car_possession is equal to the share of population with a car.
    # Otherwise:
    #   The car_possessions is equal to the theoretical share of the population with a car.
    car_possession_correction = 1.0
    if car_possessions_per_household / 100 < share_of_population_with_car:
        car_possession_correction = (car_possessions_per_household / 100) / share_of_population_with_car

    with_car_share_theoretical = with_car_segs[urb][income_index] / 100
    with_car = with_car_share_theoretical * car_possession_correction

    if car_possession_correction != 1:
        no_car_correction = (1 - with_car) / (1 - with_car_share_theoretical)
    else:
        no_car_correction = 1.0

    no_car_with_license = no_car_segs[urb][income_index] / 100 * no_car_correction
    no_license = no_license_segs[urb][income_index] / 100 * no_car_correction

    free_car = with_car * free_car_per_income[income_index]
    no_free_car = with_car - free_car

    out: list[float] = []
    # GratisAuto_{income_group}
    out.append(free_car * (1 - free_pt_percentage) * income_share_of_population)
    # GratisAuto_GratisOV_{income_group}
    out.append(free_car * free_pt_percentage * income_share_of_population)
    # WelAuto_GratisOV_{income_group}
    out.append(no_free_car * free_pt_percentage * income_share_of_population)
    # WelAuto_vk* columns
    for i_pref in range(len(preferences)):
        share_pref = no_free_car * (1 - free_pt_percentage) * (preferences_segs[urb][i_pref] / 100)
        out.append(share_pref * income_share_of_population)
    # GeenAuto_GratisOV + GeenAuto_vk*
    out.append(no_car_with_license * free_pt_percentage * income_share_of_population)
    for i_pref in range(len(preferences_no_car)):
        share_pref = no_car_with_license * (1 - free_pt_percentage) * (preferences_no_car_segs[urb][i_pref] / 100)
        out.append(share_pref * income_share_of_population)
    # GeenRijbewijs_GratisOV + GeenRijbewijs_vk*
    out.append(no_license * free_pt_percentage * income_share_of_population)
    for i_pref in range(len(preferences_no_car)):
        share_pref = no_license * (1 - free_pt_percentage) * (preferences_no_car_segs[urb][i_pref] / 100)
        out.append(share_pref * income_share_of_population)

    return np.array(out, dtype=float)


@pytest.mark.parametrize("zone_index", (0, 1))
@pytest.mark.parametrize(
    ("income_group", "income_index"), (("laag", 0), ("middellaag", 1), ("middelhoog", 2), ("hoog", 3))
)
def test_distribute_over_groups_computation(zone_index, income_group, income_index, segs_capture):
    from ikob.distribute_over_groups import distribute_population_over_groups

    # Prepare
    # The `segs` dict represents the in-memory contents of the SEGS datasource.
    # Keys are `(dataset_id, scenario)`.
    segs = {
        # Per-zone average cars per household (used to derive free-car share).
        ("CBS_autos_per_huishouden", ""): np.array([0.5, 1.5]) * 100,
        # Urbanization grade per zone.
        ("Stedelijkheidsgraad", ""): np.array([1, 2]),
        # Urbanization grades x 4 income classes (low..high): counts/shares by car/license status.
        ("GeenRijbewijs", ""): np.array([[10, 10, 10, 10], [5, 5, 5, 5]]),
        ("GeenAuto", ""): np.array([[10, 10, 10, 10], [5, 5, 5, 5]]),
        ("WelAuto", ""): np.array([[80, 80, 80, 80], [90, 90, 90, 90]]),
        # Urbanization grades x 4 preference categories (model-specific preference bins).
        ("Voorkeuren", ""): np.array([[25, 25, 25, 25], [25, 25, 25, 25]]),
        # Urbanization grades x 3 preferences (only for the "GeenAuto" segment).
        ("VoorkeurenGeenAuto", ""): np.array([[34, 33, 33], [34, 33, 33]]),
        # Per-zone x 4 income classes: population counts per income class.
        ("Beroepsbevolking_inkomensklasse", "2023"): np.array([[10, 10, 10, 10], [20, 20, 20, 20]]),
    }
    capture: SegsCapture = segs_capture(segs)

    config = _minimal_config()
    # Act
    distribute_population_over_groups(config)

    # Assert
    # distribute_over_groups should write a CSV for the computed distribution.
    writes = [
        w
        for w in capture.writes_csv
        if w["id"] == "Verdeling_over_groepen" and w["group"] == "motive" and w["modifier"] == ""
    ]
    assert writes, "Expected distribute_over_groups to call SegsSource.write_csv"

    assert len(writes) == 1
    data = writes[0]["data"]
    header = writes[0]["header"]

    # 2 zones, 60 group categories. The total number of groups over which the population is distributed is 60.
    assert data.shape == (2, 60)

    # The total distribution of the population over all groups sums to 1 per zone.
    np.testing.assert_allclose(data.sum(axis=1), np.ones(2))

    # Each income block is a partition of that income's population share.
    # The 60 total groups can be split up in 4 sections of 15 groups belonging to each income group.
    # With these segs, each income class is an equal share of the total population: 0.25.
    for income_group_i in range(4):
        start = income_group_i * 15
        end = start + 15
        np.testing.assert_allclose(data[0, start:end].sum(), 0.25)

    # Assert every output value for the income group
    # using the same calculations as the implementation.
    income_slice = slice(income_index * 15, (income_index + 1) * 15)
    assert header[income_slice] == _expected_header(income_group)
    expected = _expected_block(
        zone_index=zone_index,
        income_index=income_index,
        segs=segs,
        free_pt_percentage=config["verdeling"]["GratisOVpercentage"],
    )
    np.testing.assert_allclose(data[zone_index, income_slice], expected)


def test_distribution_of_income_group_is_independent_of_population_distribution(segs_capture):
    """
    The distribution of an income group over the groups is not related to how the total population is distributed among income groups.
    """
    from ikob.distribute_over_groups import distribute_population_over_groups

    # Two zones identical in every way except income distribution.
    # Note: WelAuto, GeenAuto, GeenRijbewijs must sum to 100 for each income class.
    segs = {
        ("CBS_autos_per_huishouden", ""): np.array([0.8, 0.8]) * 100,
        ("Stedelijkheidsgraad", ""): np.array([1, 1]),
        ("GeenRijbewijs", ""): np.array([[40, 10, 10, 10], [40, 10, 10, 10]]),
        ("GeenAuto", ""): np.array([[50, 10, 10, 10], [50, 10, 10, 10]]),
        ("WelAuto", ""): np.array([[10, 80, 80, 80], [10, 80, 80, 80]]),
        ("Voorkeuren", ""): np.array([[25, 25, 25, 25], [25, 25, 25, 25]]),
        ("VoorkeurenGeenAuto", ""): np.array([[34, 33, 33], [34, 33, 33]]),
        ("Beroepsbevolking_inkomensklasse", "2023"): np.array([[209, 209, 209, 208], [2, 209, 209, 208]]),
    }
    capture: SegsCapture = segs_capture(segs)
    config = _minimal_config()
    distribute_population_over_groups(config)

    writes = [
        w
        for w in capture.writes_csv
        if w["id"] == "Verdeling_over_groepen" and w["group"] == "motive" and w["modifier"] == ""
    ]
    data = writes[0]["data"]

    # Normalize the 'laag' income group distribution (columns 0-15) for each zone.
    laag_dist_zone0 = data[0, 0:15] / data[0, 0:15].sum()
    laag_dist_zone1 = data[1, 0:15] / data[1, 0:15].sum()
    # Do the same for 'high' income group distribution (column 45-60)
    hoog_dist_zone0 = data[0, 45:60] / data[0, 45:60].sum()
    hoog_dist_zone1 = data[1, 45:60] / data[1, 45:60].sum()

    # The normalized distribution within the income group should be identical
    # regardless of how the total population is distributed across income classes.
    np.testing.assert_allclose(laag_dist_zone0, laag_dist_zone1)
    np.testing.assert_allclose(hoog_dist_zone0, hoog_dist_zone1)

    # It's also true that the sizes of all the groups belonging to a single income group should sum to the to the size of the income group in the total population
    np.testing.assert_allclose(data.sum(axis=1), np.ones(2))
    np.testing.assert_allclose(
        data[0, 0:15].sum(),
        segs[("Beroepsbevolking_inkomensklasse", "2023")][0][0]
        / segs[("Beroepsbevolking_inkomensklasse", "2023")][0].sum(),
    )
    np.testing.assert_allclose(
        data[1, 0:15].sum(),
        segs[("Beroepsbevolking_inkomensklasse", "2023")][1][0]
        / segs[("Beroepsbevolking_inkomensklasse", "2023")][1].sum(),
    )


def test_distribution_of_groups_dependent_on_car_possession_correction_factor(segs_capture):
    """
    The distribution of an income group over the groups is not related to how the total population is distributed among income groups
    EXCEPT when the car possession correction factor is relevant.
    The correction factor is dependent on the % of households with a car in a zone.
    This is computed from the the "WelAuto" segs combined with "Beroepsbevolking_inkomensklasse",
    and therefore dependent on the the distribution of the population over income groups.

    The car possession factor only comes in to play when the the % of households with a car is *more* than the average number of cars per household.
    So a small 'CBS_autos_per_huishouden' achieves this state.

    """
    from ikob.distribute_over_groups import distribute_population_over_groups

    # Two zones identical in every way except income distribution.
    # Note: WelAuto, GeenAuto, GeenRijbewijs must sum to 100 for each income class.
    segs = {
        ("CBS_autos_per_huishouden", ""): np.array([0.05, 0.05]) * 100,
        ("Stedelijkheidsgraad", ""): np.array([1, 1]),
        ("GeenRijbewijs", ""): np.array([[40, 10, 10, 10], [40, 10, 10, 10]]),
        ("GeenAuto", ""): np.array([[50, 10, 10, 10], [50, 10, 10, 10]]),
        ("WelAuto", ""): np.array([[10, 80, 80, 80], [10, 80, 80, 80]]),
        ("Voorkeuren", ""): np.array([[25, 25, 25, 25], [25, 25, 25, 25]]),
        ("VoorkeurenGeenAuto", ""): np.array([[34, 33, 33], [34, 33, 33]]),
        ("Beroepsbevolking_inkomensklasse", "2023"): np.array([[209, 209, 209, 208], [2, 209, 209, 208]]),
    }
    capture: SegsCapture = segs_capture(segs)
    config = _minimal_config()
    distribute_population_over_groups(config)

    print(capture.writes_csv)
    writes = [
        w
        for w in capture.writes_csv
        if w["id"] == "Verdeling_over_groepen" and w["group"] == "motive" and w["modifier"] == ""
    ]
    data = writes[0]["data"]

    # Normalize the 'laag' income group distribution (columns 0-15) for each zone.
    laag_dist_zone0 = data[0, 0:15] / data[0, 0:15].sum()
    laag_dist_zone1 = data[1, 0:15] / data[1, 0:15].sum()
    # Do the same for 'high' income group distribution (column 45-60)
    hoog_dist_zone0 = data[0, 45:60] / data[0, 45:60].sum()
    hoog_dist_zone1 = data[1, 45:60] / data[1, 45:60].sum()

    # The normalized distribution within the income group should be identical
    # regardless of how the total population is distributed across income classes.
    np.testing.assert_raises(AssertionError, np.testing.assert_allclose, laag_dist_zone0, laag_dist_zone1)
    np.testing.assert_raises(AssertionError, np.testing.assert_allclose, hoog_dist_zone0, hoog_dist_zone1)

    # It's also true that the sizes of all the groups belonging to a single income group should sum to the to the size of the income group in the total population
    np.testing.assert_allclose(data.sum(axis=1), np.ones(2))
    np.testing.assert_allclose(
        data[0, 0:15].sum(),
        segs[("Beroepsbevolking_inkomensklasse", "2023")][0][0]
        / segs[("Beroepsbevolking_inkomensklasse", "2023")][0].sum(),
    )
    np.testing.assert_allclose(
        data[1, 0:15].sum(),
        segs[("Beroepsbevolking_inkomensklasse", "2023")][1][0]
        / segs[("Beroepsbevolking_inkomensklasse", "2023")][1].sum(),
    )
