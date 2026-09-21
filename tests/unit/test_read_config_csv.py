import pytest

from ikob.datasource import read_csv_from_config
from ikob.id_store import IdStore, ZoneIdStoreSingleton


@pytest.fixture()
def single_column_csv(tmp_path):
    """A single-column CSV: one value per zone."""
    path = tmp_path / "single_column.csv"
    path.write_text("zone,waarde\nz1,100\nz2,200\nz3,300\n")
    return path


@pytest.fixture()
def matrix_csv(tmp_path):
    """A zone-by-zone matrix CSV."""
    path = tmp_path / "matrix.csv"
    path.write_text("zone,z1,z2,z3\nz1,0,5,3\nz2,5,0,7\nz3,3,7,0\n")
    return path


def test_reads_parking_costs_as_1d_array(single_column_csv):
    ZoneIdStoreSingleton._instance = IdStore(["z1", "z2", "z3"])

    config = {
        "geavanceerd": {
            "parkeerkosten": {"bestand": str(single_column_csv), "gebruiken": True},
        },
    }
    costs = read_csv_from_config(config, key="geavanceerd", id="parkeerkosten")
    assert costs.shape == (3,)


def test_reads_kunstmab_as_1d_array(single_column_csv):
    ZoneIdStoreSingleton._instance = IdStore(["z1", "z2", "z3"])

    config = {
        "geavanceerd": {
            "kunstmab": {"bestand": str(single_column_csv), "gebruiken": True},
        },
    }
    kunstmab = read_csv_from_config(config, key="geavanceerd", id="kunstmab", type_caster=int)
    assert kunstmab.shape == (3,)


def test_reads_additional_cost_as_2d_matrix(matrix_csv):
    ZoneIdStoreSingleton._instance = IdStore(["z1", "z2", "z3"])

    config = {
        "geavanceerd": {
            "additionele_kosten": {"bestand": str(matrix_csv), "gebruiken": True},
        },
    }
    matrix = read_csv_from_config(config, key="geavanceerd", id="additionele_kosten")
    assert matrix.shape == (3, 3)
