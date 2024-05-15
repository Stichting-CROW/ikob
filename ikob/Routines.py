import csv
import xlsxwriter
import pathlib


def lijstvolnullen(lengte):
    return [0] * lengte


def transponeren(matrix):
    return [list(i) for i in zip(*matrix)]


def xlswegschrijven(matrix, filenaam, header):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    workbook = xlsxwriter.Workbook(filenaam.with_suffix('.xlsx'))
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
    workbook = xlsxwriter.Workbook(filenaam.with_suffix('.xlsx'))
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, header)
    worksheet.write_column(1, 0, getallenlijst)
    for r in range(0, 1425):
        worksheet.write_row(r + 1, 1, transmatrix[r])
    workbook.close()


def getallenlijst_maken(aantal_getallen):
    return list(range(1, aantal_getallen + 1))


def csvlezen(filenaam, aantal_lege_regels=0, type_caster=float):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)
    filenaam = filenaam.with_suffix('.csv')

    matrix = []

    with open(filenaam, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for i in range(aantal_lege_regels):
            next(reader)
        for row in reader:
            matrix.append(row)
    with open(filenaam, 'r') as csvfile:
        reader = csv.reader(csvfile)
        row_count = sum(1 for row in reader)
    uitmatrix = []
    tussenmatrix = []
    if row_count == 1:
        tussenmatrix.append(matrix[0])
        for elem in tussenmatrix[0]:
            uitmatrix.append(type_caster(elem))
    else:
        for r in range(0, row_count - aantal_lege_regels):
            tussenmatrix.append(matrix[r])
            uitmatrix.append([])
            for elem in tussenmatrix[r]:
                uitmatrix[r].append(type_caster(elem))
    return uitmatrix


def csvintlezen(filenaam, aantal_lege_regels=0):
    return csvlezen(filenaam, aantal_lege_regels, type_caster=int)


def csvfloatlezen(filenaam, aantal_lege_regels=0):
    return csvlezen(filenaam, aantal_lege_regels, type_caster=float)


def csvwegschrijven(matrix, filenaam, header=None):
    if not isinstance(filenaam, pathlib.Path):
        filenaam = pathlib.Path(filenaam)

    is_matrix_like = any(isinstance(row, list) for row in matrix)

    with open(filenaam.with_suffix('.csv'), 'w', newline='') as f:
        writer = csv.writer(f)

        if header:
            writer.writerow(header)

        if is_matrix_like:
            writer.writerows(matrix)
        else:
            writer.writerow(matrix)


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
