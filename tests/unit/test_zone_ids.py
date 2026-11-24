from unittest.mock import Mock

import pytest

from ikob import zone_ids
from ikob.id_store import IdStore, ZoneIdStoreSingleton
from ikob.utils import read_csv
from ikob.zone_ids import initialize_zone_id_store


@pytest.mark.parametrize(
    "missing_file, expected_valid",
    [
        (None, True),
        # These files are optional in the config
        ("Fiets_Afstand.csv", True),
        ("custom_parking_times.csv", True),
        # kunst.csv is the file for kunstmab (artificial car possession) and kunstmab is used.
        ("kunst.csv", False),
        ("population.csv", False),
    ],
)
def test_zone_id_store_uses_intersection_of_full_zone_inputs(tmp_path, missing_file, expected_valid):
    skims_dir = tmp_path / "skims"
    segs_dir = tmp_path / "segs"
    external_dir = tmp_path / "external"

    def write_ids(path, ids, matrix=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        if matrix:
            header = "zone," + ",".join(ids)
            rows = [f"{zone_id}," + ",".join("0" for _ in ids) for zone_id in ids]
        else:
            header = "zone,value"
            rows = [f"{zone_id},1" for zone_id in ids]
        path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")

    skim_ids = ["Auto_Tijd", "Auto_Afstand", "Fiets_Tijd", "Fiets_Afstand", "OV_Tijd", "OV_Afstand"]
    for skim_id in skim_ids:
        write_ids(skims_dir / "Morning" / f"{skim_id}.csv", ["z3", "z2", f"skim_extra {skim_id}"], matrix=True)

    write_ids(segs_dir / "CBS_autos_per_huishouden.csv", ["z2", "z3", "cbs_extra"])
    write_ids(segs_dir / "Stedelijkheidsgraad.csv", ["z2", "z3", "urban_extra"])
    write_ids(segs_dir / "2023" / "population.csv", ["z2", "z3", "population_extra"])
    write_ids(segs_dir / "2023" / "destinations.csv", ["z2", "z3", "destinations_extra"])
    write_ids(segs_dir / "custom_parking_times.csv", ["z2", "z3", "parking_times_extra"])
    write_ids(external_dir / "kunst.csv", ["z2", "z3", "kunst_extra"])
    write_ids(external_dir / "parking_costs.csv", ["z2", "z3", "parking_costs_extra"])
    write_ids(external_dir / "additional_costs.csv", ["z2", "z3", "additional_costs_extra"], matrix=True)

    config = {
        "__filename__": "project",
        "project": {
            "paden": {
                "skims_directory": str(skims_dir),
                "segs_directory": str(segs_dir),
                "output_directory": str(tmp_path / "output"),
            },
            "verstedelijkingsscenario": "2023",
            "motief": {
                "reizende populatie": "population.csv",
                "bestemmingsplaatsen": "destinations.csv",
            },
        },
        "skims": {
            "dagsoort": ["Morning"],
            "OV kostenbestand": {"gebruiken": False},
            "parkeerzoektijden_bestand": str(segs_dir / "custom_parking_times.csv"),
        },
        "geavanceerd": {
            "kunstmab": {"gebruiken": True, "bestand": str(external_dir / "kunst.csv")},
            "parkeerkosten": {"gebruiken": True, "bestand": str(external_dir / "parking_costs.csv")},
            "additionele_kosten": {"gebruiken": True, "bestand": str(external_dir / "additional_costs.csv")},
        },
    }

    if missing_file is not None:
        next(tmp_path.rglob(missing_file)).unlink()

    existing_store = IdStore.from_zone_ids(["existing-zone"])
    ZoneIdStoreSingleton.set_instance(existing_store)
    if not expected_valid:
        assert initialize_zone_id_store(config) is False
        assert ZoneIdStoreSingleton.get_instance() is existing_store
        return

    assert initialize_zone_id_store(config) is True
    store = ZoneIdStoreSingleton.get_instance()
    assert store is not existing_store
    assert store._zone_ids == ("z3", "z2")
    skim = read_csv(
        skims_dir / "Morning" / "Auto_Tijd.csv",
        has_id_header=True,
        id_store=store,
    )
    assert skim.shape == (2, 2)


def test_zone_id_store_rejects_empty_intersection(tmp_path, monkeypatch, caplog):
    config = {}
    inputs = [zone_ids.ZoneIdInputFile(tmp_path / "skim.csv", True)]
    monkeypatch.setattr(zone_ids, "_zone_id_input_files", Mock(return_value=inputs))
    monkeypatch.setattr(zone_ids.utils, "read_zone_ids", Mock(return_value=(["z1"], ["z2"])))
    existing_store = IdStore.from_zone_ids(["existing-zone"])
    ZoneIdStoreSingleton.set_instance(existing_store)

    assert initialize_zone_id_store(config) is False

    assert "no common zone IDs" in caplog.text
    assert ZoneIdStoreSingleton.get_instance() is existing_store


@pytest.mark.parametrize("contents,has_zone_header", [("", False), ("zone\nz1\n", True)])
def test_zone_id_store_reports_invalid_input_file(tmp_path, monkeypatch, caplog, contents, has_zone_header):
    config = {}
    path = tmp_path / "skim.csv"
    path.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(
        zone_ids, "_zone_id_input_files", Mock(return_value=[zone_ids.ZoneIdInputFile(path, has_zone_header)])
    )
    existing_store = IdStore.from_zone_ids(["existing-zone"])
    ZoneIdStoreSingleton.set_instance(existing_store)

    assert initialize_zone_id_store(config) is False

    assert "read zone IDs from" in caplog.text
    assert ZoneIdStoreSingleton.get_instance() is existing_store


def test_zone_id_store_reports_input_discovery_error(monkeypatch, caplog):
    monkeypatch.setattr(zone_ids, "_zone_id_input_files", Mock(side_effect=OSError("Some file errors")))

    assert initialize_zone_id_store({}) is False

    assert "Some file errors" in caplog.text
