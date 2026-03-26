import numpy as np
import pytest


@pytest.fixture(
    params=[
        np.array([[0.8, 0.15, 0.05], [0.2, 0.7, 0.1], [0.1, 0.2, 0.5]]),
        np.eye(3) * 0.8,
    ],
    ids=["complicated_matrix", "diagonal_matrix"],
)
def reachable_population_setup(request, monkeypatch, segs_capture):
    """Common setup for reachable population tests.

    The setup regards reachable working population by employers"""
    import ikob.reachable_population as pc

    pod = "Restdag"
    motive = "werk or something else"
    regime = "Basis"

    # Job counts should not matter for total potential companies (citizens reaching destinations).
    jobs_income = np.array(
        [
            [100.0, 0.0, 0.0, 40.0],
            [100.0, 0.0, 0.0, 20.0],
            [80.0, 0.0, 0.0, 30.0],
        ]
    )

    # All zones have the same working population for low income.
    working_pop_income = np.array(
        [
            [50.0, 50.0, 0, 100.0],
            [100.0, 100.0, 0, 200.0],
            [75.0, 75.0, 0, 150.0],
        ]
    )

    # Distribution matrix for target group: 3 zones × 60 columns.
    # Total results should not be dependent on this distribution.
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
            ("Beroepsbevolking_inkomensklasse", "2023"): working_pop_income,
            ("Arbeidsplaatsen_inkomensklasse", "2023"): jobs_income,
            ("Verdeling_over_groepen", "2023"): distribution,
        }
    )

    class _Weights:
        def get(self, _key):
            return request.param

    # Capture csv writes
    csv_writes = []

    def capture_write_csv(self, data, key, header=None):
        csv_writes.append({"data": data, "key": key, "header": header})

    monkeypatch.setattr(pc.DataSource, "write_csv", capture_write_csv)

    config = {
        "__filename__": "pytest",
        "project": {
            "verstedelijkingsscenario": "2023",
            "beprijzingsregime": regime,
            "motief": {
                "naam": motive,
                "reizende populatie": "path/to/Beroepsbevolking_inkomensklasse",
                "bestemmingsplaatsen": "path/to/Arbeidsplaatsen_inkomensklasse",
            },
            "welke_inkomensgroepen": ["laag", "middellaag", "middelhoog", "hoog"],
            "paden": {
                "output_directory": "out",
                "skims_directory": "skims",
                "segs_directory": "segs",
            },
        },
        "skims": {"dagsoort": [pod]},
        "verdeling": {"Percelektrisch": {"laag": 0.0, "middellaag": 0.0, "middelhoog": 0.0, "hoog": 0.0}},
        "geavanceerd": {"welke_groepen": ["alle groepen"]},
    }

    origins = pc.reachable_population(config, _Weights(), _Weights())  # type: ignore

    return {
        "origins": origins,
        "csv_writes": csv_writes,
        "pod": pod,
        "motive": motive,
        "working_pop_income": working_pop_income,
        "jobs_income": jobs_income,
        "weight_matrix": request.param,
    }


# As defined in reachable_population
modalities = ["Fiets", "Auto", "OV", "Auto_Fiets", "OV_Fiets", "Auto_OV", "Auto_OV_Fiets"]


@pytest.mark.parametrize("modality", modalities)
@pytest.mark.parametrize(
    ("income_group", "income_index"), (("laag", 0), ("middellaag", 1), ("middelhoog", 2), ("hoog", 3))
)
def test_reachable_population_totals(modality, income_group, income_index, reachable_population_setup):
    """Reachable citizens (potential workforce) totals are independent of job counts and distribution over groups."""
    from ikob.datasource import DataKey

    origins = reachable_population_setup["origins"]
    pod = reachable_population_setup["pod"]
    motive = reachable_population_setup["motive"]
    working_pop_income = reachable_population_setup["working_pop_income"]
    weight_matrix = reachable_population_setup["weight_matrix"]

    key = DataKey(
        "Totaal",
        part_of_day=pod,
        income=income_group,
        group="alle groepen",
        motive=motive,
        modality=modality,
    )
    totals = origins.get(key)
    expected_totaal = np.array(weight_matrix.T @ working_pop_income[:, income_index].T)
    np.testing.assert_allclose(totals, expected_totaal)


@pytest.mark.parametrize("modality", modalities)
def test_reachable_population_pot_totaal(modality, reachable_population_setup):
    """Pot_totaal csv output shows reachability by income group, independent of distribution over groups."""

    csv_writes = reachable_population_setup["csv_writes"]
    working_pop_income = reachable_population_setup["working_pop_income"]
    jobs_income = reachable_population_setup["jobs_income"]
    weight_matrix = reachable_population_setup["weight_matrix"]

    # Test Pot_totaal csv write (per modality, showing reachability by income group)
    pot_totaal_writes = [w for w in csv_writes if w["key"].id == "Pot_totaal" and w["key"].modality == modality]
    assert len(pot_totaal_writes) == 1, f"Expected exactly one Pot_totaal write for modality {modality}"

    pot_totaal_data = pot_totaal_writes[0]["data"]
    pot_totaal_expected = np.array(
        [weight_matrix.T @ working_pop_income[:, i].T for i in range(working_pop_income.shape[1])]
    ).T
    # Output files get rounded to integers for presentation
    np.testing.assert_array_equal(pot_totaal_data, np.round(pot_totaal_expected))

    # Test Pot_totaalproduct csv write (product of reachability and jobs)
    pot_product_writes = [w for w in csv_writes if w["key"].id == "Pot_totaalproduct" and w["key"].modality == modality]
    assert len(pot_product_writes) == 1, f"Expected exactly one Pot_totaalproduct write for modality {modality}"

    pot_product_data = pot_product_writes[0]["data"]
    # Product should be reachability * jobs per zone and income
    # Output files get rounded to integers for presentation
    np.testing.assert_array_equal(pot_product_data, np.round(pot_totaal_expected * jobs_income))
