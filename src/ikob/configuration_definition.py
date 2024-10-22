from enum import Enum
from ikob.config import build, validate


class DataType(Enum):
    CHECKBOX = "checkbox"
    CHECKLIST = "checklist"
    CHOICE = "choice"
    DIRECTORY = "directory"
    FILE = "file"
    NUMBER = "number"
    TEXT = "text"


def config_item(label: str,
                data_type: DataType,
                default: str = '',
                items: list[str] = [],
                bounds: list[str] = [],
                unit: str = ''):

    msg = "Invalid GUI data type provided."
    assert data_type in DataType, msg

    default_values = {
        DataType.CHECKBOX: False,
        DataType.NUMBER: 0
    }

    if not default:
        default = default_values.get(data_type, default)

    # The default value is expected as list when more items are present.
    if items and isinstance(default, str):
        default = [default]

    dictionary = {
        'label': label,
        'type': data_type.value,
        'default': default
    }

    # Insert all optional values when present.
    keys = ['items', 'unit', 'bounds']
    optionals = [items, unit, bounds]
    for key, optional in zip(keys, optionals):
        if optional:
            dictionary[key] = optional

    return dictionary


def default_project_tab():
    return {
        'label': 'Project',
        'naam': config_item(
            'Project naam',
            DataType.TEXT,
            default='Project 1'
        ),
        'verstedelijkingsscenario': config_item(
            'Welk verstedelijkingsscenario wordt gebruikt',
            DataType.TEXT,
        ),
        'beprijzingsregime': config_item(
             'Wat is de naam van het beprijzingsregime',
             DataType.TEXT,
             default='Basis',
        ),
        'paden': {
            'label': 'Paden',
            'skims_directory': config_item(
                'Basis directory',
                DataType.DIRECTORY,
            ),
            'segs_directory': config_item(
                'SEGS directory',
                DataType.DIRECTORY,
                default='SEGS'
            ),
            'output_directory': config_item(
                'Output directory',
                DataType.DIRECTORY,
                default='output'
            )
        },
        'motieven': config_item(
            'Motieven', DataType.CHECKLIST, default='werk',
            items=['werk', 'winkeldagelijkszorg',
                   'winkelnietdagelijksonderwijs', 'sociaal-recreatief']
        ),
        'welke_groepen': config_item(
            'Welke groepen moeten worden meegenomen qua autobezit',
            DataType.CHECKLIST,
            default='alle groepen',
            items=['alle groepen', 'alleen autobezitters'],
        ),
        'schatten_of_bekend': config_item(
            'Is het percentage autobezit bekend of moet het uit CBS-gegevens geschat worden?',
            DataType.CHECKLIST,
            default='geschat',
            items=['bekend', 'geschat'],
        ),
        'welke_inkomensgroepen': config_item(
            'Welke inkomensgroepen moeten worden meegenomen',
            DataType.CHECKLIST,
            default=['laag', 'middellaag', 'middelhoog', 'hoog'],
            items=['laag', 'middellaag', 'middelhoog', 'hoog'],
        ),
        'conc_afstand': config_item(
            'Moet in stap 8 alleen concurrentie of ook afstand worden berekend',
            DataType.CHECKLIST,
            default='concurrentie',
            items=['concurrentie', 'afstand'],
        ),
        'ketens': {
            'label': 'Wordt er ook gewerkt met ketenverplaatsingen (hubs?',
            'gebruiken': config_item(
                'Wel ketens en hubs',
                DataType.CHECKBOX,
            ),
            'naam hub': config_item(
                'Wat is de naam van de verzameling hubs?',
                DataType.TEXT,
            )
        }
    }


