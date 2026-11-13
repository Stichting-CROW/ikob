import numpy as np
import pytest

from ikob import utils
from ikob.datasource import DataKey, DataSource, DataType
from ikob.output_tables import IncomeTableAssembler, assemble_income_tables


def test_assemble_income_columns_in_header_order():
    incomes = ["laag", "middellaag", "middelhoog", "hoog"]
    num_zones = 4

    assembler = IncomeTableAssembler(num_zones, incomes)
    expected = np.arange(num_zones * len(incomes), dtype=np.float32).reshape(num_zones, len(incomes))

    for column in reversed(range(len(incomes))):
        assembler.add(incomes[column], expected[:, column])

    table = assembler.finalize()

    np.testing.assert_array_equal(table, expected)
    assert table.dtype == expected.dtype


def test_assembly_copies_results():
    assembler = IncomeTableAssembler(2, ["laag"])
    values = np.array([1.25, 2.75])

    assembler.add("laag", values)
    values[:] = 0

    np.testing.assert_array_equal(assembler.finalize(), [[1.25], [2.75]])


@pytest.mark.parametrize("incomes", [[], ["laag", "laag"]])
def test_reject_invalid_income_columns(incomes):
    with pytest.raises(ValueError):
        IncomeTableAssembler(2, incomes)


@pytest.mark.parametrize("values", [np.zeros(3), np.zeros((2, 1)), np.array(1)])
def test_reject_invalid_vector_shape(values):
    assembler = IncomeTableAssembler(2, ["laag"])

    with pytest.raises(ValueError):
        assembler.add("laag", values)


def test_reject_unknown_income():
    assembler = IncomeTableAssembler(2, ["laag"])

    with pytest.raises(ValueError):
        assembler.add("hoog", np.zeros(2))


def test_reject_duplicate_income_column():
    assembler = IncomeTableAssembler(2, ["laag"])
    assembler.add("laag", np.zeros(2))

    with pytest.raises(ValueError):
        assembler.add("laag", np.ones(2))

    np.testing.assert_array_equal(assembler.finalize(), np.zeros((2, 1)))


def test_reject_incomplete_table():
    assembler = IncomeTableAssembler(2, ["laag", "hoog"])
    assembler.add("laag", np.zeros(2))

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
                for income in incomes:
                    key = DataKey(
                        utils.INCOME_VECTOR_RESULT_ID,
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
