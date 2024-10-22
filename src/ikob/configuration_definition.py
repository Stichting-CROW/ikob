from ikob.config import build, validate


def config_item(label: str,
                data_type: str,
                default: str = '',
                items: list[str] = [],
                bounds: list[str] = [],
                unit: str = ''):
    allowed_data_types = ["text",
                          "number",
                          "directory",
                          "file",
                          "checkbox",
                          "checklist",
                          "choice"]
    assert data_type in allowed_data_types

    if data_type == "checkbox":
        default = False if not default else default
    elif data_type == "number":
        default = 0 if not default else default

    # The default value is expected as list when more items are present.
    if items and isinstance(default, str):
        default = [default]

    dictionary = {
        'label': label,
        'type': data_type,
        'default': default
    }

    # Insert all optional values when present.
    keys = ['items', 'unit', 'bounds']
    optionals = [items, unit, bounds]
    for key, optional in zip(keys, optionals):
        if optional:
            dictionary[key] = optional

    return dictionary


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

    project_tab = {
        'label': 'Project',
        'naam': config_item(
            'Project naam',
            'text',
            default='Project 1'
        ),
        'verstedelijkingsscenario': config_item(
            'Welk verstedelijkingsscenario wordt gebruikt',
            'text',
        ),
        'beprijzingsregime': config_item(
             'Wat is de naam van het beprijzingsregime',
             'text',
             default='Basis',
        ),
        'paden': {
            'label': 'Paden',
            'skims_directory': config_item(
                'Basis directory',
                'directory',
            ),
            'segs_directory': config_item(
                'SEGS directory',
                'directory',
                default='SEGS'
            ),
            'output_directory': config_item(
                'Output directory',
                'directory',
                default='output'
            )
        },
        'motieven': config_item(
            'Motieven', 'checklist', default='werk',
            items=['werk', 'winkeldagelijkszorg',
                   'winkelnietdagelijksonderwijs', 'sociaal-recreatief']
        ),
        'welke_groepen': config_item(
            'Welke groepen moeten worden meegenomen qua autobezit',
            'checklist',
            default='alle groepen',
            items=['alle groepen', 'alleen autobezitters'],
        ),
        'schatten_of_bekend': config_item(
            'Is het percentage autobezit bekend of moet het uit CBS-gegevens geschat worden?',
            'checklist',
            default='geschat',
            items=['bekend', 'geschat'],
        ),
        'welke_inkomensgroepen': config_item(
            'Welke inkomensgroepen moeten worden meegenomen',
            'checklist',
            default=['laag', 'middellaag', 'middelhoog', 'hoog'],
            items=['laag', 'middellaag', 'middelhoog', 'hoog'],
        ),
        'conc_afstand': config_item(
            'Moet in stap 8 alleen concurrentie of ook afstand worden berekend',
            'checklist',
            default='concurrentie',
            items=['concurrentie', 'afstand'],
        ),
        'ketens': {
            'label': 'Wordt er ook gewerkt met ketenverplaatsingen (hubs?',
            'gebruiken': config_item(
                'Wel ketens en hubs',
                'checkbox',
            ),
            'naam hub': config_item(
                'Wat is de naam van de verzameling hubs?',
                'text',
            )
        }
    }

    skims_tab = {
        'label': 'Gegeneraliseerde Reistijd Berekenen',
        'dagsoort': config_item(
            'Dagsoorten',
            'checklist',
            default='Restdag',
            items=['Ochtendspits', 'Restdag', 'Avondspits'],
        ),

        'OV kosten': {
            'starttarief': config_item(
                'Starttarief',
                'number',
                default=75,
                unit='Eurocent',
            ),
            'kmkosten': config_item(
                'Variabele kosten',
                'number',
                default=12,
                unit='Eurocent/km',
            )
        },
        'OV kostenbestand': {
            'label': 'Bestaat er een apart OV-kostenbestand?',
            'gebruiken': config_item(
                'Er is een apart OV-kostenbestand',
                'checkbox',
            ),
        },
        'pricecap': {
            'label': 'Is er een maximum OV-prijs (price cap)?',
            'gebruiken': config_item(
                 'pricecap',
                 'checkbox',
            ),
            'getal': config_item(
                'Wat is de pricecap in Euros',
                'number',
                default=9999.0
            ),
        },

        'Kosten auto fossiele brandstof': {
            'variabele kosten': config_item(
                'variabele kosten',
                'number',
                default=16,
                unit='Eurocent/km',
            ),
            'kmheffing': config_item(
                'Kilometerheffing',
                'number',
                unit='Eurocent/km',
            ),
        },
        'Kosten elektrische auto': {
            'variabele kosten': config_item(
                'variabele kosten',
                'number',
                default=5,
                unit='Eurocent/km'
            ),
            'kmheffing': config_item(
                'Kilometerheffing',
                'number',
                unit='Eurocent/km',
            )
        },
        'parkeerzoektijden_bestand': config_item(
            'Parkeerzoektijden bestand',
            'file',
        ),
        'varkostenga': {
            'label': 'Variabele kosten geen auto',
            'GeenAuto': config_item(
                'Deelauto (bezit geen auto, wel rijbewijs)',
                'number',
                default=0.33,
                bounds=[0, 9999],
                unit='Euro/km',
            ),
            'GeenRijbewijs': config_item(
                'Taxi (bezit geen rijbewijs)',
                'number',
                default=2.40,
                bounds=[0, 9999],
                unit='Euro/km',
            )
        },
        'tijdkostenga': {
            'label': 'Tijd kosten geen auto',
            'GeenAuto': config_item(
                'Deelauto (bezit geen auto, wel rijbewijs)',
                'number',
                default=0.05,
                bounds=[0, 9999],
                unit='Euro/Minuut',
            ),
            'GeenRijbewijs': config_item(
                'Taxi (bezit geen rijbewijs)',
                'number',
                default=0.40,
                bounds=[0, 9999],
                unit='Euro/Minuut',
            )
        }
    }

    tovm_tab = {
        'label': 'Waarde van tijd',

        'werk': {
            'label': 'Waarde van 1€ kosten in gegeneraliseerde reistijd per inkomensgroep, motief werk',
            'hoog': config_item(
                'Hoog',
                'number',
                default=4,
                unit='Minuten/Euro',
            ),
            'middelhoog': config_item(
                'Middelhoog',
                'number',
                default=6,
                unit='Minuten/Euro',
            ),
            'middellaag': config_item(
                'Middellaag',
                'number',
                default=9,
                unit='Minuten/Euro',
            ),
            'laag': config_item(
                'Laag',
                'number',
                default=12,
                unit='Minuten/Euro',
            )
        },
        'overig': {
            'label': 'Waarde van 1€ kosten in gegeneraliseerde reistijd per inkomensgroep, motief overig',
            'hoog': config_item(
                'Hoog',
                'number',
                default=4.8,
                unit='Minuten/Euro',
            ),
            'middelhoog': config_item(
                'Middelhoog',
                'number',
                default=7.25,
                unit='Minuten/Euro',
            ),
            'middellaag': config_item(
                'Middellaag',
                'number',
                default=10.9,
                unit='Minuten/Euro',
            ),
            'laag': config_item(
                'Laag',
                'number',
                default=15.5,
                unit='Minuten/Euro',
            )
        },
    }

    verdeling_tab = {
        'label': 'Verdeling Over Groepen',
        'Percelektrisch': {
            'label': 'Percentage elektrische autos per inkomensgroep',
            'laag': config_item(
                'Laag',
                'number',
                unit='%',
            ),
            'middellaag': config_item(
                'Middellaag',
                'number',
                unit='%',
            ),
            'middelhoog': config_item(
                'Middelhoog',
                'number',
                unit='%',
            ),
            'hoog': config_item(
                'hoog',
                'number',
                unit='%',
            )
        },

        'kunstmab': {
            'label': 'Kunstmatig autobezit (afgedwongen lager autobezit bv door strenge parkeernormen)',
            'gebruiken': config_item(
                'Gebruik kunstmatig autobezit',
                'checkbox',
            ),
            'bestand': config_item(
                'Kunstmatig autobezit bestand',
                'file',
            ),
        },
        'GratisOVpercentage': config_item(
            'Gratis OV',
            'number',
            default=0.03,
            bounds=[0, 100],
            unit='(fractie)',
        ),
        'parkeerkosten': {
            'label': 'Is er een bestand met parkeerkosten per zone?',
            'gebruiken': config_item(
                'Parkeerkosten',
                'checkbox',
            ),
            'bestand': config_item(
                'Parkeerkosten bestand (bedragen zijn in eurocenten (dus €2,20 wordt weergegeven als 220)',
                'file',
            ),
        },
        'additionele_kosten': {
            'label': 'Is er een bestand met additionele kosten (bedragen zijn in euros?',
            'gebruiken': config_item(
                'Additionele kosten',
                'checkbox',
            ),
            'bestand': config_item(
                'Additionele kosten bestand',
                'file',
            ),
        },
    }

    return {
        'project': project_tab,
        'skims': skims_tab,
        'TVOM': tovm_tab,
        'verdeling': verdeling_tab,
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
