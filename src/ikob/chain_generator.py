import os
import pathlib

import numpy as np

from ikob.utils import read_csv, write_csv


def ask_user_for_skims_directory():
    """Prompt user for skims directory using a Tk filedialog window."""
    from tkinter import Tk, filedialog

    main_window_size = "10x10"
    label = "Voer de directory waar de pure reistijdskims en afstandskims in staan"
    initialdir = os.getcwd()
    title = "Selecteer de directory skimsdirectory"

    skims = Tk()
    skims.geometry = main_window_size
    skims.label = label
    skims.directory = filedialog.askdirectory(initialdir=initialdir,
                                              title=title)
    skims.destroy()
    return skims.directory + '/'


def ask_user_for_hubs() -> list[int]:
    """Prompt user over ``stdin`` for hubs in the hub set."""
    hubs = []
    prompt = 'Geef de zone(s) met hub(s) één voor één aan. Als je de laatste hebt gehad, typ dan -1: '

    while True:
        response = input(prompt)

        hub = int(response)
        if hub < 0:
            break

    return hubs


def ask_user_for_hub_name() -> str:
    """Prompt user over ``stdin`` for a idenfier for the hub set."""
    prompt = 'Geef de hubset een naam'
    return input(prompt)


def ask_user_for_transfer_times() -> tuple[int, int]:
    """Prompt user over ``stdin`` for transfer time between transport kinds."""
    prompt = 'Hoeveel overstaptijd is er op de hub tussen auto en OV?'
    transfer_time_car_pt = int(input(prompt))

    prompt = 'Hoeveel overstaptijd is er op de hub tussen auto en fiets?'
    transfer_time_car_bike = int(input(prompt))

    return transfer_time_car_pt, transfer_time_car_bike


