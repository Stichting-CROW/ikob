import numpy as np
import pytest


class SegsCapture:
    """Test double for SegsSource that captures reads and writes in memory."""

    def __init__(self, data_by_key):
        self.data_by_key = data_by_key
        self.writes_csv = []

    def read(self, id: str, type_caster=int, scenario="", group="", modifier="", has_index_column=False):
        key = (id, scenario)
        if key not in self.data_by_key:
            raise KeyError(f"Missing SEGS fixture for id={id!r}, scenario={scenario!r}")
        return np.array(self.data_by_key[key], dtype=type_caster)

    def write_csv(self, data, id, header, group="", modifier="", scenario="", index=None):
        self.writes_csv.append(
            {
                "id": id,
                "group": group,
                "modifier": modifier,
                "scenario": scenario,
                "header": list(header),
                "data": np.array(data),
            }
        )


@pytest.fixture
def segs_capture(monkeypatch):
    """Factory fixture to patch SegsSource to an in-memory dict-backed provider.

    Usage:
        cap = segs_capture({("SomeId", "2023"): array, ...})
    """

    def _make(data_by_key) -> SegsCapture:
        # Some modules import SegsSource directly ("from ikob.datasource import SegsSource"),
        # so patching only ikob.datasource.SegsSource is not sufficient.
        import ikob.competition as competition
        import ikob.datasource as datasource
        import ikob.distribute_over_groups as distribute_over_groups
        import ikob.reachable_destinations as reachable_destinations
        import ikob.reachable_population as reachable_population

        capture = SegsCapture(data_by_key)

        monkeypatch.setattr(datasource, "SegsSource", lambda _: capture)
        monkeypatch.setattr(distribute_over_groups, "SegsSource", lambda _: capture)
        monkeypatch.setattr(reachable_destinations, "SegsSource", lambda _: capture)
        monkeypatch.setattr(reachable_population, "SegsSource", lambda _: capture)
        monkeypatch.setattr(competition, "SegsSource", lambda _: capture)
        return capture

    return _make
