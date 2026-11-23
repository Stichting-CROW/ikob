from ikob.configuration_definition import DecayCurveName


def work_constants(modality, decay_curve_name: DecayCurveName):
    """Returns the value from Table 9-11 in IKOB-algorithm.pdf"""

    if decay_curve_name == DecayCurveName.WORK_AND_SOCIAL:
        return _work_constants(modality)
    elif decay_curve_name == DecayCurveName.DAILY_SHOPPING_AND_HEALTH:
        return _daily_shopping_constants(modality)
    elif decay_curve_name == DecayCurveName.NON_DAILY_SHOPPING_AND_EDUCATION:
        return _non_daily_shopping_constants(modality)
    else:
        raise ValueError(f"Unknown decay_curve_name: '{decay_curve_name}'")


def _work_constants(modality):
    alpha = 0.125
    omega = 45
    scaling = 1
    if modality == "Fiets":
        alpha = 0.225
        omega = 25

    return alpha, omega, scaling


def _daily_shopping_constants(modality):
    alpha = 0.225
    omega = 12.5
    scaling = 1
    if modality == "Fiets":
        omega = 10

    return alpha, omega, scaling


def _non_daily_shopping_constants(modality):
    alpha = 0.225
    omega = 20
    scaling = 1
    if modality == "Fiets":
        omega = 15

    return alpha, omega, scaling
