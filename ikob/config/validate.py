
### Validate the template

from config.build import buildConfigDict

def _validateDefaultType(valtype, defvalue):
  defvaluetype = type(defvalue)
  if defvaluetype is dict:
    return False
  if (valtype == 'text'
    or valtype == 'file'
    or valtype == 'directory'
    or valtype == 'choice') and defvaluetype is not str:
      return False
  if valtype == 'number' and not (defvaluetype is float or defvaluetype is int):
    return False
  if (valtype == 'checklist') and not defvaluetype is list:
    return False
  if (valtype == 'checkbox') and not defvaluetype is bool:
    return False
  return True

def validateTemplate(template):
  for key in set(template.keys()):
    t = template[key]
    if key == 'label':
      continue
    if not type(t) is dict:
      print(f"Het 'type' veld mist.")
      return False
    if 'type' in t:
      valtype = t['type']
      if (valtype == 'checklist'
        or valtype == 'choice'):
          if not 'items' in t:
            print(f"Items is verplicht voor type '{valtype}' in '{key}'.")
            return False
          if len(t['items']) < 1:
            print(f"Geen opties in 'items' voor type '{valtype}' in '{key}'.")
            return False
      if 'range' in t:
        valrange = t['range']
        if valtype != 'number':
          print(f"De 'range' optie wordt niet ondersteund voor type '{valtype}'.")
          return False
        if not type(valrange) is list:
          print(f"De 'range' moet worden opgegeven als een lijst in '{key}'.")
          return False
        if len(valrange) != 2:
          print(f"De 'range' moet precies twee waarden bevatten in '{key}'.")
          return False
      if 'default' in t:
        defvalue = t['default']
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
  if not type(value) is str:
    return False
  return True


def _validateNumber(value, template):
  if not (type(value) is float or type(value) is int):
    return False
  if 'range' in template:
    if value < template.range[0] or value > template.range[1]:
      return False
  return True


def _validateItems(values, template):
  if not type(values) is list:
    return False
  for item in values:
    if not item in template.items:
      return False
  return True


def _validateChoice(value, template):
  if not value in template.items:
    return False
  return True


def validateConfigWithTemplate(config, template, strict=False, repair=False):
  """
  Valideert een configuratie gegeven een template.
  Er wordt gekeken naar structuur en waarden van de bladen.

  Args:
    strict (bool):
      True = Configuratie moet precies kloppen met het template.
      False = Het toegestaan om in de config extra velden te hebben die niet
              in het template staan. In dat geval garandeert de validatie
              alleen dus de standaard velden. De overige velden en waarden
              worden klakkeloos overgenomen.
    repair (bool): Repareer missende velden met standaard waarden van template.

  Return:
    bool: De configuratie 'klopt' indien True, anders False.
  """
  templatekeys = [ key for key in template.keys() if key != 'label' ]
  if strict and set(config.keys()) != set(templatekeys) and not repair:
    return False
  for key in templatekeys:
    if not strict:
      if not key in config:
        if not repair:
          return False
        config[key] = buildConfigDict(template[key])
    if 'type' in template[key]:
      check = {
        'text': _validateText,
        'number': _validateNumber,
        'directory': _validateText,
        'file': _validateText,
        'checkbox': _validateItems,
        'checklist': _validateItems,
        'choice': _validateChoice
      }
      return check.get(template[key]['type'], _false)(config[key], template[key])
    elif type(template[key]) is dict:
      return validateConfigWithTemplate(config[key], template[key], strict=strict, repair=repair)
  return True
