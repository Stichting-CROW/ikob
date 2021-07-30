def alomwerk (mod, voorkeur):
    alpha = 0.125
    omega = 45
    weging = 1
    if mod == 'Fiets':
        alpha = 0.225
        omega = 25
    elif mod == 'Efiets':
        alpha = 0.175
        omega = 35
    if voorkeur == 'Auto':
        if mod == 'OV':
            omega = 30
            weging = 0.95
    elif voorkeur == 'OV':
        alpha = 0.12
        omega = 60
        if mod == 'Auto':
            weging = 0.75
            alpha = 0.125
            omega = 45
    elif voorkeur == 'Fiets':
        if mod == 'Auto':
            weging = 0.75
        elif mod == 'Fiets':
            alpha = 0.175
            omega = 35
        elif mod == 'Efiets':
            alpha = 0.125
            omega = 55
    return alpha, omega, weging

def alomwinkeldagelijkszorg (mod, voorkeur):
    alpha = 0.225
    omega = 12.5
    weging = 1
    if mod == 'Fiets' or 'EFiets' :
        omega = 10
        if voorkeur == 'Fiets':
            omega = 12.5
    if mod == 'Auto' and voorkeur == 'Fiets':
        weging = 0.75
    if mod == 'OV' and voorkeur == 'OV':
        alpha = 0.175
    return alpha, omega,weging

def alomwinkelnietdagelijksonderwijs (mod, voorkeur):
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
