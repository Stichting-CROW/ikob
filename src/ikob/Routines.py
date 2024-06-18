import xlsxwriter
import pathlib
import numpy as np


def lijstvolnullen(lengte):
    return [0] * lengte


def transponeren(matrix):
    return [list(i) for i in zip(*matrix)]


def xlswegschrijven(matrix, filenaam, header):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    workbook = xlsxwriter.Workbook(filenaam)
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, header)
    for r in range(0, len(matrix)):
        worksheet.write(r+1, 0, r+1)
        worksheet.write_row(r + 1, 1, matrix[r])
    workbook.close()


def xlswegschrijven_totalen(matrix, header, getallenlijst, filenaam, aantal_zones=1425):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    transmatrix = transponeren(matrix)
    workbook = xlsxwriter.Workbook(filenaam)
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, header)
    worksheet.write_column(1, 0, getallenlijst)
    for r in range(0, 1425):
        worksheet.write_row(r + 1, 1, transmatrix[r])
    workbook.close()


def getallenlijst_maken(aantal_getallen):
    return list(range(1, aantal_getallen + 1))


def csvlezen(filenaam, type_caster=float):
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


def csvintlezen(filenaam):
    return csvlezen(filenaam, type_caster=int)


def csvfloatlezen(filenaam):
    return csvlezen(filenaam, type_caster=float)


def csvwegschrijven(matrix, filenaam, header=[]):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    matrix = np.array(matrix)
    if matrix.ndim == 1:
        # One dimensional data is expected as one row, while
        # np.savetxt writes this by default as one column.
        matrix = matrix.reshape(1, matrix.shape[0])

    # Explicitly format integers as integers.
    fmt = "%d" if np.issubdtype(matrix.dtype, np.integer) else "%.16f"
    delim = ","
    header = delim.join(header)

    np.savetxt(filenaam,
               matrix,
               fmt=fmt,
               delimiter=delim,
               header=header,
               comments='')


def minmaxmatrix(Matrix1, Matrix2, minmax="max"):
    Eindmatrix = []
    for i in range(0, len(Matrix1)):
        Eindmatrix.append([])
        for j in range(0, len(Matrix1)):
            if minmax == "max":
                Eindmatrix[i].append(max(Matrix1[i][j], Matrix2[i][j]))
            else:
                Eindmatrix[i].append(min(Matrix1[i][j], Matrix2[i][j]))
    return Eindmatrix


def minmaxmatrix3(matrix1, matrix2, matrix3, minmax="max"):
    eindmatrix = []
    for i in range(0, len(matrix1)):
        eindmatrix.append([])
        for j in range(0, len(matrix1)):
            if minmax == "max":
                eindmatrix[i].append(max(matrix1[i][j], matrix2[i][j], matrix3[i][j]))
            else:
                eindmatrix[i].append(min(matrix1[i][j], matrix2[i][j], matrix3[i][j]))
    return eindmatrix


def inkomensgroepbepalen(naam):
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


def vindvoorkeur(naam, mod):
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


def enkelegroep(mod, gr):
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


def combigroep(mod, gr):
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
