import numpy as np
import pytest


@pytest.mark.parametrize("modality", ["Auto", "OV", "Fiets"])
@pytest.mark.parametrize("preference", ["Auto", "OV", "Fiets"])
def test_calculate_weights_threshold_and_monotonicity(modality, preference):
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
    weights = calculate_weights(
        gtt, modality=modality, preference=preference, decay_curve_name=DecayCurveName.WORK_AND_SOCIAL
    )

    # Assert
    # Hard threshold at 180 minutes.
    assert weights[0, 3] == 0.0

    # Monotonic decay
    assert weights[0, 1] > weights[0, 2]
    assert weights[0, 0] > weights[0, 1]


def test_calculate_single_weights_writes_expected_keys():
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
    weights = sw.calculate_single_weights(config, _FakeGTT())  # type: ignore

    # Assert
    # A set of representative keys that must be produced.
    assert weights.get(DataKey("Fiets_vk", part_of_day=pod, regime=regime, motive=motive, income="laag")).shape == (
        2,
        2,
    )
    assert weights.get(
        DataKey(
            "Auto_vk",
            part_of_day=pod,
            income="laag",
            regime=regime,
            motive=motive,
            preference="Auto",
            fuel_kind="fossiel",
        )
    ).shape == (2, 2)
    assert weights.get(
        DataKey(
            "OV_vk",
            part_of_day=pod,
            income="laag",
            regime=regime,
            motive=motive,
            preference="OV",
        )
    ).shape == (2, 2)