def chain_generator(skims_directory: pathlib.Path,
                    name: str,
                    hubs: list[int],
                    transfer_time_pt: int,
                    transfer_time_bike: int):
    """Generate skim input files for chains (P+R)

    Note: The hubs are internally converted for zero-base indexing.
    """
    # Correct for zero-base indexing.
    hubs = np.array(hubs) - 1

    car_times = read_csv(skims_directory / 'Auto_Tijd.csv')
    bike_times = read_csv(skims_directory / 'Fiets_Tijd.csv')
    pt_times = read_csv(skims_directory / 'OV_Tijd.csv')
    car_distances = read_csv(skims_directory / 'Auto_Afstand.csv')
    pt_distances = read_csv(skims_directory / 'OV_Afstand.csv')

    n_hubs = len(hubs)
    n_car_times = len(car_times)

    pr_origin_times = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_destination_times = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_bike_times = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_origin_pt_distances = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_origin_car_distances = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_destination_pt_distances = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_destination_car_distances = np.zeros((n_car_times, n_car_times, n_hubs))
    pr_bike_car_distances = np.zeros((n_car_times, n_car_times, n_hubs))

    for (i, j) in np.ndindex(n_car_times, n_car_times):
        mask = pt_times[i, hubs] <= car_times[hubs, j]

        pr_destination_times[i, j, :] = np.where(
            mask,
            pt_times[i, hubs] + car_times[hubs, j],
            car_times[i, hubs] + pt_times[hubs, j],
        )

        pr_origin_times[i, j, :] = np.where(
            mask,
            car_times[i, hubs] + pt_times[hubs, j],
            pt_times[i, hubs] + car_times[hubs, j],
        )

        pr_destination_car_distances[i, j, :] = np.where(
            mask,
            car_distances[hubs, j],
            car_distances[i, hubs],
        )

        pr_destination_pt_distances[i, j, :] = np.where(
            mask,
            pt_distances[i, hubs],
            pt_distances[hubs, j],
        )

        pr_origin_car_distances[i, j, :] = np.where(
            mask,
            car_distances[i, hubs],
            car_distances[hubs, j],
        )

        pr_origin_pt_distances[i, j, :] = np.where(
            mask,
            pt_distances[hubs, j],
            pt_distances[i, hubs],
        )

    for (i, j) in np.ndindex(n_car_times, n_car_times):
        mask = bike_times[i, hubs] <= bike_times[hubs, j]

        pr_bike_times[i, j, :] = np.where(
            mask,
            bike_times[i, hubs] + car_times[hubs, j],
            bike_times[j, hubs] + car_times[hubs, i],
        )

        pr_bike_car_distances[i, j, :] = np.where(
            mask,
            car_distances[hubs, j],
            car_distances[hubs, i],
        )

    # Add additional transfer times.
    pr_destination_times += transfer_time_pt
    pr_origin_times += transfer_time_pt
    pr_bike_times += transfer_time_bike

    # Apply rouding to all arrays.
    arrays = [
        pr_origin_times,
        pr_destination_times,
        pr_bike_times,
        pr_origin_pt_distances,
        pr_origin_car_distances,
        pr_destination_pt_distances,
        pr_destination_car_distances,
        pr_bike_car_distances,
    ]
    for array in arrays:
        array[:] = np.round(array)

    # Compute minimum distance, time values.

    # FIXME: The original implementation computed the minimum value by looping
    # over the arrays with an starting value of 9999. This initial value needs
    # to be kept when using numpy arrays as the contents _do_ exceed this value
    # and this should be verified.
    initial = 9999
    pr_origin_time = np.min(pr_origin_times, axis=2, initial=initial)
    pr_bike_time = np.min(pr_bike_times, axis=2, initial=initial)
    pr_origin_pt_distance = np.min(
        pr_origin_pt_distances, axis=2, initial=initial)
    pr_destination_car_distance = np.min(
        pr_destination_car_distances, axis=2, initial=initial)
    pr_destination_pt_distance = np.min(
        pr_destination_pt_distances, axis=2, initial=initial)
    pr_bike_car_distance = np.min(
        pr_bike_car_distances, axis=2, initial=initial)
    pr_destination_time = np.min(pr_destination_times, axis=2, initial=initial)
    pr_origin_car_distance = np.min(
        pr_origin_car_distances, axis=2, initial=initial)

    # Extract hubs at minimum values.
    rmin = np.argmin(pr_destination_times, axis=2)
    fietsmin = np.argmin(pr_origin_car_distances, axis=2)
    pr_min_hubs = hubs[rmin]
    pr_min_hubs_bike = hubs[fietsmin]

    # Convert hubs to one-base indexing before writing output.
    pr_min_hubs += 1
    pr_min_hubs_bike += 1

    filename_and_data = [
        (f'PplusR_{name}_bestemmings_Tijd.csv', pr_destination_time),
        (f'PplusR_{name}_bestemmings_Afstand_Auto.csv', pr_destination_car_distance),
        (f'PplusR_{name}_bestemmings_Afstand_OV.csv', pr_destination_pt_distance),
        (f'PplusR_{name}_herkomst_Tijd.csv', pr_origin_time),
        (f'PplusR_{name}_herkomst_Afstand_Auto.csv', pr_origin_car_distance),
        (f'PplusR_{name}_herkomst_Afstand_OV.csv', pr_origin_pt_distance),
        (f'Pplusfiets_{name}_Tijd.csv', pr_bike_time),
        (f'Pplusfiets_{name}_Afstand_Auto.csv', pr_bike_car_distance),
        (f'Pplusfiets_{name}_bestehubs.csv', pr_min_hubs_bike),
        (f'PplusR_{name}_bestehubs.csv', pr_min_hubs),
    ]
    for filename, data in filename_and_data:
        write_csv(data, skims_directory / filename)


if __name__ == "__main__":
    skims_directory = pathlib.Path(ask_user_for_skims_directory())
    hubs = ask_user_for_hubs()
    hub_name = ask_user_for_hub_name()
    transfer_times = ask_user_for_transfer_times()
    chain_generator(skims_directory, hub_name, hubs, *transfer_times)
