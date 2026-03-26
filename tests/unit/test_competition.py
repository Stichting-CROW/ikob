import numpy as np
import pytest

from ikob.datasource import DataKey


@pytest.mark.parametrize(("ratio_electric"), ([0, 0.3, 1.0]))
def test_get_weight_matrix_auto_with_electric_ratio(ratio_electric):
    """Test that get_weight_matrix correctly blends fossil and electric car matrices."""
    from ikob.competition import get_weight_matrix

    fossil_matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
    electric_matrix = np.array([[10.0, 20.0], [30.0, 40.0]])

    class MockWeights:
        def get(self, key: DataKey):
            if key.fuel_kind == "fossiel":
                return fossil_matrix
            elif key.fuel_kind == "elektrisch":
                return electric_matrix
            return None

    single_weights = MockWeights()
    combined_weights = MockWeights()

    result = get_weight_matrix(
        single_weights,  # type: ignore
        combined_weights,  # type: ignore
        group="WelAuto_vkAuto_laag",
        modality="Auto",
        motive="werk",
        regime="Basis",
        part_of_day="Spits",
        income="laag",
        ratio_electric=ratio_electric,
    )

    expected = ratio_electric * electric_matrix + (1 - ratio_electric) * fossil_matrix
    np.testing.assert_array_equal(result, expected)


def test_get_weight_matrix_ov_modality():
    """Test that get_weight_matrix handles OV (public transport) correctly."""
    from ikob.competition import get_weight_matrix

    single_matrix = np.array([[5, 6], [7, 8]])
    combined_matrix = np.array([[99, 100], [101, 102]])

    class MockSingleWeights:
        def get(self, key: DataKey):
            return single_matrix

    class MockCombinedWeights:
        def get(self, key: DataKey):
            return combined_matrix

    single_weights = MockSingleWeights()
    combined_weights = MockCombinedWeights()

    result = get_weight_matrix(
        single_weights,  # type: ignore
        combined_weights,  # type: ignore
        group="GeenAuto_vkOV_laag",
        modality="OV",
        motive="werk",
        regime="Basis",
        part_of_day="Spits",
        income="laag",
        ratio_electric=0.0,
    )
    # OV modality should use single_weights
    np.testing.assert_array_equal(result, single_matrix)


def test_get_weight_matrix_combined_modality():
    """Test that get_weight_matrix handles combined modalities correctly."""
    from ikob.competition import get_weight_matrix

    single_matrix = np.array([[1, 2], [3, 4]])
    combined_matrix = np.array([[9, 10], [11, 12]])

    class MockSingleWeights:
        def get(self, key: DataKey):
            return single_matrix

    class MockCombinedWeights:
        def get(self, key: DataKey):
            return combined_matrix

    single_weights = MockSingleWeights()
    combined_weights = MockCombinedWeights()

    # Test with combined modality like AutoOV (car + public transport)
    result = get_weight_matrix(
        single_weights,  # type: ignore
        combined_weights,  # type: ignore
        group="WelAuto_vkOV_laag",
        modality="AutoOV",
        motive="werk",
        regime="Basis",
        part_of_day="Spits",
        income="laag",
        ratio_electric=0.0,
    )
    # Combined modality should use combined_weights
    np.testing.assert_array_equal(result, combined_matrix)


# as defined in competition
modalities = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]


