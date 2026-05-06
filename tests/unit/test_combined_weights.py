import pytest


def test_has_preference_rules():
    from ikob.combined_weights import has_preference

    assert has_preference(kind_car="GeenAuto", kind_pt="OV", preference="Auto") is False
    assert has_preference(kind_car="GeenRijbewijs", kind_pt="GratisOV", preference="Neutraal") is False
    assert has_preference(kind_car="GeenRijbewijs", kind_pt="GratisOV", preference="OV") is True

    assert has_preference(kind_car="GratisAuto", kind_pt="OV", preference="Auto") is True
    assert has_preference(kind_car="GratisAuto", kind_pt="OV", preference="Neutraal") is False
    assert has_preference(kind_car="GratisAuto", kind_pt="GratisOV", preference="Neutraal") is True
    assert has_preference(kind_car="GratisAuto", kind_pt="GratisOV", preference="OV") is False

    assert has_preference(kind_car="Auto", kind_pt="GratisOV", preference="OV") is True
    assert has_preference(kind_car="Auto", kind_pt="GratisOV", preference="Auto") is False


@pytest.mark.parametrize(
    ("modality_key", "modalities", "preference", "income", "fuel_kind"),
    [
        # First all combinations of two modalities (with electric and fossil cars separate)
        ("Auto_OV_vk", ["car", "pt"], "Neutraal", "laag", "fossiel"),
        ("Auto_OV_vk", ["car", "pt"], "Neutraal", "laag", "elektrisch"),
        ("OV_Fiets_vk", ["bike", "pt"], "Neutraal", "laag", None),
        ("Auto_Fiets_vk", ["bike", "car"], "Neutraal", "laag", "fossiel"),
        ("Auto_Fiets_vk", ["bike", "car"], "Neutraal", "laag", "elektrisch"),
        ("Auto_OV_Fiets_vk", ["car", "pt", "bike"], "Neutraal", "laag", "fossiel"),
        ("Auto_OV_Fiets_vk", ["car", "pt", "bike"], "Neutraal", "laag", "elektrisch"),
        # Then try different car kinds (no car / free car / etc.)
        ("GeenAuto_Fiets_vk", ["bike", "car"], "Neutraal", "middelhoog", None),
        ("GratisAuto_OV_vk", ["car", "pt"], "Auto", "middellaag", None),
        ("GeenRijbewijs_OV_vk", ["car", "pt"], "Neutraal", "laag", None),
        # Then try different pt kinds
        ("GratisOV_Fiets_vk", ["bike", "pt"], "OV", "hoog", None),
        # And finally different preferences
        ("Auto_OV_Fiets_vk", ["car", "pt", "bike"], "OV", "laag", "fossiel"),
        ("Auto_OV_Fiets_vk", ["car", "pt", "bike"], "Auto", "laag", "fossiel"),
        ("Auto_OV_Fiets_vk", ["car", "pt", "bike"], "Fiets", "laag", "fossiel"),
    ],
)
def test_combined_modalities_use_elementwise_max(modality_key, modalities, preference, income, fuel_kind):
    """Test that combined modalities compute the elementwise maximum of their component modalities."""
    import numpy as np

    import ikob.combined_weights as cw
    from ikob.configuration_definition import DecayCurveName, TvomType
    from ikob.datasource import DataKey

    # Prepare
    pod = "Restdag"
    motive = "werk or something else"
    regime = "Basis"

    bike = np.array([[1.0, 0.0, 0.5], [0.0, 0.0, 0.2], [0.3, 0.1, 0.4]])
    pt = np.array([[0.0, 1.0, 0.3], [0.0, 0.0, 0.5], [0.2, 0.6, 0.1]])
    car_fossil = np.array([[0.0, 0.0, 0.2], [1.0, 0.0, 0.4], [0.1, 0.3, 0.7]])
    car_electric = np.array([[0.0, 0.0, 0.1], [0.0, 1.0, 0.6], [0.4, 0.2, 0.5]])
    car = car_fossil if fuel_kind == "fossiel" else car_electric

    class _FakeSingleWeights:
        def get(self, key: DataKey):
            if key.id == "Fiets_vk":
                return bike
            if key.id in {"OV_vk", "GratisOV_vk"}:
                return pt
            if key.id in {"Auto_vk", "GeenAuto_vk", "GeenRijbewijs_vk", "GratisAuto_vk"}:
                if key.fuel_kind == "fossiel":
                    return car_fossil
                else:
                    return car_electric
            raise KeyError(key)

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
            "paden": {
                "output_directory": "out",
                "skims_directory": "skims",
                "segs_directory": "segs",
            },
        },
        "skims": {"dagsoort": [pod]},
    }

    # Act
    combined = cw.calculate_combined_weights(config, _FakeSingleWeights())  # type: ignore

    # Assert
    key_params = {
        "part_of_day": pod,
        "income": income,
        "regime": regime,
        "motive": motive,
        "preference": preference,
        "subtopic": "combinaties",
    }
    if fuel_kind:
        key_params["fuel_kind"] = fuel_kind

    key = DataKey(modality_key, **key_params)
    out = combined.get(key)

    # Map modality names to matrices
    modality_matrices = {"bike": bike, "pt": pt, "car": car}
    matrices_to_max = [modality_matrices[m] for m in modalities]

    expected = np.maximum.reduce(matrices_to_max)

    np.testing.assert_allclose(out, expected)
