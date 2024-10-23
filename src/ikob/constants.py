def work_constants(modality, preference, motive):
    motives = ["werk", "sociaal-recreatief", "winkeldagelijks", "onderwijs"]
    assert motive in motives, f"Unknown motive: '{motive}'"

    if motive == "werk" or motive == "sociaal-recreatief":
        return _work_constants(modality, preference)
    elif motive == "winkeldagelijks" or motive == "onderwijs":
        return _daily_shopping_constants(modality, preference)
    else:
        return _non_daily_shopping_constants(modality, preference)


def _work_constants(modality, preference):
    alpha = 0.125
    omega = 45
    scaling = 1
    if modality == 'Fiets':
        alpha = 0.225
        omega = 25
    elif modality == 'EFiets':
        alpha = 0.175
        omega = 35
    if preference == 'Auto':
        if modality == 'Auto':
            omega = 50
        elif modality == 'OV':
            omega = 30
            scaling = 0.95
    elif preference == 'OV':
        if modality == 'Auto':
            scaling = 0.96
            alpha = 0.125
            omega = 45
        elif modality == 'OV':
            alpha = 0.12
            omega = 60
    elif preference == 'Fiets':
        if modality == 'Auto':
            scaling = 0.75
        elif modality == 'Fiets':
            alpha = 0.175
            omega = 35
        elif modality == 'EFiets':
            alpha = 0.125
            omega = 55
    return alpha, omega, scaling


def _daily_shopping_constants(modality, preference):
    alpha = 0.225
    omega = 12.5
    scaling = 1
    if modality == 'Fiets' or 'EFiets':
        omega = 10
        if preference == 'Fiets':
            omega = 12.5
    if modality == 'Auto' and preference == 'Fiets':
        scaling = 0.75
    if modality == 'OV' and preference == 'OV':
        alpha = 0.175

    return alpha, omega, scaling


def _non_daily_shopping_constants(modality, preference):
    alpha = 0.225
    omega = 20
    scaling = 1
    if modality == 'Fiets' or 'EFiets':
        omega = 15
        if preference == 'Fiets':
            omega = 20
    if modality == 'Auto' and preference == 'Fiets':
        scaling = 0.75
    if modality == 'OV' and preference == 'OV':
        alpha = 0.175

    return alpha, omega, scaling
