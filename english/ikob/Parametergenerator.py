def alomwork (mod, preference):
    alpha = 0.125
    omega = 45
    weging = 1
    if mod == 'Bike':
        alpha = 0.225
        omega = 25
    elif mod == 'EBike':
        alpha = 0.175
        omega = 35
    if preference == 'Car':
        if mod == 'Car' :
            omega = 50
        elif mod == 'Transit':
            omega = 30
            weging = 0.95
    elif preference == 'Transit':
        if mod == 'Car':
            weging = 0.96
            alpha = 0.125
            omega = 45
        elif mod == 'Transit' :
            alpha = 0.12
            omega = 60
    elif preference == 'Bike':
        if mod == 'Car':
            weging = 0.75
        elif mod == 'Bike':
            alpha = 0.175
            omega = 35
        elif mod == 'EBike':
            alpha = 0.125
            omega = 55
    return alpha, omega, weging

def alomdailyshopping_healthcare (mod, preference):
    alpha = 0.225
    omega = 12.5
    weging = 1
    if mod == 'Bike' or 'EBike' :
        omega = 10
        if preference == 'Bike':
            omega = 12.5
    if mod == 'Car' and preference == 'Bike':
        weging = 0.75
    if mod == 'Transit' and preference == 'Transit':
        alpha = 0.175
    return alpha, omega,weging

def alomnondailyshopping_education (mod, preference):
    alpha = 0.225
    omega = 20
    weging = 1
    if mod == 'Bike' or 'EBike':
        omega = 15
        if preference == 'Bike':
            omega = 20
    if mod == 'Car' and preference == 'Bike':
        weging = 0.75
    if mod == 'Transit' and preference == 'Transit':
        alpha = 0.175
    return alpha, omega, weging
