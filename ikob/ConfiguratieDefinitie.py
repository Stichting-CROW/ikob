from config import validate, build


def StandaardConfiguratieDefinitie():
    """
  Dit is de standaard configuratie definitie zoals gebruikt door IKOB
  De definitie bevat (mogelijk) de volgende velden:
  - Overal:
    - label: De tekst voor een label voor invoer veld, tab, of frame.
  - Alleen in 'bladen' (het diepste niveau) van de definitie:
    - type (verplicht): (soort invoer)
        text,
        number,
        directory,
        file,
        checkbox,
        checklist,
        choice.
      ('file' en 'directory' krijgen een 'browse' knop achter het veld)
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
            # 'scenario': {
            # 'label': 'Welk scenario gaat het om',
            # 'type': 'text',
            # 'default': 'normaal'
            # },
            'scenario': {
                'label': 'Welk verstedelijkingsscenario wordt gebruikt',
                'type': 'text',
                'default': '',
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
                # 'uitvoer_directory': {
                # 'label': 'Uitvoer directory',
                # 'type': 'directory',
                # 'default': 'uitvoer'
                # },
            },
            'motieven': {
                'label': 'Motieven',
                'type': 'checklist',
                'items': ['werk', 'winkeldagelijkszorg', 'winkelnietdagelijksonderwijs'],
                'default': ['werk']
            },
            'ketens': {
                'label': 'Wordt er ook gewerkt met ketenverplaatsingen (hubs?',
                'gebruiken': {
                    'label': 'Wel ketens en hubs',
                        'type': 'checkbox',
                        'default': False
                },
                'naam hub': {
                    'label': 'Wat is de naam van de hub?',
                    'type': 'text',
                    'default': ''
                }
            }
        },
        'skims': {
            'label': 'Ervaren Reistijd Berekenen',
            'dagsoort': {
                'label': 'Dagsoorten',
                'type': 'checklist',
                'items': ['Ochtendspits', 'Restdag', 'Avondspits'],
                'default': ['Restdag']
            },
            'aspect': {
                'label': 'Aspecten',
                'type': 'checklist',
                'items': ['Tijd', 'Kosten'],
                'default': ['Tijd', 'Kosten']
            },
            'OV kosten': {
                'starttarief': {
                    'label': 'Starttarief',
                    'type': 'number',
                    'unit': 'Eurocent',
                    'default': 75
                },
                'kmkosten': {
                    'label': 'Variable kosten',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 12
                }
                # ,
                # 'Uit bestand': {
                #  'label': 'OV kosten bestand',
                #  'type': 'file',
                #  'default': ''
                # }
            },
            'varautotarief': {
                'label': 'Variabele kosten auto',
                'type': 'number',
                'unit': 'Eurocent/km',
                'range': [0, 9999],
                'default': 16,
            },
            'kmheffing': {
                'label': 'Kilometerheffing',
                'type': 'number',
                'unit': 'Euro/km',
                'range': [0, 9999],
                'default': 0
            },
            'parkeerzoektijden_bestand': {
                'label': 'Parkeerzoektijden bestand',
                'type': 'file',
                'default': ''
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
                    'default': 0.01
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
                'label': 'Waarde van 1€ kosten in ervaren reistijd per inkomensgroep, motief werk',
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
                'label': 'Waarde van 1€ kosten in ervaren reistijd per inkomensgroep, motief overig',
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
            'elektrischeautos': {
                'label': 'Percentage elektrische autos',
                'type': 'choice',
                'items': ['0', '20', '40'],
                'unit': '%',
                'default': '0'
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
            # 'Gratisautopercentage': {
            #  'label': 'Gratis Auto',
            #  'laag': {
            #    'label': 'Laag',
            #    'type': 'number',
            #    'unit': '(fractie)',
            #    'range': [ 0, 100 ],
            #    'default': 0
            #  },
            #  'middellaag': {
            #    'label': 'Middellaag',
            #    'type': 'number',
            #    'unit': '(fractie)',
            #    'range': [ 0, 100 ],
            #    'default': 0.1
            #  },
            #  'middelhoog': {
            #    'label': 'Middelhoog',
            #    'type': 'number',
            #    'unit': '(fractie)',
            #    'range': [ 0, 100 ],
            #    'default': 0.35
            #  },
            #  'hoog': {
            #    'label': 'Hoog',
            #    'type': 'number',
            #    'unit': '(fractie)',
            #    'range': [ 0, 100 ],
            #    'default': 0.55
            #  }
            # },
            'GratisOVpercentage': {
                'label': 'Gratis OV',
                'type': 'number',
                'unit': '(fractie)',
                'range': [0, 100],
                'default': 0.03
            },
        },

        # 'ontplooiing': {
        # 'label': 'Ontplooiing',
        # 'verdeling_file': {
        # 'label': 'Verdeling over groepen bestand',
        # 'type': 'file',
        # 'default': ''
        # },
        # 'uitvoerdirectorynaam': {
        # 'label': 'Naam van uitvoerdirectory',
        # 'type': 'text',
        # 'default': 'ontplooiing_echte_inwoners'
        # }
        # },
        # 'bedrijven': {
        # 'label': 'Bedrijven',
        # 'verdeling_file': {
        # 'label': 'Verdeling over groepen bestand',
        # 'type': 'file',
        # 'default': ''
        # },
        # 'arbeid': {
        # 'label': 'Concurrentie om arbeidsplaatsen',
        # 'herkomsten_directory': {
        # 'label': 'Herkomsten directory',
        # 'type': 'directory',
        # 'default': 'herkomsten'
        # }
        # },
        # 'inwoners': {
        # 'label': 'Concurrentie om inwoners',
        # 'bestemmingen_directory': {
        # 'label': 'Bestemmingen directory',
        # 'type': 'directory',
        # 'default': 'bestemmingen'
        # }
        # },
        # 'uitvoer_directory_naam': {
        # 'label': 'Naam van uitvoer directory',
        # 'type': 'text',
        # 'default': 'uitvoer'
        # }
        # }
    }


def projectNaam(config):
    """
  Geeft de inhoud van het veld terug waarin de projeect naam is opgeslagen.
  """
    return config['project']['naam']


def valideerConfiguratie(config, strict=True):
    """
  Valideer een configuratie dictionary.
  """
    return validate.validateConfigWithTemplate ( config, StandaardConfiguratieDefinitie ( ), strict=strict )


def StandaardConfiguratie():
    """
  Geeft de standaard configuratie terug zoals gedefinieerd in het bovenstaande sjabloon.
  """
    template = StandaardConfiguratieDefinitie ( )
    config = build.buildConfigDict ( template )
    return config
