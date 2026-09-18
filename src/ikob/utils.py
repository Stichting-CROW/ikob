import logging
import pathlib
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from ikob.zone_id_store import ZoneIdStore

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
    filenaam, type_caster: type = FLOAT_DTYPE, has_id_column: bool = False, zone_id_store: ZoneIdStore | None = None
) -> npt.NDArray:
    """Return the matrix / vector in the csv"""
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    if has_id_column:
        if zone_id_store is None:
            raise ValueError(
                f"Unable to correctly read file with id column {filenaam} as no zone id store is provided for the mapping from zone id to internal index."
            )
        matrix, ids = read_csv_with_id_values(filenaam, type_caster)
        return zone_id_store.align_rows_to_skim_zone_ids(ids, matrix)

    # First, attempt to read without header.
    # If this fails, read with skipping the header.
    try:
        matrix = np.loadtxt(filenaam, dtype=type_caster, delimiter=",")
    except ValueError:
        matrix = np.loadtxt(filenaam, dtype=type_caster, skiprows=1, delimiter=",")

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


def read_csv_with_id_values(filenaam, type_caster: type = FLOAT_DTYPE) -> tuple[npt.NDArray, list[str]]:
    """Read csv data with an index/id column and return (ids, values).

    The first column is treated as ids and kept as strings.
    Remaining columns are cast to type_caster.
    """
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    first_non_empty_line = ""
    second_non_empty_line = ""
    with filenaam.open("r", encoding="utf-8-sig", newline="") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if not first_non_empty_line:
                first_non_empty_line = line
                continue
            second_non_empty_line = line
            break

    if not first_non_empty_line:
        raise ValueError(f"CSV file {filenaam} is empty.")

    first_parts = [part.strip() for part in first_non_empty_line.split(",")]
    if len(first_parts) < 2:
        raise ValueError(f"CSV file {filenaam} must contain at least an id column and one value column.")

    has_header = not _can_cast_all(first_parts[1:], type_caster)
    if has_header:
        if not second_non_empty_line:
            raise ValueError(f"CSV file {filenaam} has no data rows.")
        # The number of value columns is the total number of columns - 1
        num_value_columns = second_non_empty_line.count(",")
    else:
        num_value_columns = len(first_parts) - 1

    skiprows = 1 if has_header else 0
    usecols = tuple(range(1, num_value_columns + 1))

    try:
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
    except ValueError as exc:
        raise ValueError(
            f"CSV file {filenaam} has inconsistent row widths or values that cannot be cast to {type_caster}."
        ) from exc

    # If the matrix is really an array, return it as such
    if len(matrix.shape) == 2:
        if len(matrix[0, :]) == 1:
            matrix = matrix[:, 0]
        elif len(matrix[:, 0]) == 1:
            matrix = matrix[0]

    return matrix, ids_array.tolist()


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


def header_from_zone_ids(zone_list: list[str]):
    return ["zone_" + zone_id for zone_id in zone_list]


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
            [("id column", INT_DTYPE)] + [(f"data column {i}", matrix.dtype) for i in range(matrix.shape[1])]
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
):
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
