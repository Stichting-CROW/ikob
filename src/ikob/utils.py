import logging
import pathlib
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)

# This is used throughout the code as a pseudo infinite travel time that's still outputted as a number
IKOB_INFINITE = 9999.0


def zeros(lengte):
    return np.zeros(lengte)


def transpose(matrix):
    return np.array(matrix).T


def read_csv(filenaam, type_caster=float, has_index_column=True):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    # First, attempt to read without header.
    # If this fails, read with skipping the header.
    try:
        matrix = np.loadtxt(filenaam, dtype=type_caster, delimiter=",")
        if has_index_column:
            logger.warning(f"Reading file {filenaam} without headers, but with an index column.")
    except ValueError:
        matrix = np.loadtxt(filenaam, dtype=type_caster, skiprows=1, delimiter=",")
    if has_index_column:
        _check_index_column(matrix, filenaam)
        matrix = matrix[:, 1:]
    # If the matrix is really an array, return it as such
    if len(matrix.shape) == 2:
        if len(matrix[0, :]) == 1:
            return matrix[:, 0]
        if len(matrix[:, 0]) == 1:
            return matrix[0]
    return matrix


def read_csv_int(filenaam, has_index_column=True):
    return read_csv(filenaam, type_caster=int, has_index_column=has_index_column)


def read_csv_float(filenaam, has_index_column=True):
    return read_csv(filenaam, type_caster=float, has_index_column=has_index_column)


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
        idx = int(round(idx))
        if idx - prev_index != 1:
            raise ValueError(f"Csv file {filenaam} has an invalid index column because the index is not sequential.")
        prev_index = idx


@dataclass
class CsvIndex:
    name: str = ""
    values: list[int] = field(default_factory=list)

    @classmethod
    def zone_index(cls, num_zones):
        return cls("zone", list(range(1, num_zones + 1)))


def write_csv(matrix, filenaam, index=CsvIndex(), header=[]):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    matrix = np.array(matrix)
    if matrix.ndim == 1:
        # One dimensional data is expected as one row, while
        # np.savetxt writes this by default as one column.
        matrix = matrix.reshape(1, matrix.shape[0])

    # Determine format for data
    data_fmt = "%d" if np.isdtype(matrix.dtype, "integral") else "%.18e"

    # Add index column if provided
    if len(index.values) > 0:
        index_col = np.array(index.values).reshape(-1, 1)
        matrix = np.hstack([index_col, matrix])
        header = [index.name, *header]
        # Index is always integer, data keeps its original format
        fmt = ["%d"] + [data_fmt] * (matrix.shape[1] - 1)
    else:
        fmt = data_fmt

    delim = ","
    header = delim.join(header)
    np.savetxt(filenaam, matrix, fmt=fmt, delimiter=delim, header=header, comments="")


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
