import numpy as np
import pytest


@pytest.mark.parametrize(("alpha", "omega", "scaling"), [(0.125, 50, 1), (0.225, 10, 0.75), (0.12, 60, 0.95)])
@pytest.mark.parametrize(("travel_time", "weight_fraction"), [(0, 0.001), (20, 0.1), (60, 0.5), (120, 0.9)])
def test_decay_curve_and_inverse_round_trip(alpha, omega, scaling, travel_time, weight_fraction):
    from ikob.single_weights import decay_curve, inverse_decay_curve

    # a weight above the scaling is impossible, as the decay curve will never reach the scaling value
    weight = scaling * weight_fraction
    assert inverse_decay_curve(decay_curve(travel_time, alpha, omega, scaling), alpha, omega, scaling) == pytest.approx(
        travel_time, abs=1e-10
    )
    assert decay_curve(inverse_decay_curve(weight, alpha, omega, scaling), alpha, omega, scaling) == pytest.approx(
        weight, abs=1e-10
    )


@pytest.mark.parametrize("modality", ["Auto", "OV", "Fiets"])
def test_calculate_weights_threshold_and_monotonicity(modality):
    from ikob.configuration_definition import DecayCurveName
    from ikob.single_weights import calculate_weights

    # Prepare
    # Simple 1D progression of travel times.
    gtt = np.array(
        [
            [0.0, 10.0, 179.0, 180.0],
            [0.0, 10.0, 179.0, 180.0],
            [0.0, 10.0, 179.0, 180.0],
            [0.0, 10.0, 179.0, 180.0],
        ]
    )

    # Act
    weights = calculate_weights(gtt, modality=modality, decay_curve_name=DecayCurveName.WORK_AND_SOCIAL)

    # Assert
    # Hard threshold at 180 minutes.
    assert weights[0, 3] == 0.0

    # Monotonic decay
    assert weights[0, 1] > weights[0, 2]
    assert weights[0, 0] > weights[0, 1]


@pytest.mark.parametrize("selected_income", [None, "laag"])
def test_calculate_single_weights_writes_expected_keys(selected_income):
    import ikob.single_weights as sw
    from ikob.configuration_definition import DecayCurveName, TvomType
    from ikob.datasource import DataKey

    # Prepare
    pod = "Restdag"
    motive = "werk or something else"
    regime = "Basis"

    constant_gtt = np.array([[10.0, 20.0], [30.0, 40.0]])

    class _FakeGTT:
        def get(self, key: DataKey):
            # The unit under test calls many keys; for this test we just
            # need deterministic shape and non-zero under threshold.
            return constant_gtt

    config = {
        "__filename__": "pytest",
        "project": {
            "motief": {
                "naam": motive,
                "reizende populatie": "path",
                "bestemmingsplaatsen": "path",
                "TVOM": TvomType.WORK,
                "reistijdvervalscurve": DecayCurveName.WORK_AND_SOCIAL,
            },
            "beprijzingsregime": regime,
            "fiets of E-fiets": {"E-fiets": False},
            "paden": {
                "output_directory": "out",
                "skims_directory": "skims",
                "segs_directory": "segs",
            },
        },
        "skims": {
            "dagsoort": [pod],
        },
    }

    # Act
    weights = sw.calculate_single_weights(config, _FakeGTT(), selected_income=selected_income)  # type: ignore

    expected_incomes = (
        {selected_income} if selected_income is not None else {"laag", "middellaag", "middelhoog", "hoog"}
    )
    assert {key.income for key in weights.cache} == expected_incomes

    # Assert
    # A set of representative keys that must be produced.
    assert weights.get(DataKey("Fiets", part_of_day=pod, regime=regime, motive=motive, income="laag")).shape == (
        2,
        2,
    )
    assert weights.get(
        DataKey(
            "Auto",
            part_of_day=pod,
            income="laag",
            regime=regime,
            motive=motive,
            fuel_kind="fossiel",
        )
    ).shape == (2, 2)
    assert weights.get(
        DataKey(
            "OV",
            part_of_day=pod,
            income="laag",
            regime=regime,
            motive=motive,
        )
    ).shape == (2, 2)
