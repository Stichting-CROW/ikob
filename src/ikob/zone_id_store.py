from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dataclass
class ZoneIdStore:
    """A mapping for zone ID to zone index in the matrices used throughout the code"""

    zone_ids: list[str]

    def __post_init__(self):
        self.id_to_idx = {zone_id: idx for idx, zone_id in enumerate(self.zone_ids)}
        self.num_zones = len(self.zone_ids)

    def validate_exact_ids(self, row_ids: list[str], source_name: str):
        reference = set(self.zone_ids)
        current = set(row_ids)
        missing_ids = reference - current
        extra_ids = current - reference
        if missing_ids or extra_ids:
            raise ValueError(
                f"Zone id mismatch for {source_name}. Missing ids: {len(missing_ids)}, extra ids: {len(extra_ids)}"
            )

    def align_rows_to_skim_zone_ids(self, row_ids: list[str], values: NDArray) -> NDArray:
        row_id_to_idx = {row_id: row_idx for row_idx, row_id in enumerate(row_ids)}
        reordered_row_idx = [row_id_to_idx[zone_id] for zone_id in self.zone_ids]
        return values[reordered_row_idx]


class ZoneIdStoreSingleton:
    _instance: ZoneIdStore | None = None

    @staticmethod
    def get_instance(config) -> ZoneIdStore:
        if ZoneIdStoreSingleton._instance is None:
            ZoneIdStoreSingleton._instance = ZoneIdStoreSingleton._try_build_zone_id_index_map(config)

        return ZoneIdStoreSingleton._instance  # type: ignore

    @staticmethod
    def _try_build_zone_id_index_map(config) -> ZoneIdStore:
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

        return ZoneIdStore(ids_array.tolist())
