import numpy as np

from ikob.chain_generator import Hubs, chain_generator, compute_chain_travel_time
from ikob.datasource import DataKey, DataSource, DataType
from ikob.utils import IKOB_INFINITE


def _make_hubs(zones, hub_costs, pt_transfer, bike_transfer, pay_for_pt):
    """Build a Hubs object from plain lists."""
    data = np.column_stack([zones, hub_costs, pt_transfer, bike_transfer, pay_for_pt])
    return Hubs(data)


def _skim_matrices(n=4):
    """Return small deterministic skim matrices for n zones."""
    rng = np.random.default_rng(42)
    car_time = rng.random((n, n)) * 30
    car_dist = rng.random((n, n)) * 50
    bike_time = rng.random((n, n)) * 20
    bike_dist = rng.random((n, n)) * 15
    pt_time = rng.random((n, n)) * 25
    pt_dist = rng.random((n, n)) * 40
    return car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist


def test_parking_time_at_hub_is_ignored():
    """The parking time at the hub is incorporated in the hub transfer time.

    The normal parking time for the zone is ignored"""
    n = 4
    car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist = _skim_matrices(n)
    pt_cost = pt_dist * 0.10

    hub_zone = 2
    hubs = _make_hubs(zones=[hub_zone], hub_costs=[100], pt_transfer=[5], bike_transfer=[3], pay_for_pt=[1])

    kwargs = dict(
        hubs=hubs,
        car_time=car_time,
        car_dist=car_dist,
        bike_time=bike_time,
        bike_dist=bike_dist,
        pt_time=pt_time,
        pt_cost=pt_cost,
        tvom_factor=2.0,
        var_car_rate=0.05,
        road_pricing=0.01,
        bike_cost_euro_per_km=0.02,
        additional_costs=np.zeros((n, n)),
        destination_list=np.linspace(1, n, n, dtype=int),
    )

    # parking_times without any parking search time
    parking_times_zero = np.zeros((n, 3))

    # parking_times with a large search time at destinations
    parking_times_with_hub = np.zeros((n, 3))
    parking_times_with_hub[:, 2] = 2718

    result_bike_zero, result_ride_zero = compute_chain_travel_time(**kwargs, parking_times=parking_times_zero)  # type: ignore
    result_bike_hub, result_ride_hub = compute_chain_travel_time(**kwargs, parking_times=parking_times_with_hub)  # type: ignore

    np.testing.assert_allclose(result_bike_hub, result_bike_zero)
    np.testing.assert_allclose(result_ride_hub, result_ride_zero)


def test_no_hubs():
    """With no hubs, the chain travel time is infinite"""
    n = 4
    car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist = _skim_matrices(n)
    hubs = _make_hubs(zones=[], hub_costs=[], pt_transfer=[], bike_transfer=[], pay_for_pt=[])

    pt_cost = pt_dist * 0.08

    result_bike, result_ride = compute_chain_travel_time(
        hubs,
        car_time,
        car_dist,
        bike_time,
        bike_dist,
        pt_time,
        pt_cost,
        tvom_factor=1.5,
        var_car_rate=0.04,
        road_pricing=0.02,
        bike_cost_euro_per_km=0.02,
        additional_costs=np.zeros((n, n)),
        parking_times=np.zeros((n, 3)),
        destination_list=np.linspace(1, n, n, dtype=int),
    )

    np.testing.assert_allclose(IKOB_INFINITE, result_bike)
    np.testing.assert_allclose(IKOB_INFINITE, result_ride)


def test_no_pt_costs():
    """When pay_for_pt is zero, PT costs do not affect ride results"""
    n = 4
    car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist = _skim_matrices(n)
    pt_cost = pt_dist * 0.10

    hub_zone = 2
    common = dict(
        car_time=car_time,
        car_dist=car_dist,
        bike_time=bike_time,
        bike_dist=bike_dist,
        pt_time=pt_time,
        tvom_factor=2.0,
        var_car_rate=0.05,
        road_pricing=0.01,
        bike_cost_euro_per_km=0.02,
        additional_costs=np.zeros((n, n)),
        parking_times=np.zeros((n, 3)),
        destination_list=np.linspace(1, n, n, dtype=int),
    )

    # pay_for_pt=0 with real pt_cost
    hubs_no_pay = _make_hubs(zones=[hub_zone], hub_costs=[100], pt_transfer=[5], bike_transfer=[3], pay_for_pt=[0])
    _, result_ride_no_pay = compute_chain_travel_time(hubs=hubs_no_pay, pt_cost=pt_cost, **common)

    # pay_for_pt=1 with zero pt_cost
    hubs_pay = _make_hubs(zones=[hub_zone], hub_costs=[100], pt_transfer=[5], bike_transfer=[3], pay_for_pt=[1])
    _, result_ride_zero_cost = compute_chain_travel_time(hubs=hubs_pay, pt_cost=np.zeros_like(pt_cost), **common)

    np.testing.assert_allclose(result_ride_no_pay, result_ride_zero_cost)


