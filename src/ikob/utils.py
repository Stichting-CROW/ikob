import pathlib

import numpy as np
import xlsxwriter


def zeros(lengte):
    return np.zeros(lengte)


def transpose(matrix):
    return np.array(matrix).T


def write_xls(matrix, filenaam, header):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    workbook = xlsxwriter.Workbook(filenaam)
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, header)
    for r in range(0, len(matrix)):
        worksheet.write(r + 1, 0, r + 1)
        worksheet.write_row(r + 1, 1, matrix[r])
    workbook.close()


def read_csv(filenaam, type_caster=float):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    # First, attempt to read without header.
    # If this fails, read with skipping the header.
    try:
        matrix = np.loadtxt(filenaam,
                            dtype=type_caster,
                            delimiter=',')
    except ValueError:
        matrix = np.loadtxt(filenaam,
                            dtype=type_caster,
                            skiprows=1,
                            delimiter=',')
    return matrix


def read_csv_int(filenaam):
    return read_csv(filenaam, type_caster=int)


def read_csv_float(filenaam):
    return read_csv(filenaam, type_caster=float)


def write_csv(matrix, filenaam, header=[]):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    matrix = np.array(matrix)
    if matrix.ndim == 1:
        # One dimensional data is expected as one row, while
        # np.savetxt writes this by default as one column.
        matrix = matrix.reshape(1, matrix.shape[0])

    delim = ","
    header = delim.join(header)
    np.savetxt(filenaam,
               matrix,
               delimiter=delim,
               header=header,
               comments='')


def group_income_level(naam):
    if naam[-4:] == 'hoog':
        if naam[-10:] == 'middelhoog':
            return 'middelhoog'
        else:
            return 'hoog'
    elif naam[-4:] == 'laag':
        if naam[-10:] == 'middellaag':
            return 'middellaag'
        else:
            return 'laag'
    else:
        return ''


def find_preference(naam, mod):
    if 'vk' in naam:
        Beginvk = naam.find('vk')
        if naam[Beginvk + 2] == "A":
            return 'Auto'
        elif naam[Beginvk + 2] == "N":
            return 'Neutraal'
        elif naam[Beginvk + 2] == "O":
            return 'OV'
        elif naam[Beginvk + 2] == "F":
            return 'Fiets'
        else:
            return ''
    elif 'GratisAuto' in naam:
        if 'GratisAuto_GratisOV' in naam and 'OV' in mod and 'Auto' in mod:
            return 'Neutraal'
        else:
            if 'Auto' in mod:
                return 'Auto'
            else:
                return 'OV'
    elif 'GratisOV' in naam:
        return 'OV'
    else:
        return ''


def single_group(mod, gr):
    if mod == 'Auto':
        if 'GratisAuto' in gr:
            return 'GratisAuto'
        elif 'Wel' in gr:
            return 'Auto'
        if 'GeenAuto' in gr:
            return 'GeenAuto'
        if 'GeenRijbewijs' in gr:
            return 'GeenRijbewijs'
    if mod == 'OV':
        if 'GratisOV' in gr:
            return 'GratisOV'
        else:
            return 'OV'


def combined_group(mod, gr):
    string = ''
    if 'Auto' in mod:
        if 'GratisAuto' in gr:
            string = 'GratisAuto'
        elif 'Wel' in gr:
            string = 'Auto'
        if 'GeenAuto' in gr:
            string = 'GeenAuto'
        if 'GeenRijbewijs' in gr:
            string = 'GeenRijbewijs'
    if 'OV' in mod:
        if 'GratisOV' in gr:
            if string == '':
                string = string + 'GratisOV'
            else:
                string = string + '_GratisOV'
        else:
            if string == '':
                string = string + 'OV'
            else:
                string = string + '_OV'
    if 'EFiets' in mod:
        string = string + '_EFiets'
    elif 'Fiets' in mod:
        string = string + '_Fiets'
    return string
