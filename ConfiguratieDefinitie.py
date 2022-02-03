
from config import validate, build

def StandaardConfiguratieDefinitie():
  """
  Dit is de standaard configuratie definitie zoals gebruikt door IKOB
  De definitie bevat (mogelijk) de volgende velden:
  - Overal:
    - label: De tekst voor een label voor invoer veld, tab, of frame.
  - Alleen in 'bladen' (het diepste niveau) van de definitie:
    - type (verplicht): soort invoer: text, number, directory, file, checkbox, checklist, choice.
      (file en directory krijgen een 'browse' knop achter het veld)
    - unit: label achter het invoerveld: (alleen text en number)
    - default: De standaard invoerwaarde
    - items: De lijst van dingen waaruit je kan kiezen (alleen voor type 'checklist' en 'choice')
    - range: De minimum en maximum toegestane waarde (alleen voor type 'number')
  """
  return {
    'project': {
      'label': 'Project',
      'naam': {
        'label': 'Project naam',
        'type': 'text',
        'default': 'Project 1'
      },
      'paden': {
        'label': 'Paden',
        'invoer_skims_directory': {
          'label': 'Skims directory',
          'type': 'directory',
          'default': 'skims'
        },
        'uitvoer_directory': {
          'label': 'Uitvoer directory',
          'type': 'directory',
          'default': 'uitvoer'
        },
      },
      'motieven': {
        'label': 'Motieven',
        'type': 'checklist',
        'items': [ 'werk', 'winkeldagelijkszorg', 'winkelnietdagelijksonderwijs' ],
        'default': [ 'werk' ]
      }
    },
    'skims': {
      'label': 'Skims Berekenen',
      'OV kosten': {
        'Benaderen': {
          'label': 'Benader OV kosten',
          'type': 'checkbox',
          'default': True
        },
        'Uit bestand': {
          'label': 'OV kosten bestand',
          'type': 'file',
          'default': ''
        }
      },
      'dagsoort': {
        'label': 'Dagsoorten',
        'type': 'checklist',
        'items': [ 'Ochtendspits', 'Restdag', 'Avondspits' ],
        'default': [ 'Restdag' ]
      },
      'inkomen': {
        'label': 'Inkomensgroepen',
        'type': 'checklist',
        'items': ['laag', 'middellaag', 'middelhoog', 'hoog'],
        'default': ['laag', 'middellaag', 'middelhoog', 'hoog']
      },
      'aspect': {
        'label': 'Aspecten',
        'type': 'checklist',
        'items': [ 'Tijd', 'Kosten' ],
        'default': [ 'Tijd', 'Kosten' ]
      },
      'TVOMwerk': {
        'label': 'TVoM Werk',
        'hoog': {
          'label': 'Hoog',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 4
        },
        'middelhoog': {
          'label': 'Middelhoog',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 6
        },
        'middellaag': {
          'label': 'Middellaag',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 9
        },
        'laag': {
          'label': 'Laag',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 12
        }
      },
      'TVOMoverig': {
        'label': 'TVoM Overig',
        'hoog': {
          'label': 'Hoog',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 4.8
        },
        'middelhoog': {
          'label': 'Middelhoog',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 7.25
        },
        'middellaag': {
          'label': 'Middellaag',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 10.9
        },
        'laag': {
          'label': 'Laag',
          'type':'number',
          'unit': 'Minuten/Euro',
          'default': 15.5
        }
      },
      'varkosten': {
        'label': 'Variabele kosten auto',
        'type': 'number',
        'unit': 'Euro/km',
        'range': [ 0, 9999 ],
        'default': 0.16,
      },
      'kmheffing': {
        'label': 'Kilometer heffing',
        'type': 'number',
        'unit': 'Euro/km',
        'range': [ 0, 9999 ],
        'default': 0
      },
      'soortgeenauto': {
        'label': 'Soort geen auto',
        'type': 'checklist',
        'items': ['GeenAuto', 'GeenRijbewijs'],
        'default': ['GeenAuto', 'GeenRijbewijs']
      },
      'varkostenga': {
        'label': 'Variabele kosten geen auto',
        'GeenAuto': {
          'label': 'Bezit geen auto',
          'type': 'number',
          'unit': 'Euro/km',
          'range': [ 0, 9999 ],
          'default': 0.33
        },
        'GeenRijbewijs': {
          'label': 'Bezit geen rijbewijs',
          'type': 'number',
          'unit': 'Euro/km',
          'range': [ 0, 9999 ],
          'default': 2.40
        }
      },
      'tijdkostenga': {
        'label': 'Tijd kosten geen auto',
        'GeenAuto': {
          'label': 'Bezit geen auto',
          'type': 'number',
          'unit': 'Euro/Minuut',
          'range': [ 0, 9999 ],
          'default': 0.01
        },
        'GeenRijbewijs': {
          'label': 'Bezit geen rijbewijs',
          'type': 'number',
          'unit': 'Euro/Minuut',
          'range': [ 0, 9999 ],
          'default': 0.40
        }
      }
    },
    'verdeling': {
      'label': 'Verdeling Over Groepen',
      'inkomens': {
        'label': 'Inkomensgroepen',
        'type': 'checklist',
        'items': ['laag', 'middellaag', 'middelhoog', 'hoog'],
        'default': ['laag', 'middellaag', 'middelhoog', 'hoog']
      },
#      'Gratisautonaarinkomens': {
#        [0, 0.02, 0.175, 0.275]
#      },
      'Gratisautopercentage': {
        'label': 'Gratis Auto',
        'laag': {
          'label': 'Laag',
          'type': 'number',
          'unit': '%',
          'range': [ 0, 100 ],
          'default': 0
        },
        'middellaag': {
          'label': 'Middellaag',
          'type': 'number',
          'unit': '%',
          'range': [ 0, 100 ],
          'default': 0.1
        },
        'middelhoog': {
          'label': 'Middelhoog',
          'type': 'number',
          'unit': '%',
          'range': [ 0, 100 ],
          'default': 0.35
        },
        'hoog': {
          'label': 'Hoog',
          'type': 'number',
          'unit': '%',
          'range': [ 0, 100 ],
          'default': 0.55
        }
      },
      'GratisOVpercentage': {
        'label': 'Gratis OV',
        'type': 'number',
        'unit': 'fractie',
        'range': [0, 100],
        'default': 0.03
      }
    }
  }

def projectNaam(config):
  """
  Geeft de inhoud van het veld terug waarin de projeect naam is opgeslagen.
  """
  return config['project']['naam']

def valideerConfiguratie(config, strict = True):
  """
  Valideer een configuratie dictionary.
  """
  return validate.validateConfigWithTemplate(config, StandaardConfiguratieDefinitie(), strict = strict)

def StandaardConfiguratie():
  """
  Geeft de standaard configuratie terug zoals gedefinieerd in het bovenstaande sjabloon.
  """
  template = StandaardConfiguratieDefinitie()
  config = build.buildConfigDict(template)
  return config