@pytest.mark.parametrize("modality", modalities)
@pytest.mark.parametrize(
    ("income_group", "income_index"), (("laag", 0), ("middellaag", 1), ("middelhoog", 2), ("hoog", 3))
)
@pytest.mark.parametrize(
    "weight_matrix",
    [
        np.array([[0.8, 0.15, 0.05], [0.2, 0.7, 0.1], [0.1, 0.2, 0.5]]),
        np.eye(3) * 0.8,
    ],
    ids=["complicated_matrix", "diagonal_matrix"],
)
def test_competition_on_jobs_per_capita_sensitivity(
    modality, income_group, income_index, monkeypatch, segs_capture, weight_matrix
):
    import ikob.competition as comp
    from ikob.datasource import DataKey

    # Prepare
    pod = "Restdag"
    motive = "werk or somethings else"
    regime = "Basis"

    citizens_income = np.array(
        [
            [100.0, 0.0, 0.0, 40.0],
            [100.0, 0.0, 0.0, 20.0],
            [80.0, 0.0, 0.0, 30.0],
        ]
    )
    jobs_income_reachable = np.array(
        [
            [50.0, 500.0, 0.0, 25.0],
            [25.0, 3.1415, 0.0, 50.0],
            [75.0, 75.0, 0, 150.0],
        ]
    )
    jobs_income_present = np.array(
        [
            [50.0, 50.0, 0, 100.0],
            [100.0, 100.0, 0, 200.0],
            [75.0, 75.0, 0, 150.0],
        ]
    )

    # Distribution matrix for target group: 3 zones × 60 columns (15 per income class).
    # The distribution over the groups should be inline with the actual working population.
    distribution_per_income = np.zeros((3, 15), dtype=float)
    distribution_per_income[0, 0] = 1.0
    distribution_per_income[1, 0] = 0.5
    distribution_per_income[1, 1] = 0.5
    distribution_per_income[2, 0] = 0.3
    distribution_per_income[2, 1] = 0.4
    distribution_per_income[2, 2] = 0.3

    distribution = np.zeros((3, 60), dtype=float)
    distribution[:, 0:15] = distribution_per_income * (1 / 4)
    distribution[:, 15:30] = distribution_per_income * (1 / 4)
    distribution[:, 45:60] = distribution_per_income * (1 / 2)

    segs_capture(
        {
            ("reizende populatie bestand", "2023"): citizens_income,
            ("bestemmingen bestand", "2023"): jobs_income_present,
            ("Verdeling_over_groepen", "2023"): distribution,
        }
    )

    monkeypatch.setattr(comp, "get_weight_matrix", lambda *args, **kwargs: weight_matrix)
    monkeypatch.setattr(comp.DataSource, "write_csv", lambda *args, **kwargs: None)

    class _Origins:
        def get(self, _key: DataKey):
            # Reach of each zone to each zone
            if _key.income == "laag":
                return jobs_income_reachable[:, 0]
            elif _key.income == "middellaag":
                return jobs_income_reachable[:, 1]
            elif _key.income == "middelhoog":
                return jobs_income_reachable[:, 2]
            elif _key.income == "hoog":
                return jobs_income_reachable[:, 3]

    class _Weights:
        def get(self, _key):
            return weight_matrix

    which_groups = "alle groepen"
    config = {
        "__filename__": "pytest",
        "project": {
            "verstedelijkingsscenario": "2023",
            "beprijzingsregime": regime,
            "motief": {
                "naam": motive,
                "reizende populatie": "path/to/reizende populatie bestand",
                "bestemmingsplaatsen": "path/to/bestemmingen bestand",
            },
            "paden": {
                "output_directory": "out",
                "skims_directory": "skims",
                "segs_directory": "segs",
            },
        },
        "skims": {"dagsoort": [pod]},
        "verdeling": {"Percelektrisch": {"laag": 0.0, "middellaag": 0.0, "middelhoog": 0.0, "hoog": 0.0}},
        "geavanceerd": {"welke_groepen": [which_groups]},
    }

    # Act
    competitions = comp.competition_on_destinations(config, _Weights(), _Weights(), _Origins())  # type: ignore

    # Assert
    key = DataKey(
        id="Totaal",
        part_of_day=pod,
        subtopic="bestemmingen",
        income=income_group,
        motive=motive,
        modality=modality,
        group=which_groups,
    )
    total = competitions.get(key)

    # Intended per-capita behavior under diagonal reach: (jobs_low / citizens_low) * weight
    expected = np.where(
        jobs_income_reachable[:, income_index] > 0,
        weight_matrix @ (jobs_income_present[:, income_index] / jobs_income_reachable[:, income_index]),
        0.0,
    )
    np.testing.assert_allclose(total, expected)