def test_minimum_across_hubs():
    """With two hubs, element-wise minimum is taken correctly."""
    n = 4
    car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist = _skim_matrices(n)
    hub_costs1 = 50
    hub_costs3 = 80
    pt_transfer1 = 4
    pt_transfer3 = 6
    bike_transfer1 = 2
    bike_transfer3 = 3
    pay_for_pt = 1
    hubs = _make_hubs(
        zones=[1, 3],
        hub_costs=[hub_costs1, hub_costs3],
        pt_transfer=[pt_transfer1, pt_transfer3],
        bike_transfer=[bike_transfer1, bike_transfer3],
        pay_for_pt=[pay_for_pt, pay_for_pt],
    )

    pt_cost = pt_dist * 0.08
    input_dict = dict(
        car_time=car_time,
        car_dist=car_dist,
        bike_time=bike_time,
        bike_dist=bike_dist,
        pt_time=pt_time,
        pt_cost=pt_cost,
        tvom_factor=1.5,
        var_car_rate=0.04,
        road_pricing=0.02,
        bike_cost_euro_per_km=0.02,
        additional_costs=np.zeros((n, n)),
        parking_times=np.zeros((n, 3)),
        destination_list=np.linspace(1, n, n, dtype=int),
    )

    result_bike, result_ride = compute_chain_travel_time(hubs, **input_dict)

    # Result is <= single-hub results
    for zone in [1, 3]:
        single = _make_hubs(
            zones=[zone],
            hub_costs=[hub_costs1 if zone == 1 else hub_costs3],
            pt_transfer=[pt_transfer1 if zone == 1 else pt_transfer3],
            bike_transfer=[bike_transfer1 if zone == 1 else bike_transfer3],
            pay_for_pt=[1],
        )
        sb, sr = compute_chain_travel_time(single, **input_dict)
        assert np.all(result_bike <= sb + 1e-10)
        assert np.all(result_ride <= sr + 1e-10)


def test_destination_list():
    """Destinations not in the destinations list have an "infinite" travel time via the hub"""
    n = 4
    car_time, car_dist, bike_time, bike_dist, pt_time, pt_dist = _skim_matrices(n)
    hub_costs1 = 50
    hub_costs3 = 80
    pt_transfer1 = 4
    pt_transfer3 = 6
    bike_transfer1 = 2
    bike_transfer3 = 3
    pay_for_pt = 1
    hubs = _make_hubs(
        zones=[1, 3],
        hub_costs=[hub_costs1, hub_costs3],
        pt_transfer=[pt_transfer1, pt_transfer3],
        bike_transfer=[bike_transfer1, bike_transfer3],
        pay_for_pt=[pay_for_pt, pay_for_pt],
    )

    pt_cost = pt_dist * 0.08

    result_bike, result_ride = compute_chain_travel_time(
        hubs,
        car_time,
        car_dist,
        bike_time,
        bike_dist,
        pt_time,
        pt_cost,
        tvom_factor=1.5,
        var_car_rate=0.04,
        road_pricing=0.02,
        bike_cost_euro_per_km=0.02,
        additional_costs=np.zeros((n, n)),
        parking_times=np.zeros((n, 3)),
        destination_list=np.array([1, 2, 4]),
    )
    assert np.allclose(result_bike[:, 2], IKOB_INFINITE)
    assert not np.any(np.isclose(result_bike[:, [0, 1, 3]], IKOB_INFINITE))
    assert np.allclose(result_ride[:, 2], IKOB_INFINITE)
    assert not np.any(np.isclose(result_ride[:, [0, 1, 3]], IKOB_INFINITE))


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
            "parkeerzoektijden_bestand": "unused.csv",
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
            "additionele_kosten": {"gebruiken": False, "bestand": ""},
            "parkeerkosten": {"gebruiken": False, "bestand": ""},
        },
        "__filename__": "tmp",
    }


def test_computed_keys(monkeypatch):
    """chain_generator populates the DataSource with P+Bike and P+R keys."""
    import ikob.chain_generator as cg

    num_zones = 5
    rng = np.random.default_rng(99)

    skims_data = {
        "Auto_Tijd": rng.random((num_zones, num_zones)) * 30,
        "Auto_Afstand": rng.random((num_zones, num_zones)) * 30,
        "Fiets_Tijd": rng.random((num_zones, num_zones)) * 30,
        "OV_Tijd": rng.random((num_zones, num_zones)) * 30,
        "OV_Afstand": rng.random((num_zones, num_zones)) * 30,
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

    hub_data = np.array([[2, 50, 5, 3, 1], [4, 80, 6, 4, 1]], dtype=float)

    def fake_read_csv_from_config(config, key, id, type_caster=float, has_index_column=False):
        if key == "ketens" and id == "chains":
            return hub_data
        if key == "ketens" and id == "bestemmingslijst":
            return np.linspace(1, num_zones, num_zones, dtype=int)
        raise AssertionError(f"Unexpected read_csv_from_config call: key={key!r}, id={id!r}")

    monkeypatch.setattr(cg, "SkimsSource", fake_skims_source)
    monkeypatch.setattr(cg, "read_csv_from_config", fake_read_csv_from_config)
    monkeypatch.setattr(cg, "read_parking_times", lambda _config: np.zeros((num_zones, 3)))

    config = _make_config()

    datasource = DataSource(config, DataType.GENERALIZED_TRAVEL_TIME)
    datasource.cache = {}

    chain_generator(datasource, config)

    # Expect keys for 4 income levels x 2 fuel kinds x {Pplusfiets, PplusR} = 16 keys
    assert len(datasource.cache) == 16
    for income in ["laag", "middellaag", "middelhoog", "hoog"]:
        for fuel in ["fossiel", "elektrisch"]:
            for prefix in ["Pplusfiets", "PplusR"]:
                key = DataKey(
                    id=f"{prefix}_{fuel}",
                    part_of_day="restdag",
                    income=income,
                    hub_name="test_hubset",
                    motive="woon-werk",
                    regime="basis",
                )
                assert key in datasource.cache, f"Missing key: {key}"
                matrix = datasource.cache[key]
                assert matrix.shape == (num_zones, num_zones)
