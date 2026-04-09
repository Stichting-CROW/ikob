import numpy as np
import pytest

from ikob.utils import IKOB_INFINITE


def test_costs_public_transport_pricecap_and_starting_rate():
    from ikob.utils import costs_public_transport

    # Prepare
    distance = np.array(
        [
            [0.0, 10.0, 20.0],
            [20.0, 30.0, 40.0],
            [5.0, 15.0, 25.0],
        ]
    )

    # Prices in euros (generalized_travel_time converts cents -> euros before calling).
    pt_km_price = 0.5
    starting_rate = 1.0
    pricecap_value = 15.0

    # Act
    costs = costs_public_transport(distance, pt_km_price, starting_rate, pricecap=True, pricecap_value=pricecap_value)

    # Assert
    expected = np.array(
        [
            [1.0, 6.0, 11.0],
            [11.0, 15.0, 15.0],
            [3.5, 8.5, 13.5],
        ]
    )
    np.testing.assert_allclose(costs, expected)


def setup_generalized_travel_time_input(monkeypatch, gtt):
    from ikob.configuration_definition import DecayCurveName, TvomType

    pod = "Restdag"
    motive = "werk or something else"
    regime = "Basis"
    income = "laag"

    car_time = np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0], [70.0, 80.0, 90.0]])
    car_dist = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    bike_time = np.array([[100.0, 200.0, 150.0], [50.0, 180.0, 170.0], [160.0, 175.0, 190.0]])
    bike_distance = np.array([[5.0, 10.0, 8.0], [4.0, 9.0, 7.0], [6.0, 11.0, 9.0]])
    pt_time = np.array([[1.0, 2.0, 3.0], [0.4, 5.0, 6.0], [7.0, 8.0, 9.0]])
    pt_dist = np.array([[0.0, 10.0, 20.0], [20.0, 30.0, 40.0], [5.0, 15.0, 25.0]])

    skims_data = {
        ("Auto_Tijd", pod): car_time,
        ("Auto_Afstand", pod): car_dist,
        ("Fiets_Tijd", pod): bike_time,
        ("Fiets_Afstand", pod): bike_distance,
        ("OV_Tijd", pod): pt_time,
        ("OV_Afstand", pod): pt_dist,
    }

    def fake_skims_source(_skims_dir):
        class _Reader:
            def read(self, id: str, dagdeel: str, type_caster=float, default=None, has_index_column=False):
                return np.array(skims_data[(id, dagdeel)], dtype=type_caster)

        return _Reader()

    # The first entry of each row is the zone number
    parking_times = np.array(
        [
            [0, 1, 2],
            [1, 3, 4],
            [2, 4, 6],
        ]
    )

    def fake_read_csv_from_config(config, key: str, id: str, type_caster=float, has_index_column=False):
        # Only used to infer the number of zones when parking costs are disabled.
        if key == "skims" and id == "parkeerzoektijden_bestand":
            return np.zeros(3)
        raise AssertionError(f"Unexpected read_csv_from_config call: key={key!r}, id={id!r}")

    monkeypatch.setattr(gtt, "SkimsSource", fake_skims_source)
    monkeypatch.setattr(gtt, "SegsSource", lambda _config: None)
    monkeypatch.setattr(gtt, "read_parking_times", lambda _config: parking_times)
    monkeypatch.setattr(gtt, "read_csv_from_config", fake_read_csv_from_config)

    tvom = TvomType.WORK
    config = {
        "__filename__": "pytest",
        "project": {
            "verstedelijkingsscenario": "2023",
            "beprijzingsregime": regime,
            "motief": {
                "naam": motive,
                "reizende populatie": "path",
                "bestemmingsplaatsen": "path",
                "TVOM": tvom,
                "reistijdvervalscurve": DecayCurveName.WORK_AND_SOCIAL,
            },
            "paden": {
                "skims_directory": "skims",
                "output_directory": "out",
                "segs_directory": "segs",
            },
        },
        "skims": {
            "OV kostenbestand": {"gebruiken": False},
            "OV kosten": {"kmkosten": 50.0, "starttarief": 100.0},
            "pricecap": {"gebruiken": True, "getal": 15.0},
            "Kosten auto fossiele brandstof": {"variabele kosten": 20.0, "kmheffing": 10.0},
            "Kosten elektrische auto": {"variabele kosten": 10.0, "kmheffing": 10.0},
            "varkostenga": {"GeenAuto": 0.3, "GeenRijbewijs": 1.0},
            "tijdkostenga": {"GeenAuto": 0.05, "GeenRijbewijs": 0.1},
            "dagsoort": [pod],
            "parkeerzoektijden_bestand": "unused.csv",
            "bike_cost_ct_per_km": -5.0,
        },
        "TVOM": {
            "werk": {"laag": 0.1, "middellaag": 0.4, "middelhoog": 0.5, "hoog": 0.7},
            "overig": {"laag": 0.2, "middellaag": 0.3, "middelhoog": 0.6, "hoog": 0.8},
        },
        "geavanceerd": {
            "additionele_kosten": {"gebruiken": False, "bestand": ""},
            "parkeerkosten": {"gebruiken": False, "bestand": ""},
        },
        "ketens": {
            "chains": {"gebruiken": False, "naam hub": ""},
            "bestemmingslijst": {"gebruiken": False},
        },
    }
    return (
        config,
        pod,
        regime,
        motive,
        income,
        car_time,
        car_dist,
        bike_time,
        bike_distance,
        pt_time,
        pt_dist,
        parking_times,
        tvom,
    )