def default_skims_tab():
    return {
        'label': 'Gegeneraliseerde Reistijd Berekenen',
        'dagsoort': config_item(
            'Dagsoorten',
            DataType.CHECKLIST,
            default='Restdag',
            items=['Ochtendspits', 'Restdag', 'Avondspits'],
        ),

        'OV kosten': {
            'starttarief': config_item(
                'Starttarief',
                DataType.NUMBER,
                default=75,
                unit='Eurocent',
            ),
            'kmkosten': config_item(
                'Variabele kosten',
                DataType.NUMBER,
                default=12,
                unit='Eurocent/km',
            )
        },
        'OV kostenbestand': {
            'label': 'Bestaat er een apart OV-kostenbestand?',
            'gebruiken': config_item(
                'Er is een apart OV-kostenbestand',
                DataType.CHECKBOX,
            ),
        },
        'pricecap': {
            'label': 'Is er een maximum OV-prijs (price cap)?',
            'gebruiken': config_item(
                 'pricecap',
                 DataType.CHECKBOX,
            ),
            'getal': config_item(
                'Wat is de pricecap in Euros',
                DataType.NUMBER,
                default=9999.0
            ),
        },

        'Kosten auto fossiele brandstof': {
            'variabele kosten': config_item(
                'variabele kosten',
                DataType.NUMBER,
                default=16,
                unit='Eurocent/km',
            ),
            'kmheffing': config_item(
                'Kilometerheffing',
                DataType.NUMBER,
                unit='Eurocent/km',
            ),
        },
        'Kosten elektrische auto': {
            'variabele kosten': config_item(
                'variabele kosten',
                DataType.NUMBER,
                default=5,
                unit='Eurocent/km'
            ),
            'kmheffing': config_item(
                'Kilometerheffing',
                DataType.NUMBER,
                unit='Eurocent/km',
            )
        },
        'parkeerzoektijden_bestand': config_item(
            'Parkeerzoektijden bestand',
            DataType.FILE,
        ),
        'varkostenga': {
            'label': 'Variabele kosten geen auto',
            'GeenAuto': config_item(
                'Deelauto (bezit geen auto, wel rijbewijs)',
                DataType.NUMBER,
                default=0.33,
                bounds=[0, 9999],
                unit='Euro/km',
            ),
            'GeenRijbewijs': config_item(
                'Taxi (bezit geen rijbewijs)',
                DataType.NUMBER,
                default=2.40,
                bounds=[0, 9999],
                unit='Euro/km',
            )
        },
        'tijdkostenga': {
            'label': 'Tijd kosten geen auto',
            'GeenAuto': config_item(
                'Deelauto (bezit geen auto, wel rijbewijs)',
                DataType.NUMBER,
                default=0.05,
                bounds=[0, 9999],
                unit='Euro/Minuut',
            ),
            'GeenRijbewijs': config_item(
                'Taxi (bezit geen rijbewijs)',
                DataType.NUMBER,
                default=0.40,
                bounds=[0, 9999],
                unit='Euro/Minuut',
            )
        }
    }


def default_tovm_tab():
    levels = ["Hoog", "Middelhoog", "Middellaag", "Laag"]
    werk_values = [4, 6, 9, 12]

    werk_levels = {
        level.lower(): config_item(
            level, DataType.NUMBER, default=value, unit="Minuten/Euro"
        )
        for level, value in zip(levels, werk_values)
    }

    overig_values = [4.8, 7.25, 10.9, 15.5]
    overig_levels = {
        level.lower(): config_item(
            level, DataType.NUMBER, default=value, unit="Minuten/Euro"
        )
        for level, value in zip(levels, overig_values)
    }

    return {
        'label': 'Waarde van tijd',
        'werk': {
            'label': 'Waarde van 1€ kosten in gegeneraliseerde reistijd per inkomensgroep, motief werk',
            **werk_levels,
        },
        'overig': {
            'label': 'Waarde van 1€ kosten in gegeneraliseerde reistijd per inkomensgroep, motief overig',
            **overig_levels,
        },
    }


def default_verdeling_tab():
    levels = ["Laag", "Middellaag", "Middelhoog", "Hoog"]

    electric_share = {
        level.lower(): config_item(level, DataType.NUMBER, unit="%") for level in levels
    }

    return {
        'label': 'Verdeling Over Groepen',
        'Percelektrisch': electric_share,

        'kunstmab': {
            'label': 'Kunstmatig autobezit (afgedwongen lager autobezit bv door strenge parkeernormen)',
            'gebruiken': config_item(
                'Gebruik kunstmatig autobezit',
                DataType.CHECKBOX,
            ),
            'bestand': config_item(
                'Kunstmatig autobezit bestand',
                DataType.FILE,
            ),
        },
        'GratisOVpercentage': config_item(
            'Gratis OV',
            DataType.NUMBER,
            default=0.03,
            bounds=[0, 100],
            unit='(fractie)',
        ),
        'parkeerkosten': {
            'label': 'Is er een bestand met parkeerkosten per zone?',
            'gebruiken': config_item(
                'Parkeerkosten',
                DataType.CHECKBOX,
            ),
            'bestand': config_item(
                'Parkeerkosten bestand (bedragen zijn in eurocenten (dus €2,20 wordt weergegeven als 220)',
                DataType.FILE,
            ),
        },
        'additionele_kosten': {
            'label': 'Is er een bestand met additionele kosten (bedragen zijn in euros?',
            'gebruiken': config_item(
                'Additionele kosten',
                DataType.CHECKBOX,
            ),
            'bestand': config_item(
                'Additionele kosten bestand',
                DataType.FILE,
            ),
        },
    }


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

    project_tab = default_project_tab()
    skims_tab = default_skims_tab()
    tovm_tab = default_tovm_tab()
    verdeling_tab = default_verdeling_tab()

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
