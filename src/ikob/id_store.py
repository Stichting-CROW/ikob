import logging
from collections import Counter
from dataclasses import dataclass, field
from types import MappingProxyType

from numpy.typing import NDArray

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IdStore:
    """A mapping for (zone) ID to (zone) index in the matrices used throughout the code

    Zone is in between brackets as this class is mainly used for converting zone id's to indices but can also be used to correctly read
    files with different id's such as urbanization grades.
    """

    _zone_ids: tuple[str, ...] = field(hash=True)
    # MappingProxyType is essentially an immutable dict
    _id_to_idx: MappingProxyType[str, int] = field(hash=False)
    _num_zones: int = field(hash=False)
    _zone_source: str = field(hash=False)
    _allow_extra_ids: bool = field(default=False)

    @classmethod
    def from_zone_ids(cls, zone_ids: list[str], zone_source="", allow_extra_ids=False):
        if not zone_ids:
            raise ValueError(
                "Empty zone IDs provided to id store constructor" + (f" from {zone_source}" if zone_source else "")
            )

        duplicates = {zone_id for zone_id, count in Counter(zone_ids).items() if count > 1}
        if duplicates:
            logger.warning(
                "IdStore initialized with duplicate IDs found in %s: %s.", zone_source or "zone IDs", duplicates
            )
            zone_ids = list(dict.fromkeys(zone_ids))

        id_to_idx = {zone_id: idx for idx, zone_id in enumerate(zone_ids)}
        num_zones = len(zone_ids)
        return cls(tuple(zone_ids), MappingProxyType(id_to_idx.copy()), num_zones, zone_source, allow_extra_ids)

    def _validate_exact_ids(self, ids: list[str], source_name: str):
        reference = set(self._zone_ids)
        duplicates = {zone_id for zone_id, count in Counter(ids).items() if count > 1}
        if duplicates:
            msg = f"Duplicate IDs found in {source_name}: {duplicates}. Using the first occurrence."
            if self._allow_extra_ids:
                logger.warning(msg)
            else:
                raise ValueError(msg)

        current = set(ids)
        missing_ids = reference - current
        extra_ids = current - reference
        if missing_ids or (extra_ids and not self._allow_extra_ids):
            msg = f"id mismatch for {source_name}.\nMissing ids: {missing_ids}\nextra ids: {extra_ids}"
            msg += ("\nid's have been read from " + self._zone_source) if self._zone_source else ""
            raise ValueError(msg)

    def reorder_rows_to_internal_idx(self, row_ids: list[str], values: NDArray, source_name: str) -> NDArray:
        self._validate_exact_ids(row_ids, source_name)

        if len(row_ids) != values.shape[0]:
            raise ValueError(
                f"Number of row IDs ({len(row_ids)}) does not match the number of rows in values ({values.shape[0]}) "
                f"for {source_name}"
            )

        reordered_row_idx = self._reorder(row_ids)
        return values[reordered_row_idx]

    def reorder_columns_to_internal_idx(self, col_ids: list[str], values: NDArray, source_name: str) -> NDArray:
        self._validate_exact_ids(col_ids, source_name)

        if len(col_ids) != values.shape[1]:
            raise ValueError(
                f"Number of column IDs ({len(col_ids)}) does not match the number of columns in values ({values.shape[1]}) "
                f"for {source_name}"
            )

        reordered_col_idx = self._reorder(col_ids)
        return values[:, reordered_col_idx]

    def _reorder(self, ids):
        id_to_index: dict[str, int] = {}
        for index, id in enumerate(ids):
            # Use setdefault so a repeat of id does not overwrite the index
            # i.e. so we use the first row/column of of any duplicate row/column ids and not the last.
            id_to_index.setdefault(id, index)

        reordered_ids = [id_to_index[zone_id] for zone_id in self._zone_ids]
        return reordered_ids


class ZoneIdStoreSingleton:
    _instance: IdStore | None = None

    @staticmethod
    def set_instance(instance: IdStore):
        ZoneIdStoreSingleton._instance = instance

    @staticmethod
    def get_instance(config) -> IdStore:
        if ZoneIdStoreSingleton._instance is None:
            raise ValueError("No instance is set yet for this singleton")

        return ZoneIdStoreSingleton._instance  # type: ignore

    @staticmethod
    def clear_instance():
        """To clear the singleton during testing"""
        ZoneIdStoreSingleton._instance = None
