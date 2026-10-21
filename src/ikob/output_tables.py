from collections.abc import Iterator, Sequence
from dataclasses import replace

import numpy as np
from numpy.typing import NDArray

from ikob import utils
from ikob.datasource import DataKey, DataSource

# small type alias to have clearer type hints in this file
type IncomeClass = str
type Modality = str
type IncomeTable = NDArray


class IncomeTableAssembler:
    """Combine per-income IKOB results into the multi-income output tables.

    The runner processes one income class at a time so it can release that
    income's large weight matrices before processing the next. The calculation
    steps consequently produce a separate zone vector for each income and
    modality. This assembler places those vectors into the income columns used
    by the final CSV outputs.
    """

    def __init__(self, num_zones: int, incomes: Sequence[IncomeClass]):
        self.num_zones = num_zones
        self.incomes = tuple(incomes)
        if not self.incomes or len(set(self.incomes)) != len(self.incomes):
            raise ValueError("Income columns must be nonempty and unique.")
        self._tables: dict[Modality, IncomeTable] = {}
        self._completed: dict[Modality, set[IncomeClass]] = {}

    def add(self, income: IncomeClass, modality: Modality, values: NDArray):
        column = self.incomes.index(income)
        values = np.asarray(values)
        if values.shape != (self.num_zones,):
            raise ValueError(f"Expected a result vector with shape ({self.num_zones},), got {values.shape}.")
        if income in self._completed.get(modality, set()):
            raise ValueError(f"Duplicate income column {income} for {modality}.")

        if modality not in self._tables:
            self._tables[modality] = np.empty((self.num_zones, len(self.incomes)), dtype=values.dtype)
            self._completed[modality] = set()
        else:
            dtype = np.result_type(self._tables[modality].dtype, values.dtype)
            if dtype != self._tables[modality].dtype:
                self._tables[modality] = self._tables[modality].astype(dtype)

        self._tables[modality][:, column] = values
        self._completed[modality].add(income)

    def finalize(self) -> dict[Modality, IncomeTable]:
        if not self._tables:
            raise ValueError("No income tables have been assembled.")
        for modality, completed in self._completed.items():
            missing = set(self.incomes) - completed
            if missing:
                raise ValueError(f"Missing income columns for {modality}: {missing}.")
        return self._tables.copy()


def assemble_income_tables(source: DataSource, incomes: Sequence[str]) -> Iterator[tuple[DataKey, NDArray]]:
    assemblers: dict[DataKey, IncomeTableAssembler] = {}
    for key, values in source.cache.items():
        if key.id != utils.INCOME_VECTOR_RESULT_ID:
            continue
        if not isinstance(values, np.ndarray):
            raise TypeError("Income output tables require dense result vectors.")
        table_key = replace(key, income="", header=list(incomes), is_intermediate=False)
        if table_key not in assemblers:
            assemblers[table_key] = IncomeTableAssembler(values.shape[0], incomes)
        assemblers[table_key].add(key.income, key.modality, values)

    for key, assembler in assemblers.items():
        yield key, assembler.finalize()[key.modality]
