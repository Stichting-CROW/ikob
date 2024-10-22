from ikob.config import build, validate


def default_configuration_definition():
    """
    The default configuration definition for IKOB.

    The configuration contains the label attribute:
      - label: The label text for an input field, tab, or frame.

    For each leaf in the configuration additional attributes are defined:
      - type (required): the kind of input:
          text
          number
          directory
          file
          checkbox
          checklist
          choice
      - unit: a label after the input field for ``text`` and ``number``
      - default: the default input value
      - items: a list of items to choose from
      - range: the minimum and maximum allowed values for type ``number``
    """

    return {
        'project': {
            'label': 'Project',
            'naam': {
                'label': 'Project naam',
                'type': 'text',
                'default': 'Project 1'
            },
            'verstedelijkingsscenario': {
                'label': 'Welk verstedelijkingsscenario wordt gebruikt',
                'type': 'text',
                'default': '',
            },
            'beprijzingsregime': {
                'label': 'Wat is de naam van het beprijzingsregime',
                'type': 'text',
                'default': 'Basis',
            },
            'paden': {
                'label': 'Paden',
                'skims_directory': {
                    'label': 'Basis directory',
                    'type': 'directory',
                    'default': ''
                },
                'segs_directory': {
                    'label': 'SEGS directory',
                    'type': 'directory',
                    'default': 'SEGS'
                },
                'output_directory': {
                    'label': 'Output directory',
                    'type': 'directory',
                    'default': 'output'
                }
            },
            'motieven': {
                'label': 'Motieven',
                'type': 'checklist',
                'items': ['werk', 'winkeldagelijkszorg', 'winkelnietdagelijksonderwijs', 'sociaal-recreatief'],
                'default': ['werk']
            },
            'welke_groepen': {
                'label': 'Welke groepen moeten worden meegenomen qua autobezit',
                'type': 'checklist',
                'items': ['alle groepen', 'alleen autobezitters'],
                'default': ['alle groepen']
            },
            'schatten_of_bekend': {
                'label': 'Is het percentage autobezit bekend of moet het uit CBS-gegevens geschat worden?',
                'type': 'checklist',
                'items': ['bekend', 'geschat'],
                'default': ['geschat']
            },
            'welke_inkomensgroepen': {
                'label': 'Welke inkomensgroepen moeten worden meegenomen',
                'type': 'checklist',
                'items': ['laag', 'middellaag', 'middelhoog', 'hoog'],
                'default': ['laag', 'middellaag', 'middelhoog', 'hoog']
            },
            'conc_afstand': {
                'label': 'Moet in stap 8 alleen concurrentie of ook afstand worden berekend',
                'type': 'checklist',
                'items': ['concurrentie', 'afstand'],
                'default': ['concurrentie']
            },
            'ketens': {
                'label': 'Wordt er ook gewerkt met ketenverplaatsingen (hubs?',
                'gebruiken': {
                    'label': 'Wel ketens en hubs',
                    'type': 'checkbox',
                    'default': False
                },
                'naam hub': {
                    'label': 'Wat is de naam van de verzameling hubs?',
                    'type': 'text',
                    'default': ''
                }
            }
        },
        'skims': {
            'label': 'Gegeneraliseerde Reistijd Berekenen',
            'dagsoort': {
                'label': 'Dagsoorten',
                'type': 'checklist',
                'items': ['Ochtendspits', 'Restdag', 'Avondspits'],
                'default': ['Restdag']
            },

            'OV kosten': {
                'starttarief': {
                    'label': 'Starttarief',
                    'type': 'number',
                    'unit': 'Eurocent',
                    'default': 75
                },
                'kmkosten': {
                    'label': 'Variabele kosten',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 12
                }
            },
            'OV kostenbestand': {
                'label': 'Bestaat er een apart OV-kostenbestand?',
                'gebruiken': {
                    'label': 'Er is een apart OV-kostenbestand',
                    'type': 'checkbox',
                    'default': False
                },
            },
            'pricecap': {
                'label': 'Is er een maximum OV-prijs (price cap)?',
                'gebruiken': {
                    'label': 'pricecap',
                    'type': 'checkbox',
                    'default': False
                },
                'getal': {
                    'label': 'Wat is de pricecap in Euros',
                    'type': 'number',
                    'default': 9999.0
                },
            },

            'Kosten auto fossiele brandstof': {
                'variabele kosten': {
                    'label': 'variabele kosten',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 16
                },
                'kmheffing': {
                    'label': 'Kilometerheffing',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 0
                },
            },
            'Kosten elektrische auto': {
                'variabele kosten': {
                    'label': 'variabele kosten',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 5
                },
                'kmheffing': {
                    'label': 'Kilometerheffing',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 0
                }
            },
            'parkeerzoektijden_bestand': {
                'label': 'Parkeerzoektijden bestand',
                'type': 'file',
                'default': ''
            },
            'varkostenga': {
                'label': 'Variabele kosten geen auto',
                'GeenAuto': {
                    'label': 'Deelauto (bezit geen auto, wel rijbewijs)',
                    'type': 'number',
                    'unit': 'Euro/km',
                    'range': [0, 9999],
                    'default': 0.33
                },
                'GeenRijbewijs': {
                    'label': 'Taxi (bezit geen rijbewijs)',
                    'type': 'number',
                    'unit': 'Euro/km',
                    'range': [0, 9999],
                    'default': 2.40
                }
            },
            'tijdkostenga': {
                'label': 'Tijd kosten geen auto',
                'GeenAuto': {
                    'label': 'Deelauto (bezit geen auto, wel rijbewijs)',
                    'type': 'number',
                    'unit': 'Euro/Minuut',
                    'range': [0, 9999],
                    'default': 0.05
                },
                'GeenRijbewijs': {
                    'label': 'Taxi (bezit geen rijbewijs)',
                    'type': 'number',
                    'unit': 'Euro/Minuut',
                    'range': [0, 9999],
                    'default': 0.40
                }
            }
        },
        'TVOM': {
            'label': 'Waarde van tijd',

            'werk': {
                'label': 'Waarde van 1€ kosten in gegeneraliseerde reistijd per inkomensgroep, motief werk',
                'hoog': {
                    'label': 'Hoog',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 4
                },
                'middelhoog': {
                    'label': 'Middelhoog',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 6
                },
                'middellaag': {
                    'label': 'Middellaag',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 9
                },
                'laag': {
                    'label': 'Laag',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 12
                }
            },
            'overig': {
                'label': 'Waarde van 1€ kosten in gegeneraliseerde reistijd per inkomensgroep, motief overig',
                'hoog': {
                    'label': 'Hoog',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 4.8
                },
                'middelhoog': {
                    'label': 'Middelhoog',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 7.25
                },
                'middellaag': {
                    'label': 'Middellaag',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 10.9
                },
                'laag': {
                    'label': 'Laag',
                    'type': 'number',
                    'unit': 'Minuten/Euro',
                    'default': 15.5
                }
            },
        },
        'verdeling': {
            'label': 'Verdeling Over Groepen',
            'Percelektrisch': {
                'label': 'Percentage elektrische autos per inkomensgroep',
                'laag': {
                    'label': 'Laag',
                    'type': 'number',
                    'unit': '%',
                    'default': 0
                },
                'middellaag': {
                    'label': 'Middellaag',
                    'type': 'number',
                    'unit': '%',
                    'default': 0
                },
                'middelhoog': {
                    'label': 'Middelhoog',
                    'type': 'number',
                    'unit': '%',
                    'default': 0
                },
                'hoog': {
                    'label': 'hoog',
                    'type': 'number',
                    'unit': '%',
                    'default': 0
                }
            },

            'kunstmab': {
                'label': 'Kunstmatig autobezit (afgedwongen lager autobezit bv door strenge parkeernormen)',
                'gebruiken': {
                    'label': 'Gebruik kunstmatig autobezit',
                    'type': 'checkbox',
                    'default': False
                },
                'bestand': {
                    'label': 'Kunstmatig autobezit bestand',
                    'type': 'file',
                    'default': ''
                },
            },
            'GratisOVpercentage': {
                'label': 'Gratis OV',
                'type': 'number',
                'unit': '(fractie)',
                'range': [0, 100],
                'default': 0.03
            },
            'parkeerkosten': {
                'label': 'Is er een bestand met parkeerkosten per zone?',
                'gebruiken': {
                    'label': 'Parkeerkosten',
                    'type': 'checkbox',
                    'default': False
                },
                'bestand': {
                    'label': 'Parkeerkosten bestand (bedragen zijn in eurocenten (dus €2,20 wordt weergegeven als 220)',
                    'type': 'file',
                    'default': ''
                },
            },
            'additionele_kosten': {
                'label': 'Is er een bestand met additionele kosten (bedragen zijn in euros?',
                'gebruiken': {
                    'label': 'Additionele kosten',
                    'type': 'checkbox',
                    'default': False
                },
                'bestand': {
                    'label': 'Additionele kosten bestand',
                    'type': 'file',
                    'default': ''
                },
            },
        },
    }


def project_name(config):
    """Extract the project name from the project configuration."""
    return config['project']['naam']


def validate_config(config, strict=True):
    """Validate a config dictionary."""
    return validate.validateConfigWithTemplate(
        config, default_configuration_definition(), strict=strict)


def default_config():
    """Provide the configuration using the default config definition."""
    template = default_configuration_definition()
    config = build.buildConfigDict(template)
    return config
