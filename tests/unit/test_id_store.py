import numpy as np
import pytest

from ikob.id_store import IdStore


def test_from_zone_ids_rejects_duplicates():
    with pytest.raises(ValueError):
        IdStore.from_zone_ids(["z1", "z2", "z1"])


@pytest.mark.parametrize(
    "values, expected",
    [
        ([20, 30, 10], [10, 20, 30]),
        ([[20, 21], [30, 31], [10, 11]], [[10, 11], [20, 21], [30, 31]]),
    ],
)
def test_reorder_rows_to_internal_idx(values, expected):
    store = IdStore.from_zone_ids(["z1", "z2", "z3"])
    values = np.array(values)
    original = values.copy()

    actual = store.reorder_rows_to_internal_idx(["z2", "z3", "z1"], values, "")

    np.testing.assert_array_equal(actual, expected)
    np.testing.assert_array_equal(values, original)


@pytest.mark.parametrize(
    "values, expected",
    [
        ([[20, 30, 10]], [[10, 20, 30]]),
        ([[20, 30, 10], [21, 31, 11]], [[10, 20, 30], [11, 21, 31]]),
    ],
)
def test_reorder_columns_to_internal_idx(values, expected):
    store = IdStore.from_zone_ids(["z1", "z2", "z3"])
    values = np.array(values)
    original = values.copy()

    actual = store.reorder_columns_to_internal_idx(["z2", "z3", "z1"], values, "")

    np.testing.assert_array_equal(actual, expected)
    np.testing.assert_array_equal(values, original)


@pytest.mark.parametrize("reorder", [IdStore.reorder_rows_to_internal_idx, IdStore.reorder_columns_to_internal_idx])
def test_reorder_preserves_already_aligned_values(reorder):
    store = IdStore.from_zone_ids(["z2", "z1"])
    values = np.array([[1, 2], [3, 4]])

    np.testing.assert_array_equal(reorder(store, ["z2", "z1"], values, "input.csv"), values)


@pytest.mark.parametrize("reorder", [IdStore.reorder_rows_to_internal_idx, IdStore.reorder_columns_to_internal_idx])
def test_reorder_rejects_duplicate_ids(reorder):
    store = IdStore.from_zone_ids(["z1", "z2"])

    with pytest.raises(ValueError):
        reorder(store, ["z1", "z2", "z1"], np.zeros((3, 3)), "input.csv")


@pytest.mark.parametrize("reorder", [IdStore.reorder_rows_to_internal_idx, IdStore.reorder_columns_to_internal_idx])
def test_reorder_rejects_missing_ids(reorder):
    store = IdStore.from_zone_ids(["z1", "z2", "z3"])

    with pytest.raises(ValueError, match="id mismatch"):
        reorder(store, ["z1", "z2"], np.zeros((2, 2)), "input.csv")


@pytest.mark.parametrize("reorder", [IdStore.reorder_rows_to_internal_idx, IdStore.reorder_columns_to_internal_idx])
def test_reorder_rejects_extra_ids(reorder):
    store = IdStore.from_zone_ids(["z1", "z2"])

    with pytest.raises(ValueError, match="id mismatch"):
        reorder(store, ["z1", "z2", "z3"], np.zeros((3, 3)), "input.csv")


def test_reorder_rows_rejects_id_count_mismatch_with_values():
    store = IdStore.from_zone_ids(["z1", "z2", "z3"])

    with pytest.raises(ValueError, match="Number of.*IDs.*does not match"):
        store.reorder_rows_to_internal_idx(["z1", "z2", "z3"], np.zeros((2, 3)), "input.csv")


def test_reorder_cols_rejects_id_count_mismatch_with_values():
    store = IdStore.from_zone_ids(["z1", "z2", "z3"])

    with pytest.raises(ValueError, match="Number of.*IDs.*does not match"):
        store.reorder_columns_to_internal_idx(["z1", "z2", "z3"], np.zeros((3, 2)), "input.csv")


def test_from_zone_ids_rejects_empty_list():
    with pytest.raises(ValueError):
        IdStore.from_zone_ids([])


def test_reorder_rows_rejects_empty_ids():
    store = IdStore.from_zone_ids(["z1", "z2"])

    with pytest.raises(ValueError):
        store.reorder_rows_to_internal_idx([], np.zeros((0, 2)), "input.csv")


def test_reorder_columns_rejects_empty_ids():
    store = IdStore.from_zone_ids(["z1", "z2"])

    with pytest.raises(ValueError):
        store.reorder_columns_to_internal_idx([], np.zeros((2, 0)), "input.csv")