def test_generalized_travel_time_fiets(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey

    config, pod, regime, motive, income, _, _, bike_time, bike_distance, _, _, _, tvom = (
        setup_generalized_travel_time_input(monkeypatch, gtt)
    )

    datasource = gtt.generalized_travel_time(config)

    fiets_key = DataKey(id="Fiets", part_of_day=pod, regime=regime, motive=motive, income=income)
    fiets = datasource.get(fiets_key)
    expected_fiets = (
        bike_time + config["TVOM"][tvom][income] * bike_distance * config["skims"]["bike_cost_ct_per_km"] / 100
    )
    np.testing.assert_allclose(fiets, expected_fiets)


def test_generalized_travel_time_public_transport(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey
    from ikob.utils import costs_public_transport

    config, pod, regime, motive, income, _, _, _, _, pt_time, pt_dist, _, tvom = setup_generalized_travel_time_input(
        monkeypatch, gtt
    )

    datasource = gtt.generalized_travel_time(config)

    pt_key = DataKey(id="OV", part_of_day=pod, income=income, motive=motive, regime=regime)
    pt = datasource.get(pt_key)
    expected_pt = np.array(
        pt_time
        + config["TVOM"][tvom][income]
        * costs_public_transport(
            distance=pt_dist,
            # The config is is in cents, but the function expects euros.
            pt_km_price=config["skims"]["OV kosten"]["kmkosten"] / 100,
            starting_rate=config["skims"]["OV kosten"]["starttarief"] / 100,
            pricecap=config["skims"]["pricecap"]["gebruiken"],
            pricecap_value=config["skims"]["pricecap"]["getal"],
        )
    )
    # Don't take the PT option if travel is less than 0.5 minutes.
    expected_pt = np.where(pt_time > 0.5, expected_pt, IKOB_INFINITE)
    np.testing.assert_allclose(pt, expected_pt)


def test_generalized_travel_time_free_public_transport(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey

    config, pod, regime, motive, _, _, _, _, _, pt_time, _, _, _ = setup_generalized_travel_time_input(monkeypatch, gtt)

    datasource = gtt.generalized_travel_time(config)

    free_pt_key = DataKey(id="GratisOV", part_of_day=pod, motive=motive, regime=regime)
    free_pt = datasource.get(free_pt_key)
    expected_free_pt = np.where(pt_time > 0.5, pt_time, IKOB_INFINITE)
    np.testing.assert_allclose(free_pt, expected_free_pt)


def test_generalized_travel_time_auto_fossiel(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey

    config, pod, regime, motive, income, car_time, car_dist, _, _, _, _, parking_times, tvom = (
        setup_generalized_travel_time_input(monkeypatch, gtt)
    )

    datasource = gtt.generalized_travel_time(config)

    auto_key = DataKey(id="Auto_fossiel", part_of_day=pod, income=income, regime=regime, motive=motive)
    auto = datasource.get(auto_key)
    # total_time = car_time + parking_arrival(origin) + parking_departure(dest)
    total_time = car_time + parking_times[:, [0]] + parking_times[[0, 1, 2], [1]]
    expected_auto = total_time + config["TVOM"][tvom][income] * car_dist * (
        config["skims"]["Kosten auto fossiele brandstof"]["variabele kosten"] / 100
        + config["skims"]["Kosten auto fossiele brandstof"]["kmheffing"] / 100
    )
    np.testing.assert_allclose(auto, expected_auto)


def test_generalized_travel_time_geen_auto(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey

    config, pod, regime, motive, income, car_time, car_dist, _, _, _, _, _, tvom = setup_generalized_travel_time_input(
        monkeypatch, gtt
    )

    datasource = gtt.generalized_travel_time(config)

    no_car_key = DataKey(id="GeenAuto", part_of_day=pod, income=income, motive=motive, regime=regime)
    no_car = datasource.get(no_car_key)
    # total_cost = time * tijdkost + distance * (varkost + kmheffing)
    expected_no_car = car_time + config["TVOM"][tvom][income] * (
        car_time * config["skims"]["tijdkostenga"]["GeenAuto"]
        + car_dist
        * (
            config["skims"]["varkostenga"]["GeenAuto"]
            + config["skims"]["Kosten auto fossiele brandstof"]["kmheffing"] / 100
        )
    )
    np.testing.assert_allclose(no_car, expected_no_car)


def test_generalized_travel_time_geen_rijbewijs(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey

    config, pod, regime, motive, income, car_time, car_dist, _, _, _, _, _, tvom = setup_generalized_travel_time_input(
        monkeypatch, gtt
    )

    datasource = gtt.generalized_travel_time(config)

    no_license_key = DataKey(id="GeenRijbewijs", part_of_day=pod, income=income, motive=motive, regime=regime)
    no_license = datasource.get(no_license_key)
    expected_no_license = car_time + config["TVOM"][tvom][income] * (
        car_time * config["skims"]["tijdkostenga"]["GeenRijbewijs"]
        + car_dist
        * (
            config["skims"]["varkostenga"]["GeenRijbewijs"]
            + config["skims"]["Kosten auto fossiele brandstof"]["kmheffing"] / 100
        )
    )
    np.testing.assert_allclose(no_license, expected_no_license)


def test_generalized_travel_time_includes_additional_and_parking_costs(monkeypatch):
    import ikob.generalized_travel_time as gtt
    from ikob.datasource import DataKey

    config, pod, regime, motive, income, car_time, car_dist, _, _, _, _, parking_times, tvom = (
        setup_generalized_travel_time_input(monkeypatch, gtt)
    )

    parking_costs = np.array([100.0, 300.0, 500.0])
    additional_costs = np.array([[0.0, 50.0, 25.0], [100.0, 0.0, 75.0], [60.0, 80.0, 90.0]])

    def fake_read_csv_from_config(config, key: str, id: str, type_caster=float, has_index_column=False):
        if key == "skims" and id == "parkeerzoektijden_bestand":
            return np.zeros(2)
        if key == "geavanceerd" and id == "parkeerkosten":
            return parking_costs
        if key == "geavanceerd" and id == "additionele_kosten":
            return additional_costs
        raise AssertionError(f"Unexpected read_csv_from_config call: key={key!r}, id={id!r}")

    config["geavanceerd"]["additionele_kosten"]["gebruiken"] = True
    config["geavanceerd"]["parkeerkosten"]["gebruiken"] = True

    monkeypatch.setattr(gtt, "read_csv_from_config", fake_read_csv_from_config)

    datasource = gtt.generalized_travel_time(config)

    auto_key = DataKey(id="Auto_fossiel", part_of_day=pod, income=income, regime=regime, motive=motive)
    auto = datasource.get(auto_key)

    # Focus assertion on one cell to keep intent clear:
    assert auto[0][1] == pytest.approx(
        car_time[0][1]
        + parking_times[0][0]
        + parking_times[1][1]
        + config["TVOM"][tvom][income]
        * (
            car_dist[0][1]
            * (
                config["skims"]["Kosten auto fossiele brandstof"]["variabele kosten"] / 100
                + config["skims"]["Kosten auto fossiele brandstof"]["kmheffing"] / 100
            )
            + additional_costs[0][1] / 100
            + parking_costs[1] / 100
        )
    )
    assert auto.shape == (3, 3)
