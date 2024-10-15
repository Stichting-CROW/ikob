def stedelijkheid_to_parkeerzoektijd(stedelijkheidsgraad: [int]) -> [[int]]:
    # TODO: This conversion is missing documentation. Why these values?
    omzetting = {1: 12, 2: 8, 3: 4, 4: 0, 5: 0}

    parkeerzoektijden = []
    for i, sg in enumerate(stedelijkheidsgraad):
        aankomst = omzetting[sg]
        vertrek = round(omzetting[sg] / 4)
        parkeerzoektijden.append([i + 1, aankomst, vertrek])

    return parkeerzoektijden
