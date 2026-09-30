import numpy as np

from ikob import datasource as datasource_module
from ikob.datasource import DataKey, DataSource, DataType


def test_get_falls_back_to_read_csv_on_cache_miss(tmp_path, monkeypatch):
    # Prepare the config
    skims_dir = tmp_path / "skims"
    skim_day_dir = skims_dir / "ochtend"
    skim_day_dir.mkdir(parents=True)
    (skim_day_dir / "Auto_Tijd.csv").write_text("zone,tijd\nz1,0\nz2,0\n", encoding="utf-8")

    config = {
        "__filename__": "test-project",
        "project": {
            "paden": {
                "output_directory": str(tmp_path / "output"),
                "skims_directory": str(skims_dir),
            }
        },
        "skims": {"dagsoort": ["ochtend"]},
    }

    # Setup some data source and key with a csv file located at the path of the key
    source = DataSource(config=config, datatype=DataType.POTENCY)
    key = DataKey(id="some_id", part_of_day="ochtend")

    csv_path = source._make_file_path(key).with_suffix(".csv")
    csv_path.write_text("zone,waarde\nz2,20\nz1,10\n", encoding="utf-8")

    # Catch any calls to read csv to ensure that a get request not in the cache actually calls read_csv
    read_csv_calls = [0]  # a list so that it's captured correctly by the spy
    original_read_csv = datasource_module.utils.read_csv

    def read_csv_spy(*args, **kwargs):
        read_csv_calls[0] += 1
        return original_read_csv(*args, **kwargs)

    monkeypatch.setattr(datasource_module.utils, "read_csv", read_csv_spy)

    assert key not in source.cache
    actual = source.get(key)

    # Note that the actual array is ordered zone1, zone2 like Auto_Tijd.csv and not zone2, zone1 as is the order in retrieved csv
    # This is the zone id store doing its job
    assert np.array_equal(actual, np.array([10.0, 20.0], dtype=np.float32))

    assert read_csv_calls[0] == 1
