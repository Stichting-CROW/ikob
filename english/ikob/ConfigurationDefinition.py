from config import validate, build

def DefaultConfigurationDefinition():
    """
  This is the Default configuration definition as used by IKOB
  This Definition includes the following fields:
  - Everywhere:
    - label
  - Only in 'pages' (the deepest level) of thee Definition:
    - type (compulsary): (kind of input)
        text,
        number,
        directory,
        file,
        checkbox,
        checklist,
        choice.
      ('file' and 'directory' get a 'browse' button after the field)
    - unit: label behind the input field: (only text and number)
    - default: the Default input value
    - items: choice list (only for type 'checklist' and 'choice')
    - range: Minimum and maximum allowed value (only for type 'number')
  """
    return {
        'project': {
            'label': 'Project',
            'name': {
                'label': 'Project name',
                'type': 'text',
                'default': 'Project 1'
            },
            # 'scenario': {
            # 'label': 'What is the name of the urban situation scenario',
            # 'type': 'text',
            # 'default': ''
            # },
            'scenario': {
                'label': 'What is the name of the urban situation scenario',
                'type': 'text',
                'default': '',
            },
            'paths': {
                'label': 'Paths',
                'base_directory': {
                    'label': 'Base directory',
                    'type': 'directory',
                    'default': ''
                },
                'segs_directory': {
                    'label': 'SEGS directory',  #SEGS stands for Sociaal Economische Gegevens, Social Economic Data
                    'type': 'directory',
                    'default': 'SEGS'
                },
                # 'uitvoer_directory': {
                # 'label': 'Uitvoer directory',
                # 'type': 'directory',
                # 'default': 'uitvoer'
                # },
            },
            'motives': {
                'label': 'Motives',
                'type': 'checklist',
                'items': ['work', 'dailyshopping/healthcare', 'non-daily-shopping/education'],
                'default': ['work']
            },
            'chains': {
                'label': 'Are chain-trips at hand(hubs?',
                'use': {
                    'label': 'There are chains and hubs',
                        'type': 'checkbox',
                        'default': False
                },
                'name hub': {
                    'label': 'What is the name of the (set of) hubs?',
                    'type': 'text',
                    'default': ''
                }
            }
        },
        'skims': {
            'label': 'Calculate Generalised (Experienced) Travel Time',
            'part of the day': {
                'label': 'Part of the day',
                'type': 'checklist',
                'items': ['Morning Peak', 'Restday', 'Evening Peak'],
                'default': ['Restday']
            },
 #           'aspect': {
 #               'label': 'Aspect',
 #               'type': 'checklist',
 #               'items': ['Tijd', 'Kosten'],
 #               'default': ['Tijd', 'Kosten']
 #           },
            'Transit costs': {
                'starting fee': {
                    'label': 'Starting Fee',
                    'type': 'number',
                    'unit': 'Eurocent',
                    'default': 108
                },
                'kmcosts': {
                    'label': 'Variable costs',
                    'type': 'number',
                    'unit': 'Eurocent/km',
                    'default': 19
                }
                # ,
                # 'Uit bestand': {
                #  'label': 'OV kosten bestand',
                #  'type': 'file',
                #  'default': ''
                # }
            },
            'variablecarcosts': {
                'label': 'Variable car costs',
                'type': 'number',
                'unit': 'Eurocent/km',
                'range': [0, 9999],
                'default': 16,
            },
            'kmcharge': {
                'label': 'Kilometercharge',
                'type': 'number',
                'unit': 'Euro/km',
                'range': [0, 9999],
                'default': 0
            },
            'parking search file': {
                'label': 'parking search file',
                'type': 'file',
                'default': ''
            },
            'parking costs': {
                'label': 'Is there a file with parking costs (per day) for every zone?',
                'use': {
                    'label': 'Parking costs per day',
                    'type': 'checkbox',
                    'default': False
                },
                'data-file': {
                    'label': 'Parking costs file (tariifs are is in eurocents (€2,20 should be 220 in the file)',
                    'type': 'file',
                    'default': ''
                },
            },
            'additional costs': {
                'label': 'Is there a file with additional costs (amounts are in euros)?',
                'use': {
                    'label': 'Additional costs',
                    'type': 'checkbox',
                    'default': False
                },
                'data-file': {
                    'label': 'Additional costs file',
                    'type': 'file',
                    'default': ''
                },
            },
 #           'nocarcategory': {
 #               'label': 'Categorisation of non-car-owners (NoCar possesses no car but has a driving license)',
 #               'type': 'checklist',
 #               'items': ['NoCar', 'NoLicense'],
 #               'default': ['NoCar', 'NoLicense']
 #           },
            'variable costs no car': {
                'label': 'Variable costs no car',
                'NoCar': {
                    'label': 'Variable costs Share Car',
                    'type': 'number',
                    'unit': 'Euro/km',
                    'range': [0, 9999],
                    'default': 0.33
                },
                'NoLicense': {
                    'label': 'Variable costs Taxi (possesses no driving license',
                    'type': 'number',
                    'unit': 'Euro/km',
                    'range': [0, 9999],
                    'default': 2.40
                }
            },
            'time costs no car': {
                'label': 'Time costs no car',
                'NoCar': {
                    'label': 'Time Costs for Share Care',
                    'type': 'number',
                    'unit': 'Euro/Minuut',
                    'range': [0, 9999],
                    'default': 0.05
                },
                'NoLicense': {
                    'label': 'Time costs Taxi (possesses no driving license',
                    'type': 'number',
                    'unit': 'Euro/Minuut',
                    'range': [0, 9999],
                    'default': 0.40
                }
            }
        },
        'TVOM': {
            'label': 'Value of Time',
            'work': {
                'label': 'Value of 1€ costs in experienced travel time per income group, motive work',
                'high': {
                    'label': 'High',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 4
                },
                'middle high': {
                    'label': 'Middle high',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 6
                },
                'middle low': {
                    'label': 'Middle low',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 9
                },
                'low': {
                    'label': 'Low',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 12
                }
            },
            'other': {
                'label': 'Value of 1€ costs in experienced travel time per income group, motive other',
                'high': {
                    'label': 'High',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 4.8
                },
                'middle high': {
                    'label': 'Middle high',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 7.25
                },
                'middel low': {
                    'label': 'Middle low',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 10.9
                },
                'low': {
                    'label': 'Low',
                    'type': 'number',
                    'unit': 'Minutes/Euro',
                    'default': 15.5
                }
            },
        },
        'distribution': {
            'label': 'Distribution over Groups',
            'EV': {
                'label': 'Percentage EV',
                'type': 'choice',
                'items': ['0', '20', '40'],
                'unit': '%',
                'default': '0'
            },
            'artificialcarpossession': {
                'label': 'Policy on car possession (such as low parking standards)',
                'use': {
                    'label': 'Use artificial car possession',
                    'type': 'checkbox',
                    'default': False
                },
                'data-file': {
                    'label': 'Artificial car possession file',
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
            'Free Transit Forfait share': {
                'label': 'Share of people with free transit forfaits',
                'type': 'number',
                'unit': '(share)',
                'range': [0, 1],
                'default': 0.03
            },
#            'uitvoername': {
#                'label': 'name van uitvoerbestand',
#                'type': 'text',
#                'default': 'verdelingovergroepen'
#            }
        },

        # 'ontplooiing': {
        # 'label': 'Ontplooiing',
        # 'verdeling_file': {
        # 'label': 'Verdeling over groepen bestand',
        # 'type': 'file',
        # 'default': ''
        # },
        # 'uitvoerdirectoryname': {
        # 'label': 'name van uitvoerdirectory',
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
        # 'uitvoer_directory_name': {
        # 'label': 'name van uitvoer directory',
        # 'type': 'text',
        # 'default': 'uitvoer'
        # }
        # }
    }


def projectName(config):
    """
  Returns the contant of the field where the project name is stored.
  """
    return config['project']['name']


def validateConfiguration(config, strict=True):
    """
  Validate a Configuration dictionary.
  """
    return validate.validateConfigWithTemplate ( config, DefaultConfigurationDefinition ( ), strict=strict )


def DefaultConfiguration():
    """
  Returns the Default Configuration as defined in the aboive defined template.
  """
    template = DefaultConfigurationDefinition ( )
    config = build.buildConfigDict ( template )
    return config
