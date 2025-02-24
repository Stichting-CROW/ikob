import json
import pathlib

from ikob.configuration_definition import (try_fix_incompatible_configuration,
                                           validate_config)
from ikob.ikobconfig import loadConfig

old_config = """
{
  "TVOM": {
    "werk": {
      "middellaag": 9.0,
      "laag": 12.0,
      "hoog": 4.0,
      "middelhoog": 6.0
    },
    "overig": {
      "middellaag": 10.9,
      "laag": 15.5,
      "hoog": 4.8,
      "middelhoog": 7.25
    }
  },
  "project": {
    "naam": "Vlaanderen",
    "beprijzingsregime": "Basis",
    "paden": {
      "segs_directory": "tests/vlaanderen/SEGS",
      "skims_directory": "tests/vlaanderen/skims",
      "output_directory": "tests/vlaanderen/"
    },
    "verstedelijkingsscenario": "2023",
    "welke_groepen": [
      "alle groepen"
    ],
    "motieven": [
      "werk"
    ],
    "ketens": {
      "gebruiken": false,
      "naam hub": ""
    },
    "welke_inkomensgroepen": [
      "laag",
      "middellaag",
      "middelhoog",
      "hoog"
    ]
  },
  "verdeling": {
    "GratisOVpercentage": 0.03,
    "kunstmab": {
      "gebruiken": false,
      "bestand": ""
    },
    "parkeerkosten": {
      "gebruiken": false,
      "bestand": ""
    },
    "Percelektrisch": {
      "middellaag": 0.0,
      "laag": 0.0,
      "hoog": 0.0,
      "middelhoog": 0.0
    },
    "additionele_kosten": {
      "gebruiken": false,
      "bestand": ""
    }
  },
  "skims": {
    "Kosten auto fossiele brandstof": {
      "variabele kosten": 16.0,
      "kmheffing": 0.0
    },
    "Kosten elektrische auto": {
      "variabele kosten": 5.0,
      "kmheffing": 0.0
    },
    "varkostenga": {
      "GeenAuto": 0.33,
      "GeenRijbewijs": 2.4
    },
    "pricecap": {
      "gebruiken": false,
      "getal": 9999.0
    },
    "OV kostenbestand": {
      "gebruiken": false
    },
    "parkeerzoektijden_bestand": "tests/vlaanderen/SEGS/Parkeerzoektijd.csv",
    "OV kosten": {
      "kmkosten": 12.0,
      "starttarief": 75.0
    },
    "dagsoort": [
      "Restdag"
    ],
    "tijdkostenga": {
      "GeenAuto": 0.05,
      "GeenRijbewijs": 0.4
    }
  }
}"""


def test_auto_fix_config():
    config = json.loads(old_config)

    msg = "The old configuration should initially be reported as invalid."
    assert not validate_config(config), msg

    config = try_fix_incompatible_configuration(config)

    msg = "The configuration should be OK after attempted fix."
    assert validate_config(config), msg


def test_load_fixable_config(tmpdir):
    tmpdir = pathlib.Path(tmpdir)
    config_file = (tmpdir / "test.json")
    config_file.write_text(old_config)
    loadConfig(config_file)
