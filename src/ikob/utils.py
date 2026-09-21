import logging
import pathlib
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from ikob.id_store import IdStore

logger = logging.getLogger(__name__)

# This is used throughout the code as a pseudo infinite travel time that's still outputted as a number
IKOB_INFINITE = 9999.0
FLOAT_DTYPE = np.float32
INT_DTYPE = np.int32


def zeros(lengte):
    return np.zeros(lengte, dtype=FLOAT_DTYPE)


def transpose(matrix):
    return np.asarray(matrix).T


def read_csv(
    filename,
    type_caster: type = FLOAT_DTYPE,
    has_id_column: bool = True,
    has_id_header: bool = False,
    id_store: IdStore | None = None,
) -> npt.NDArray:
    """Return the matrix / vector in the csv in the given type

    If has_id_column is true the first column is taken to be a column of row id's,
    an IdStore is required to map the ids to a consistent internal representation regardless of the order of the rows in the input file.
    Similarly, if has_id_header is true the header row is taken to be a list of column id's to be mapped to a consistent internal id.

    """
    if not isinstance(filename, pathlib.Path):
        filename = pathlib.Path(filename)

    if has_id_column:
        if id_store is None:
            raise ValueError(
                f"Unable to correctly read file with id column {filename} as no id store is provided for the mapping from id to internal index."
            )
        matrix, ids, header = read_csv_with_id_values(filename, type_caster)
        id_store.validate_exact_ids(ids, str(filename))
        if has_id_header:
            if header is None:
                raise ValueError(f"File {filename} was loaded as having an id header, but it has no header.")
            matrix_header = header[1:]  # The first entry is the header of the index column
            id_store.validate_exact_ids(matrix_header, str(filename))
            matrix = id_store.reorder_columns_to_internal_idx(matrix_header, matrix)
        return id_store.reorder_rows_to_internal_idx(ids, matrix)

    # First, attempt to read without header.
    # If this fails, read with skipping the header.
    try:
        matrix = np.loadtxt(filename, dtype=type_caster, delimiter=",")
        has_header = False
    except ValueError:
        matrix = np.loadtxt(filename, dtype=type_caster, skiprows=1, delimiter=",")
        has_header = True

    if has_id_header:
        if not has_header:
            raise ValueError(f"File {filename} was loaded as having an id header but it has no header.")
        if id_store is None:
            raise ValueError(
                f"Unable to correctly read file with id header {filename} as no id store is provided for the mapping from id to internal index."
            )

        with filename.open("r") as f:
            matrix_header = None
            for raw_line in f:
                matrix_header = raw_line.strip().split(",")[1:]  # The first entry is the header of the index column
                break
            if matrix_header is None:
                raise ValueError(f"File {filename} was loaded as having an id header but it has no header.")
            matrix = id_store.reorder_columns_to_internal_idx(matrix_header, matrix)

    # If the matrix is really an array, return it as such
    if len(matrix.shape) == 2:
        if len(matrix[0, :]) == 1:
            matrix = matrix[:, 0]
        if len(matrix[:, 0]) == 1:
            matrix = matrix[0]
    return matrix


def _can_cast_all(values: list[str], type_caster: type) -> bool:
    for value in values:
        text = value.strip()
        if text == "":
            return False
        try:
            type_caster(text)
        except (TypeError, ValueError):
            return False
    return True


def read_csv_with_id_values(filenaam, type_caster: type) -> tuple[npt.NDArray, list[str], list[str] | None]:
    """Read csv data with an index/id column and return (values, id's, headers).

    The first column is treated as ids and kept as strings.
    Remaining columns are cast to type_caster.
    """
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    first_non_empty_line = ""
    with filenaam.open("r") as f:
        for raw_line in f:
            line = raw_line.strip()
            first_non_empty_line = line
            break

    if not first_non_empty_line:
        raise ValueError(f"CSV file {filenaam} is empty.")

    first_parts = [part.strip() for part in first_non_empty_line.split(",")]
    if len(first_parts) < 2:
        raise ValueError(f"CSV file {filenaam} must contain at least an id column and one value column.")

    has_header = not _can_cast_all(first_parts[1:], type_caster)
    header = first_parts if has_header else None

    # The number of value columns is the total number of columns - 1
    num_value_columns = len(first_parts) - 1

    skiprows = 1 if has_header else 0
    usecols = tuple(range(1, num_value_columns + 1))

    matrix = np.loadtxt(
        filenaam,
        dtype=type_caster,
        delimiter=",",
        skiprows=skiprows,
        usecols=usecols,
        ndmin=2,
    )
    ids_array = np.loadtxt(
        filenaam,
        dtype=str,
        delimiter=",",
        skiprows=skiprows,
        usecols=(0,),
        ndmin=1,
        encoding="utf-8-sig",
    )

    # If the matrix is really an array, return it as such
    if len(matrix.shape) == 2:
        if len(matrix[0, :]) == 1:
            matrix = matrix[:, 0]
        elif len(matrix[:, 0]) == 1:
            matrix = matrix[0]

    return matrix, ids_array.tolist(), header


def _check_index_column(matrix: npt.NDArray, filenaam):
    """Assert that the given index column contains indices in sequential order, starting at 1: 1,2,3,4"""
    index_column = matrix[:, 0]
    if len(matrix.shape) != 2:
        raise ValueError(
            f"Reading file {filenaam} as a file with index column, but the matrix it contains is not two dimensional, so it cannot contain an index column."
        )
    prev_index = 0
    for idx in index_column:
        if abs(round(idx) - idx) > 1e-5:
            raise ValueError(f"Csv file {filenaam} has an invalid index column because index {idx} is not integer.")
        idx = round(idx)
        if idx - prev_index != 1:
            raise ValueError(f"Csv file {filenaam} has an invalid index column because the index is not sequential.")
        prev_index = idx


