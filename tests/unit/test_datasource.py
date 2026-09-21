import numpy as np

from ikob.datasource import DataKey, DataSource, DataType


def test_get_falls_back_to_read_csv_on_cache_miss(tmp_path):
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

    source = DataSource(config=config, datatype=DataType.POTENCY)
    key = DataKey(id="some_id", part_of_day="ochtend")

    csv_path = source._make_file_path(key).with_suffix(".csv")
    csv_path.write_text("zone,waarde\nz2,20\nz1,10\n", encoding="utf-8")

    actual = source.get(key)

    # Note that the actual array is ordered zone1, zone2 like Auto_Tijd.csv and not zone2, zone1 as is the order in retrieved csv
    # This is the zone id store doing it's job
    assert np.array_equal(actual, np.array([10.0, 20.0], dtype=np.float32))
    assert key in source.cache
    assert source.cache[key] is actual
