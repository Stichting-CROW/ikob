import logging

import numpy as np

import ikob.utils as utils
from ikob.datasource import (DataKey, DataSource, DataType, SegsSource,
                             SkimsSource, read_csv_from_config,
                             read_parking_times)

logger = logging.getLogger(__name__)


def costs_public_transport(
        distance,
        pt_km_price,
        starting_rate,
        pricecap,
        pricecap_value):
    distance = np.where(distance < 0, 0, distance)
    distance = starting_rate + distance * pt_km_price

    if pricecap:
        np.clip(distance, None, pricecap_value, out=distance)

    return distance


def generalised_travel_time(config) -> DataSource:
    logger.info("Compute generalised travel time from time and costs.")

    project_config = config['project']
    skims_config = config['skims']
    tvom_config = config['TVOM']
    advanced_config = config['geavanceerd']
    ketens_config = config['ketens']

    scenario = project_config['verstedelijkingsscenario']
    regime = project_config['beprijzingsregime']
    motives = project_config['motieven']
    chains = ketens_config['chains']['gebruiken']
    use_destination_list = ketens_config['bestemmingslijst']['gebruiken']
    hub_name = ketens_config['chains']['naam hub']
    pt_cost_file = skims_config['OV kostenbestand']['gebruiken']
    tvom_work = tvom_config['werk']
    tvom_other = tvom_config['overig']
    var_fossil = skims_config['Kosten auto fossiele brandstof']['variabele kosten']
    road_pricing_fossil = skims_config['Kosten auto fossiele brandstof']['kmheffing']
    var_electric = skims_config['Kosten elektrische auto']['variabele kosten']
    road_pricing_electric = skims_config['Kosten elektrische auto']['kmheffing']
    costs_no_car = skims_config['varkostenga']
    time_costs_no_car = skims_config['tijdkostenga']
    part_of_day = skims_config['dagsoort']
    kind_no_car = ['GeenAuto', 'GeenRijbewijs']
    pt_km_price = skims_config['OV kosten']['kmkosten']
    starting_rate = skims_config['OV kosten']['starttarief']
    additional_costs = advanced_config['additionele_kosten']['gebruiken']
    parking_costs = advanced_config['parkeerkosten']['gebruiken']
    pricecap = skims_config['pricecap']['gebruiken']
    pricecap_value = skims_config['pricecap']['getal']
    parking_times_temporary = read_csv_from_config(
        config, key='skims', id='parkeerzoektijden_bestand')

    if parking_costs:
        parking_cost_array = read_csv_from_config(
            config, key='geavanceerd', id='parkeerkosten')
    else:
        parking_cost_array = utils.zeros(len(parking_times_temporary))

    if additional_costs:
        additional_cost_matrix = read_csv_from_config(
            config, key='geavanceerd', id='additionele_kosten')
    if chains:
        hubset = read_csv_from_config(config, key='ketens', id='chains')
        print(hubset)

    income_levels = ['laag', 'middellaag', 'middelhoog', 'hoog']
    pt_km_price = pt_km_price / 100
    starting_rate = starting_rate / 100
    var_fossil = var_fossil / 100
    var_electric = var_electric / 100
    road_pricing_fossil = road_pricing_fossil / 100
    road_pricing_electric = road_pricing_electric / 100
    fuel_kinds = ['fossiel', 'elektrisch']
    parking_times = read_parking_times(config)

    segs_source = SegsSource(config)

    skims_dir = config['project']['paden']['skims_directory']
    skims_reader = SkimsSource(skims_dir)

    generalised_travel_time = DataSource(
        config, DataType.GENERALISED_TRAVEL_TIME)

    for motive in motives:
        tvom = tvom_work if motive == 'werk' else tvom_other
        for pod in part_of_day:
            car_time_matrix = skims_reader.read('Auto_Tijd', pod)
            car_distance_matrix = skims_reader.read('Auto_Afstand', pod)
            bike_time_matrix = skims_reader.read('Fiets_Tijd', pod)
            pt_time_matrix = skims_reader.read('OV_Tijd', pod)

            num_zones_time = len(car_time_matrix)
            num_zones_distance = len(car_distance_matrix)
            msg = (
                "Number of zones in time and distance have to match: "
                f"{num_zones_distance} == {num_zones_time}"
            )
            assert num_zones_distance == num_zones_time, msg
            num_zones = num_zones_time

            if pt_cost_file:
                pt_cost_matrix = skims_reader.read("OV_Kosten", pod)
            else:
                pt_distance_matrix = skims_reader.read('OV_Afstand', pod)
                n = len(pt_time_matrix)
                pt_cost_matrix = np.zeros((n, n))
                pt_cost_matrix = costs_public_transport(
                    pt_distance_matrix, pt_km_price, starting_rate, pricecap, pricecap_value)

            # Eerst de fiets:
            ggr_skim = np.where(
                bike_time_matrix < 180,
                bike_time_matrix,
                9999)

            key = DataKey(id='Fiets',
                          part_of_day=pod,
                          regime=regime,
                          motive=motive)
            generalised_travel_time.set(key, ggr_skim.copy())

            ggr_skim = np.zeros((num_zones, num_zones))
            for income_level in income_levels:
                factor = tvom.get(income_level)

                for fuel_kind in fuel_kinds:
                    if fuel_kind == 'fossiel':
                        var_car_rate = var_fossil
                        road_pricing = road_pricing_fossil
                    else:
                        var_car_rate = var_electric
                        road_pricing = road_pricing_electric
                    for i in range(num_zones):
                        for j in range(num_zones):
                            total_time = car_time_matrix[i][j] + \
                                parking_times[i][1] + parking_times[j][2]
                            if additional_costs:
                                ggr_skim[i][j] = total_time + factor * (car_distance_matrix[i][j] * (
                                    var_car_rate + road_pricing) + additional_cost_matrix[i][j] / 100 + parking_cost_array[j] / 100)
                            else:
                                ggr_skim[i][j] = total_time + factor * (car_distance_matrix[i][j] * (
                                    var_car_rate + road_pricing) + parking_cost_array[j] / 100)
                    if chains:
                        key = DataKey(id=f'Pplusfiets_{fuel_kind}',
                                      part_of_day=pod,
                                      income=income_level,
                                      hub_name=hub_name,
                                      motive=motive,
                                      regime=regime)
                        ggr_park_and_bike_skim = generalised_travel_time.get(
                            key)
                        bestskim = np.minimum(ggr_skim, ggr_park_and_bike_skim)
                        key = DataKey(id=f'PplusR_{fuel_kind}',
                                      part_of_day=pod,
                                      income=income_level,
                                      hub_name=hub_name,
                                      motive=motive,
                                      regime=regime)
                        ggr_park_and_ride_skim = generalised_travel_time.get(
                            key)
                        ggr_skim = np.minimum(bestskim, ggr_park_and_ride_skim)

                    key = DataKey(id=f"Auto_{fuel_kind}",
                                  part_of_day=pod,
                                  income=income_level,
                                  regime=regime,
                                  motive=motive)
                    generalised_travel_time.set(key, ggr_skim.copy())

                # Dan het OV
                factor = tvom.get(income_level)
                ggr_skim = np.where(
                    pt_time_matrix > 0.5,
                    pt_time_matrix +
                    factor *
                    pt_cost_matrix,
                    9999)
                key = DataKey(id='OV',
                              part_of_day=pod,
                              income=income_level,
                              motive=motive,
                              regime=regime)
                generalised_travel_time.set(key, ggr_skim.copy())

                # Dan geen auto (rijbewijs)
                for kind in kind_no_car:
                    ggr_skim.fill(99999)
                    factor = tvom.get(income_level)
                    for i in range(num_zones):
                        for j in range(num_zones):
                            if car_time_matrix[i][j] >= 7:
                                total_time = car_time_matrix[i][j] + \
                                    parking_times[i][1] + parking_times[j][2]
                                total_cost = car_time_matrix[i][j] * time_costs_no_car.get(
                                    kind) + car_distance_matrix[i][j] * (costs_no_car.get(kind) + road_pricing)
                                ggr_skim[i][j] = total_time + \
                                    factor * total_cost

                    key = DataKey(id=f'{kind}',
                                  part_of_day=pod,
                                  income=income_level,
                                  motive=motive,
                                  regime=regime)
                    generalised_travel_time.set(key, ggr_skim.copy())

                # GratisAuto
                for income_level in income_levels:
                    ggr_skim.fill(0)
                    factor = tvom.get(income_level)
                    for i in range(num_zones):
                        for j in range(num_zones):
                            total_time = car_time_matrix[i][j] + \
                                parking_times[i][1] + parking_times[j][2]
                            if additional_costs:
                                ggr_skim[i][j] = total_time + factor * (
                                    car_distance_matrix[i][j] * road_pricing + additional_cost_matrix[i][j] / 100 + parking_cost_array[j] / 100)
                            else:
                                ggr_skim[i][j] = total_time + factor * (
                                    car_distance_matrix[i][j] * road_pricing + parking_cost_array[j] / 100)
                    key = DataKey(id='GratisAuto',
                                  part_of_day=pod,
                                  income=income_level,
                                  motive=motive,
                                  regime=regime)
                    generalised_travel_time.set(key, ggr_skim.copy())

                # GratisOV
                ggr_skim = np.where(
                    pt_time_matrix > 0.5,
                    pt_time_matrix,
                    9999)
                key = DataKey(id='GratisOV',
                              part_of_day=pod,
                              motive=motive,
                              regime=regime)
                generalised_travel_time.set(key, ggr_skim.copy())

    return generalised_travel_time
