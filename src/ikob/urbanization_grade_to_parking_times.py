from typing import Iterable


def urbanization_grade_to_parking_times(urbanization_grades: Iterable[int]) -> list[list[int]]:
    # TODO: This conversion is missing documentation. Why these values?
    urbanization_to_parking = {1: 12, 2: 8, 3: 4, 4: 0, 5: 0}

    parking_times = []
    for i, urbanization_grade in enumerate(urbanization_grades):
        arrival = urbanization_to_parking[urbanization_grade]
        departure = urbanization_to_parking[urbanization_grade] / 4
        parking_times.append([arrival, departure])

    return parking_times
