from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, unsafe_hash=True)
class IdStore:
    """A mapping for (zone) ID to (zone) index in the matrices used throughout the code

    Zone is in between brackets as this class is mainly used for converting zone id's to indices but can also be used to correctly read
    files with different id's such as urbanization grades.
    """

    # All the other fields get generated from the zone_ids, so we only need this in the hash
    _zone_ids: tuple[str, ...] = field(hash=True)
    # MappingProxyType is essentially an immutable dict
    _id_to_idx: MappingProxyType[str, int] = field(hash=False)
    _num_zones: int = field(hash=False)
    _zone_source: str = field(hash=False)

    @classmethod
    def from_zone_ids(cls, zone_ids: list[str], zone_source=""):
        duplicates = {id for id in zone_ids if zone_ids.count(id) > 1}
        if any(duplicates):
            raise ValueError(
                "Duplicate id's found in "
                + (zone_source if zone_source != "" else "zone ids provided to id store constructor")
                + f"\nduplicates: {duplicates}"
            )

        id_to_idx = {zone_id: idx for idx, zone_id in enumerate(zone_ids)}
        num_zones = len(zone_ids)
        return cls(tuple(zone_ids), MappingProxyType(id_to_idx.copy()), num_zones, zone_source)

    def validate_exact_ids(self, ids: list[str], source_name: str):
        reference = set(self._zone_ids)
        duplicates = {id for id in ids if ids.count(id) > 1}
        if any(duplicates):
            raise ValueError(f"Duplicate id's found in {source_name}. Duplicates: {duplicates}")

        current = set(ids)
        missing_ids = reference - current
        extra_ids = current - reference
        if missing_ids or extra_ids:
            msg = f"id mismatch for {source_name}.\nMissing ids: {missing_ids}\nextra ids: {extra_ids}"
            msg += ("\nid's have been read from " + self._zone_source) if self._zone_source else ""
            raise ValueError(msg)

    def reorder_rows_to_internal_idx(self, row_ids: list[str], values: NDArray) -> NDArray:
        row_id_to_idx = {row_id: row_idx for row_idx, row_id in enumerate(row_ids)}
        reordered_row_idx = [row_id_to_idx[zone_id] for zone_id in self._zone_ids]
        return values[reordered_row_idx]

    def reorder_columns_to_internal_idx(self, col_ids: list[str], values: NDArray) -> NDArray:
        col_id_to_idx = {col_id: col_idx for col_idx, col_id in enumerate(col_ids)}
        reordered_col_idx = [col_id_to_idx[zone_id] for zone_id in self._zone_ids]
        return values[:, reordered_col_idx]


class ZoneIdStoreSingleton:
    _instance: IdStore | None = None

    @staticmethod
    def get_instance(config) -> IdStore:
        if ZoneIdStoreSingleton._instance is None:
            ZoneIdStoreSingleton._instance = ZoneIdStoreSingleton._try_build_zone_id_index_map(config)

        return ZoneIdStoreSingleton._instance  # type: ignore

    @staticmethod
    def clear_instance():
        """To clear the singleton during testing"""
        ZoneIdStoreSingleton._instance = None

    @staticmethod
    def _try_build_zone_id_index_map(config) -> IdStore:
        """Do this without using the utils of the segs / skims source, since this map is needed in the construction of the segs / skims source"""
        project_paths = config.get("project", {}).get("paden", {})
        skims_dir = project_paths.get("skims_directory", "")
        part_of_day = config.get("skims", {}).get("dagsoort", [])
        if not skims_dir or not part_of_day:
            raise ValueError("No skim directory or part of day found in config.")

        reference_path = (Path(skims_dir) / part_of_day[0] / "Auto_Tijd").with_suffix(".csv")
        if not reference_path.exists():
            raise ValueError(f"Car travel time path {reference_path} does not exist.")

        ids_array = np.loadtxt(
            reference_path,
            dtype=str,
            delimiter=",",
            skiprows=1,
            usecols=(0,),
            ndmin=1,
            encoding="utf-8-sig",
        )

        return IdStore.from_zone_ids(ids_array.tolist(), zone_source="first column of Auto_Tijd skim file")
