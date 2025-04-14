### Validate the template


def _validateDefaultType(valtype, defvalue):
    defvaluetype = type(defvalue)
    if defvaluetype is dict:
        return False
    if (
        valtype == "text" or valtype == "file" or valtype == "directory" or valtype == "choice"
    ) and defvaluetype is not str:
        return False
    if valtype == "number" and not (defvaluetype is float or defvaluetype is int):
        return False
    if (valtype == "checklist") and defvaluetype is not list:
        return False
    if (valtype == "checkbox") and defvaluetype is not bool:
        return False
    return True


def validateTemplate(template):
    for key in set(template.keys()):
        t = template[key]
        if key == "label":
            continue
        if type(t) is not dict:
            print("Het 'type' veld mist.")
            return False
        if "type" in t:
            valtype = t["type"]
            if valtype == "checklist" or valtype == "choice":
                if "items" not in t:
                    print(f"Items is verplicht voor type '{valtype}' in '{key}'.")
                    return False
                if len(t["items"]) < 1:
                    print(f"Geen opties in 'items' voor type '{valtype}' in '{key}'.")
                    return False
            if "range" in t:
                valrange = t["range"]
                if valtype != "number":
                    print(f"De 'range' optie wordt niet ondersteund voor type '{valtype}'.")
                    return False
                if type(valrange) is not list:
                    print(f"De 'range' moet worden opgegeven als een lijst in '{key}'.")
                    return False
                if len(valrange) != 2:
                    print(f"De 'range' moet precies twee waarden bevatten in '{key}'.")
                    return False
            if "default" in t:
                defvalue = t["default"]
                if not _validateDefaultType(type, defvalue):
                    print(f"Default waarde '{defvalue}' voor '{key}' past niet bij type '{valtype}'.")
                    return False
        else:
            return validateTemplate(template[key])
    return True


### Validate config


def _false(value, template):
    return False


def _validateText(value, template):
    if type(value) is not str:
        return False
    return True


def _validateNumber(value, template):
    if not (type(value) is float or type(value) is int):
        return False
    if "range" in template:
        if value < template.range[0] or value > template.range[1]:
            return False
    return True


def _validateItems(values, template):
    if type(values) is not list:
        return False
    for item in values:
        if item not in template.items:
            return False
    return True


def _validateChoice(value, template):
    if value not in template.items:
        return False
    return True


def validateConfigWithTemplate(config, template, strict=False):
    """
    Valideert een configuratie gegeven een template.
    Er wordt gekeken naar structuur en waarden van de bladen.
    Indien strict op False staat, dan is het toegestaan om in de config
    extra velden te hebben die niet in het template staan. In dat geval
    garandeert de validatie alleen dus de standaard velden. De overige
    waarden worden klakkeloos overgenomen.
    Resultaat: True - Configuratie klopt.
               False - Configuratie klopt niet.
    """
    templatekeys = [key for key in template.keys() if key != "label"]
    if strict and set(config.keys()) != set(templatekeys):
        return False
    for key in templatekeys:
        if not strict:
            if key not in config:
                return False
        if "type" in template[key]:
            check = {
                "text": _validateText,
                "number": _validateNumber,
                "directory": _validateText,
                "file": _validateText,
                "checkbox": _validateItems,
                "checklist": _validateItems,
                "choice": _validateChoice,
            }
            check.get(template[key]["type"], _false)(config[key], template[key])
        elif type(template[key]) is dict:
            return validateConfigWithTemplate(config[key], template[key], strict=strict)
    return True
