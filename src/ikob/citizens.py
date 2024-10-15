import ikob.utils as utils
from tkinter import *
import os
from ikobconfig import getConfigFromArgs

# Deze routine kijkt naar de command-line en leest
# het opgegeven configuratie bestand in een dict.
# Indien er een probleem is, sluit het script hier af.
config = getConfigFromArgs()
paden_config = config['project']['paden']

# Ophalen van instellingen
skims_directory = paden_config['skims_directory']
segs_directory = paden_config['segs_directory']
year=config['project']['jaar']

income_distribution_path = os.path.join (segs_directory, 'Inkomensverdeling_per_zone')
citizens_count_path = os.path.join (segs_directory, f'Beroepsbevolking{year}')
incomde_distribution = utils.read_csv_int(income_distribution_path,aantal_lege_regels=1)
citizens = utils.read_csv_int(citizens_count_path)
citizens_per_zone = []
for i in range (len(citizens)):
    citizens_per_zone.append([])
    for j in range (len(incomde_distribution[0])):
        citizens_per_zone[i].append(int(citizens[i]*incomde_distribution[i][j]/100))
citizens_class_zone_file = os.path.join (segs_directory, f'Inwoners_per_klasse{year}')
utils.write_csv(citizens_per_zone,citizens_class_zone_file)
