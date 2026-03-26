import logging
import pathlib
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


def zeros(lengte):
    return np.zeros(lengte)


def transpose(matrix):
    return np.array(matrix).T


def read_csv(filenaam, type_caster=float, has_index_column=False):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    # First, attempt to read without header.
    # If this fails, read with skipping the header.
    try:
        matrix = np.loadtxt(filenaam, dtype=type_caster, delimiter=",")
    except ValueError:
        matrix = np.loadtxt(filenaam, dtype=type_caster, skiprows=1, delimiter=",")
    if has_index_column:
        return matrix[:, 1:]
    else:
        return matrix


def read_csv_int(filenaam, has_index_column=False):
    return read_csv(filenaam, type_caster=int, has_index_column=has_index_column)


def read_csv_float(filenaam, has_index_column=False):
    return read_csv(filenaam, type_caster=float, has_index_column=has_index_column)


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