@dataclass
class CsvIdColumn:
    name: str = ""
    values: list[str] = field(default_factory=list)

    @classmethod
    def from_zone_ids(cls, zone_list: list[str]):
        return cls("zone", zone_list)


def write_csv(matrix, filenaam, index: CsvIdColumn, header: list[str]):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    matrix = np.asarray(matrix)
    if matrix.ndim == 1:
        # One dimensional data is expected as one row, while
        # np.savetxt writes this by default as one column.
        matrix = matrix.reshape(1, -1)

    # Determine format for data
    data_fmt = "%d" if np.issubdtype(matrix.dtype, np.integer) else "%.6e"

    # Add index column if provided
    if len(index.values) > 0:
        index_col = np.asarray(index.values)
        # We need to use a struct type to avoid promoting the dtype when combining with index column int dtype
        struct_dtype = np.dtype(
            [("id column", index_col.dtype)] + [(f"data column {i}", matrix.dtype) for i in range(matrix.shape[1])]
        )
        combined = np.empty(matrix.shape[0], dtype=struct_dtype)
        combined["id column"] = index_col
        for i in range(matrix.shape[1]):
            combined[f"data column {i}"] = matrix[:, i]
        matrix = combined
        header = [index.name, *header]
        # Index is always a string, data keeps its original format
        field_names = struct_dtype.names or ()
        fmt = ["%s"] + [data_fmt] * (len(field_names) - 1)
    else:
        fmt = data_fmt

    delim = ","
    header_line = delim.join(header)
    np.savetxt(filenaam, matrix, fmt=fmt, delimiter=delim, header=header_line, comments="")


def group_income_level(naam):
    if naam[-4:] == "hoog":
        if naam[-10:] == "middelhoog":
            return "middelhoog"
        else:
            return "hoog"
    elif naam[-4:] == "laag":
        if naam[-10:] == "middellaag":
            return "middellaag"
        else:
            return "laag"
    else:
        return ""


def find_preference(naam, mod):
    if "vk" in naam:
        Beginvk = naam.find("vk")
        if naam[Beginvk + 2] == "A":
            return "Auto"
        elif naam[Beginvk + 2] == "N":
            return "Neutraal"
        elif naam[Beginvk + 2] == "O":
            return "OV"
        elif naam[Beginvk + 2] == "F":
            return "Fiets"
        else:
            return ""
    elif "GratisAuto" in naam:
        if "GratisAuto_GratisOV" in naam and "OV" in mod and "Auto" in mod:
            return "Neutraal"
        else:
            if "Auto" in mod:
                return "Auto"
            else:
                return "OV"
    elif "GratisOV" in naam:
        return "OV"
    else:
        return ""


def single_group(mod, gr):
    if mod == "Auto":
        if "GratisAuto" in gr:
            return "GratisAuto"
        elif "Wel" in gr:
            return "Auto"
        if "GeenAuto" in gr:
            return "GeenAuto"
        if "GeenRijbewijs" in gr:
            return "GeenRijbewijs"
    if mod == "OV":
        if "GratisOV" in gr:
            return "GratisOV"
        else:
            return "OV"


def combined_group(mod, gr):
    string = ""
    if "Auto" in mod:
        if "GratisAuto" in gr:
            string = "GratisAuto"
        elif "Wel" in gr:
            string = "Auto"
        if "GeenAuto" in gr:
            string = "GeenAuto"
        if "GeenRijbewijs" in gr:
            string = "GeenRijbewijs"
    if "OV" in mod:
        if "GratisOV" in gr:
            if string == "":
                string = string + "GratisOV"
            else:
                string = string + "_GratisOV"
        else:
            if string == "":
                string = string + "OV"
            else:
                string = string + "_OV"
    if "EFiets" in mod:
        string = string + "_EFiets"
    elif "Fiets" in mod:
        string = string + "_Fiets"
    return string


"""
Some functions that compute general travel time / costs to avoid copying this logic
"""


def compute_bike_gtt(
    bike_time_matrix: npt.NDArray,
    bike_distance_matrix: npt.NDArray,
    bike_cost_euro_per_km: float,
    tvom_factor: float,
):
    return bike_time_matrix + tvom_factor * bike_distance_matrix * bike_cost_euro_per_km


def compute_pt_gtt(pt_time_matrix: npt.NDArray, pt_cost_matrix: npt.NDArray, tvom_factor: float):
    return np.where(pt_time_matrix > 0.5, pt_time_matrix + tvom_factor * pt_cost_matrix, IKOB_INFINITE)


def compute_car_gtt(
    car_time: npt.NDArray,
    car_dist: npt.NDArray,
    var_rate: float,
    road_pricing: float,
    tvom_factor: float,
    additional_costs_eurocent: npt.NDArray,
    parking_times_array: npt.NDArray,
    parking_costs_array_eurocent: npt.NDArray,
) -> npt.NDArray:
    parking_time_matrix = parking_times_array[:, 0][:, np.newaxis] + parking_times_array[:, 1][np.newaxis, :]
    return (
        car_time
        + parking_time_matrix
        + tvom_factor
        * ((var_rate + road_pricing) * car_dist + additional_costs_eurocent / 100 + parking_costs_array_eurocent / 100)
    )


def costs_public_transport(distance, pt_km_price, starting_rate, pricecap, pricecap_value):
    distance = np.where(distance < 0, 0, distance)
    distance = starting_rate + distance * pt_km_price

    if pricecap:
        np.clip(distance, None, pricecap_value, out=distance)

    return distance
