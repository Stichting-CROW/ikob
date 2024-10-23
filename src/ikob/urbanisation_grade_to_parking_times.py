def urbanisation_grade_to_parking_times(urbanisation_grades: [int]) -> [[int]]:
    # TODO: This conversion is missing documentation. Why these values?
    urbanisation_to_parking = {1: 12, 2: 8, 3: 4, 4: 0, 5: 0}

    parking_times = []
    for i, urbanisation_grade in enumerate(urbanisation_grades):
        arrival = urbanisation_to_parking[urbanisation_grade]
        departure = urbanisation_to_parking[urbanisation_grade] / 4
        parking_times.append([i + 1, arrival, departure])

    return parking_times
