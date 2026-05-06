import pytest

from ikob.datasource import read_csv_from_config


@pytest.fixture()
def single_column_csv(tmp_path):
    """A single-column CSV: one value per zone."""
    path = tmp_path / "single_column.csv"
    path.write_text("zone,waarde\n1,100\n2,200\n3,300\n")
    return path


@pytest.fixture()
def matrix_csv(tmp_path):
    """A zone-by-zone matrix CSV."""
    path = tmp_path / "matrix.csv"
    path.write_text("zone,z1,z2,z3\n1,0,5,3\n2,5,0,7\n3,3,7,0\n")
    return path


def test_reads_parking_costs_as_1d_array(single_column_csv):
    config = {
        "geavanceerd": {
            "parkeerkosten": {"bestand": str(single_column_csv), "gebruiken": True},
        },
    }
    costs = read_csv_from_config(config, key="geavanceerd", id="parkeerkosten")
    assert costs.shape == (3,)


def test_reads_kunstmab_as_1d_array(single_column_csv):
    config = {
        "geavanceerd": {
            "kunstmab": {"bestand": str(single_column_csv), "gebruiken": True},
        },
    }
    kunstmab = read_csv_from_config(config, key="geavanceerd", id="kunstmab", type_caster=int)
    assert kunstmab.shape == (3,)


def test_reads_additional_cost_as_2d_matrix(matrix_csv):
    config = {
        "geavanceerd": {
            "additionele_kosten": {"bestand": str(matrix_csv), "gebruiken": True},
        },
    }
    matrix = read_csv_from_config(config, key="geavanceerd", id="additionele_kosten")
    assert matrix.shape == (3, 3)
