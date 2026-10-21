import numpy as np
import pytest

from ikob.datasource import DataKey, DataSource, DataType
from ikob.output_tables import IncomeTableAssembler, assemble_income_tables


@pytest.mark.parametrize("num_zones", [1, 3])
@pytest.mark.parametrize("incomes", [["laag"], ["laag", "middellaag", "middelhoog", "hoog"]])
def test_assemble_income_columns_in_header_order(num_zones, incomes):
    assembler = IncomeTableAssembler(num_zones, incomes)
    expected = np.arange(num_zones * len(incomes), dtype=np.float32).reshape(num_zones, len(incomes))

    for column in reversed(range(len(incomes))):
        for modality in ["Auto", "Fiets"]:
            assembler.add(incomes[column], modality, expected[:, column])

    tables = assembler.finalize()

    for modality in ["Auto", "Fiets"]:
        np.testing.assert_array_equal(tables[modality], expected)
        assert tables[modality].dtype == expected.dtype


def test_assembly_copies_unrounded_results():
    assembler = IncomeTableAssembler(2, ["laag"])
    values = np.array([1.25, 2.75])

    assembler.add("laag", "Auto", values)
    values[:] = 0

    np.testing.assert_array_equal(assembler.finalize()["Auto"], [[1.25], [2.75]])


def test_assembly_preserves_precision_across_incomes():
    assembler = IncomeTableAssembler(1, ["laag", "hoog"])
    assembler.add("laag", "Auto", np.array([1], dtype=int))
    assembler.add("hoog", "Auto", np.array([1.25]))

    np.testing.assert_array_equal(assembler.finalize()["Auto"], [[1, 1.25]])


@pytest.mark.parametrize("incomes", [[], ["laag", "laag"]])
def test_reject_invalid_income_columns(incomes):
    with pytest.raises(ValueError):
        IncomeTableAssembler(2, incomes)


@pytest.mark.parametrize("values", [np.zeros(3), np.zeros((2, 1)), np.array(1)])
def test_reject_invalid_vector_shape(values):
    assembler = IncomeTableAssembler(2, ["laag"])

    with pytest.raises(ValueError):
        assembler.add("laag", "Auto", values)


def test_reject_unknown_income():
    assembler = IncomeTableAssembler(2, ["laag"])

    with pytest.raises(ValueError):
        assembler.add("hoog", "Auto", np.zeros(2))


def test_reject_duplicate_income_column():
    assembler = IncomeTableAssembler(2, ["laag"])
    assembler.add("laag", "Auto", np.zeros(2))

    with pytest.raises(ValueError):
        assembler.add("laag", "Auto", np.ones(2))

    np.testing.assert_array_equal(assembler.finalize()["Auto"], np.zeros((2, 1)))


def test_reject_incomplete_modality():
    assembler = IncomeTableAssembler(2, ["laag", "hoog"])
    assembler.add("laag", "Auto", np.zeros(2))
    assembler.add("hoog", "Auto", np.zeros(2))
    assembler.add("laag", "Fiets", np.zeros(2))

    with pytest.raises(ValueError):
        assembler.finalize()


def test_reject_empty_assembly():
    assembler = IncomeTableAssembler(2, ["laag"])

    with pytest.raises(ValueError):
        assembler.finalize()


def test_assemble_source_tables_keeps_contexts_separate(tmp_path):
    source = DataSource(
        {"__filename__": "test", "project": {"paden": {"output_directory": str(tmp_path)}}},
        DataType.DESTINATIONS,
    )
    incomes = ["laag", "hoog"]
    for part_of_day in ["spits", "restdag"]:
        for group in ["alle groepen", "alleen autobezit"]:
            for modality in ["Auto", "Fiets"]:
                for income in reversed(incomes):
                    key = DataKey(
                        "Totaal",
                        part_of_day=part_of_day,
                        group=group,
                        modality=modality,
                        income=income,
                        is_intermediate=True,
                    )
                    source.set(key, np.array([1.25, 2.75]) + incomes.index(income))

    tables = dict(assemble_income_tables(source, incomes))

    assert len(tables) == 8
    for key, values in tables.items():
        assert key.income == ""
        assert key.header == incomes
        assert not key.is_intermediate
        np.testing.assert_array_equal(values, [[1.25, 2.25], [2.75, 3.75]])
