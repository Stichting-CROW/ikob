import numpy as np
import pytest

from ikob.datasource import DataKey


def _simple_matrices(num_zones):
    rng = np.random.default_rng(42)
    car_time = rng.random((num_zones, num_zones)) * 30
    car_dist = rng.random((num_zones, num_zones)) * 50
    bike_time = rng.random((num_zones, num_zones)) * 20
    bike_dist = rng.random((num_zones, num_zones)) * 15
    pt_time = rng.random((num_zones, num_zones)) * 25
    pt_dist = rng.random((num_zones, num_zones)) * 40
    return car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist


def _setup(monkeypatch, cg, gtt, num_zones, car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist):
    parking_times = np.zeros((num_zones, 3))
    parking_times[:, 0] = np.arange(num_zones)

    skims_data = {
        "Auto_Tijd": car_time,
        "Auto_Afstand": car_dist,
        "Fiets_Tijd": bike_time,
        "Fiets_Afstand": bike_dist,
        "OV_Tijd": pt_time,
        "OV_Afstand": pt_dist,
    }

    def fake_skims_source(_skims_dir):
        class _Reader:
            def read(self, id, dagdeel, type_caster=float, default=None, has_index_column=False):
                if id in skims_data:
                    return np.array(skims_data[id], dtype=type_caster)
                if default is not None:
                    return default
                raise FileNotFoundError(f"Skim {id}/{dagdeel} not found, with no default.")

        return _Reader()

    monkeypatch.setattr(cg, "SkimsSource", fake_skims_source)
    monkeypatch.setattr(gtt, "SkimsSource", fake_skims_source)
    monkeypatch.setattr(gtt, "SegsSource", lambda _config: None)
    monkeypatch.setattr(gtt, "read_parking_times", lambda _config: parking_times)
    monkeypatch.setattr(cg, "read_parking_times", lambda _config: parking_times)


def _make_config():
    return {
        "project": {
            "beprijzingsregime": "basis",
            "motief": {"naam": "woon-werk", "TVOM": "werk"},
            "paden": {
                "output_directory": "out",
                "skims_directory": "skims",
                "segs_directory": "segs",
            },
        },
        "skims": {
            "Kosten auto fossiele brandstof": {"variabele kosten": 5, "kmheffing": 1},
            "Kosten elektrische auto": {"variabele kosten": 3, "kmheffing": 1},
            "OV kosten": {"kmkosten": 10, "starttarief": 100},
            "OV kostenbestand": {"gebruiken": False},
            "pricecap": {"gebruiken": False, "getal": 0},
            "bike_cost_ct_per_km": 2,
            "dagsoort": ["restdag"],
            "varkostenga": {"GeenAuto": 0, "GeenRijbewijs": 0},
            "tijdkostenga": {"GeenAuto": 0, "GeenRijbewijs": 0},
        },
        "TVOM": {
            "werk": {"laag": 0.9, "middellaag": 1.5, "middelhoog": 2.0, "hoog": 2.5},
            "overig": {"laag": 0.8, "middellaag": 1.2, "middelhoog": 1.6, "hoog": 2.0},
        },
        "ketens": {
            "chains": {
                "gebruiken": True,
                "naam hub": "test_hubset",
            },
            "bestemmingslijst": {
                "gebruiken": False,
            },
        },
        "geavanceerd": {
            "additionele_kosten": {"gebruiken": False},
            "parkeerkosten": {"gebruiken": False},
        },
        "__filename__": "tmp",
    }


@pytest.mark.parametrize("hub_zone", [1, 2])
@pytest.mark.parametrize("income", ["laag", "middellaag", "middelhoog", "hoog"])
@pytest.mark.parametrize("fuel", ["fossiel", "elektrisch"])
def test_chain_time_equals_sum_of_parts(monkeypatch, hub_zone, income, fuel):
    """With a zero-cost hub, the P+R chain time equals the generalized travel time to the hub plus the time to the destination.

    This test asserts that the chain computation and the generalized travel time computation use the same logic.
    """
    import ikob.chain_generator as cg
    import ikob.generalized_travel_time as gtt

    num_zones = 30
    car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist = _simple_matrices(num_zones)

    config = _make_config()
    _setup(monkeypatch, cg, gtt, num_zones, car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist)

    hub_data = np.array([[hub_zone, 0, 0, 0, 1]], dtype=float)

    def fake_read_csv(config, key, id, type_caster=float, has_index_column=False):
        if key == "ketens" and id == "chains":
            return hub_data
        if key == "skims" and id == "parkeerzoektijden_bestand":
            return np.zeros(num_zones)
        raise AssertionError(f"Unexpected read_csv_from_config: key={key!r}, id={id!r}")

    monkeypatch.setattr(cg, "read_csv_from_config", fake_read_csv)
    monkeypatch.setattr(gtt, "read_csv_from_config", fake_read_csv)

    datasource = gtt.generalized_travel_time(config)

    gen_car = datasource.get(
        DataKey(
            id=f"Auto_{fuel}",
            part_of_day="restdag",
            income=income,
            regime="basis",
            motive="woon-werk",
        )
    )

    gen_bike = datasource.get(
        DataKey(
            id="Fiets",
            part_of_day="restdag",
            income=income,
            regime="basis",
            motive="woon-werk",
        )
    )

    gen_pt = datasource.get(
        DataKey(
            id="OV",
            part_of_day="restdag",
            income=income,
            regime="basis",
            motive="woon-werk",
        )
    )

    chain_bike = datasource.get(
        DataKey(
            id=f"Pplusfiets_{fuel}",
            part_of_day="restdag",
            income=income,
            hub_name="test_hubset",
            motive="woon-werk",
            regime="basis",
        )
    )

    chain_pt = datasource.get(
        DataKey(
            id=f"PplusR_{fuel}",
            part_of_day="restdag",
            income=income,
            hub_name="test_hubset",
            motive="woon-werk",
            regime="basis",
        )
    )

    expected_bike = gen_car[:, hub_zone - 1][:, np.newaxis] + gen_bike[hub_zone - 1, :][np.newaxis, :]
    expected_pt = gen_car[:, hub_zone - 1][:, np.newaxis] + gen_pt[hub_zone - 1, :][np.newaxis, :]
    np.testing.assert_allclose(chain_bike, expected_bike)
    np.testing.assert_allclose(chain_pt, expected_pt)
