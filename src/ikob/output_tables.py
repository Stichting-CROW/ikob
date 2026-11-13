from collections.abc import Iterator, Sequence
from dataclasses import replace

import numpy as np
from numpy.typing import NDArray

from ikob import utils
from ikob.datasource import DataKey, DataSource

# small type alias to have clearer type hints in this file
type IncomeClass = str
type IncomeTable = NDArray


class IncomeTableAssembler:
    """Combine per-income IKOB results into one multi-income output table.

    The runner processes one income class at a time so it can release that
    income's large weight matrices before processing the next. The calculation
    steps consequently produce a separate zone vector for each income and
    modality. Each assembler places one modality's vectors into the income
    columns used by a final CSV output.
    """

    def __init__(self, num_zones: int, incomes: Sequence[IncomeClass]):
        self.num_zones = num_zones
        self.incomes = tuple(incomes)
        if not self.incomes or len(set(self.incomes)) != len(self.incomes):
            raise ValueError("Income columns must be nonempty and unique.")
        self._table: IncomeTable | None = None
        self._income_classes_added_to_table: set[IncomeClass] = set()

    def add(self, income: IncomeClass, values: NDArray):
        column = self.incomes.index(income)

        if values.shape != (self.num_zones,):
            raise ValueError(f"Expected a result vector with shape ({self.num_zones},), got {values.shape}.")
        if income in self._income_classes_added_to_table:
            raise ValueError(f"Duplicate income column {income}.")

        if self._table is None:
            self._table = np.empty((self.num_zones, len(self.incomes)), dtype=values.dtype)

        self._table[:, column] = values
        self._income_classes_added_to_table.add(income)

    def finalize(self) -> IncomeTable:
        if self._table is None:
            raise ValueError("No income table has been assembled.")
        missing = set(self.incomes) - self._income_classes_added_to_table
        if missing:
            raise ValueError(f"Missing income columns: {missing}.")
        return self._table


def assemble_income_tables(source: DataSource, incomes: Sequence[str]) -> Iterator[tuple[DataKey, NDArray]]:
    assemblers: dict[DataKey, IncomeTableAssembler] = {}

    for key, values in source.cache.items():
        if key.id != utils.INCOME_VECTOR_RESULT_ID:
            continue
        if not isinstance(values, np.ndarray):
            raise TypeError("Income output tables require dense result vectors.")

        # The table assembler will combine results for _all_ income classes, so remove it from the table key
        table_key = replace(key, income="", header=list(incomes), is_intermediate=False)
        if table_key not in assemblers:
            assemblers[table_key] = IncomeTableAssembler(values.shape[0], incomes)
        assemblers[table_key].add(key.income, values)

    for key, assembler in assemblers.items():
        yield key, assembler.finalize()
