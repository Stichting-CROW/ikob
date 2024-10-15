def alomwerk(mod, voorkeur, motief):
    motieven = ["werk", "sociaal-recreatief", "winkeldagelijks", "onderwijs"]
    assert motief in motieven, f"Unknown motief: '{motief}'"

    if motief == "werk" or motief == "sociaal-recreatief":
        return _alomwerk(mod, voorkeur)
    elif motief == "winkeldagelijks" or motief == "onderwijs":
        return _alomwinkeldagelijkszorg(mod, voorkeur)
    else:
        return _alomwinkelnietdagelijksonderwijs(mod, voorkeur)


def _alomwerk(mod, voorkeur):
    alpha = 0.125
    omega = 45
    weging = 1
    if mod == 'Fiets':
        alpha = 0.225
        omega = 25
    elif mod == 'EFiets':
        alpha = 0.175
        omega = 35
    if voorkeur == 'Auto':
        if mod == 'Auto':
            omega = 50
        elif mod == 'OV':
            omega = 30
            weging = 0.95
    elif voorkeur == 'OV':
        if mod == 'Auto':
            weging = 0.96
            alpha = 0.125
            omega = 45
        elif mod == 'OV':
            alpha = 0.12
            omega = 60
    elif voorkeur == 'Fiets':
        if mod == 'Auto':
            weging = 0.75
        elif mod == 'Fiets':
            alpha = 0.175
            omega = 35
        elif mod == 'EFiets':
            alpha = 0.125
            omega = 55
    return alpha, omega, weging


def _alomwinkeldagelijkszorg(mod, voorkeur):
    alpha = 0.225
    omega = 12.5
    weging = 1
    if mod == 'Fiets' or 'EFiets':
        omega = 10
        if voorkeur == 'Fiets':
            omega = 12.5
    if mod == 'Auto' and voorkeur == 'Fiets':
        weging = 0.75
    if mod == 'OV' and voorkeur == 'OV':
        alpha = 0.175

    return alpha, omega, weging


def _alomwinkelnietdagelijksonderwijs(mod, voorkeur):
    alpha = 0.225
    omega = 20
    weging = 1
    if mod == 'Fiets' or 'EFiets':
        omega = 15
        if voorkeur == 'Fiets':
            omega = 20
    if mod == 'Auto' and voorkeur == 'Fiets':
        weging = 0.75
    if mod == 'OV' and voorkeur == 'OV':
        alpha = 0.175

    return alpha, omega, weging
