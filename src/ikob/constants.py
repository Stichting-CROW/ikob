from ikob.configuration_definition import DecayCurveName


def work_constants(modality, preference, decay_curve_name: DecayCurveName):
    """Returns the value from Table 9-11 in IKOB-algorithm.pdf"""

    if decay_curve_name == DecayCurveName.WORK_AND_SOCIAL:
        return _work_constants(modality, preference)
    elif decay_curve_name == DecayCurveName.DAILY_SHOPPING_AND_HEALTH:
        return _daily_shopping_constants(modality, preference)
    elif decay_curve_name == DecayCurveName.NON_DAILY_SHOPPING_AND_EDUCATION:
        return _non_daily_shopping_constants(modality, preference)
    else:
        raise ValueError(f"Unknown decay_curve_name: '{decay_curve_name}'")


def _work_constants(modality, preference):
    alpha = 0.125
    omega = 45
    scaling = 1
    if modality == "Fiets":
        alpha = 0.225
        omega = 25
    elif modality == "EFiets":
        alpha = 0.175
        omega = 35
    if preference == "Auto":
        if modality == "Auto":
            omega = 50
        elif modality == "OV":
            omega = 30
            scaling = 0.95
    elif preference == "OV":
        if modality == "Auto":
            scaling = 0.96
            alpha = 0.125
            omega = 45
        elif modality == "OV":
            alpha = 0.12
            omega = 60
    elif preference == "Fiets":
        if modality == "Auto":
            scaling = 0.75
        elif modality == "Fiets":
            alpha = 0.175
            omega = 35
        elif modality == "EFiets":
            alpha = 0.125
            omega = 55
    return alpha, omega, scaling


def _daily_shopping_constants(modality, preference):
    alpha = 0.225
    omega = 12.5
    scaling = 1
    if modality == "Fiets" or "EFiets":
        omega = 10
        if preference == "Fiets":
            omega = 12.5
    if modality == "Auto" and preference == "Fiets":
        scaling = 0.75
    if modality == "OV" and preference == "OV":
        alpha = 0.175

    return alpha, omega, scaling


def _non_daily_shopping_constants(modality, preference):
    alpha = 0.225
    omega = 20
    scaling = 1
    if modality == "Fiets" or "EFiets":
        omega = 15
        if preference == "Fiets":
            omega = 20
    if modality == "Auto" and preference == "Fiets":
        scaling = 0.75
    if modality == "OV" and preference == "OV":
        alpha = 0.175

    return alpha, omega, scaling
