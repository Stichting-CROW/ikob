import numpy as np
import pathlib
from ikob.utils import read_csv, write_csv

import os


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

    Autotijdmatrix = read_csv(skims_directory / 'Auto_Tijd.csv')
    Fietstijdmatrix = read_csv(skims_directory / 'Fiets_Tijd.csv')
    OVtijdmatrix = read_csv(skims_directory / 'OV_Tijd.csv')
    Autoafstandmatrix = read_csv(skims_directory / 'Auto_Afstand.csv')
    OVafstandmatrix = read_csv(skims_directory / 'OV_Afstand.csv')

    n_hubs = len(hubs)
    n_car_times = len(Autotijdmatrix)

    PplusRherkomsttijdmatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusRbestemmingstijdmatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusFietstijdmatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusRherkomstafstandOVmatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusRherkomstafstandautomatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusRbestemmingsafstandOVmatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusRbestemmingsafstandautomatrix = np.zeros((n_car_times, n_car_times, n_hubs))
    PplusFietsautoafstandmatrix = np.zeros((n_car_times, n_car_times, n_hubs))

    for i in range(n_car_times):
        for j in range(n_car_times):
            for h, hub in enumerate(hubs):
                if OVtijdmatrix[i, hub] <= Autotijdmatrix[hub, j]:
                    PplusRbestemmingstijdmatrix[i, j, h] = OVtijdmatrix[i, hub] + Autotijdmatrix[hub, j]
                    PplusRbestemmingsafstandautomatrix[i, j, h] = Autoafstandmatrix[hub, j]
                    PplusRbestemmingsafstandOVmatrix[i, j, h] = OVafstandmatrix[i, hub]
                    PplusRherkomsttijdmatrix[i, j, h] = Autotijdmatrix[i, hub] + OVtijdmatrix[hub, j]
                    PplusRherkomstafstandautomatrix[i, j, h] = Autoafstandmatrix[i, hub]
                    PplusRherkomstafstandOVmatrix[i, j, h] = OVafstandmatrix[hub, j]
                else:
                    PplusRbestemmingstijdmatrix[i, j, h] = Autotijdmatrix[i, hub] + OVtijdmatrix[hub, j]
                    PplusRbestemmingsafstandautomatrix[i, j, h] = Autoafstandmatrix[i, hub]
                    PplusRbestemmingsafstandOVmatrix[i, j, h] = OVafstandmatrix[hub, j]
                    PplusRherkomsttijdmatrix[i, j, h] = OVtijdmatrix[i, hub] + Autotijdmatrix[hub, j]
                    PplusRherkomstafstandautomatrix[i, j, h] = Autoafstandmatrix[hub, j]
                    PplusRherkomstafstandOVmatrix[i, j, h] = OVafstandmatrix[i, hub]

    for i in range(n_car_times):
        for j in range(n_car_times):
            PplusFietstijdmatrix[i, j, :] = np.where(Fietstijdmatrix[i, hubs] <= Fietstijdmatrix[hubs, j],
                                                     Fietstijdmatrix[i, hubs] + Autotijdmatrix[hubs, j],
                                                     Fietstijdmatrix[j, hubs] + Autotijdmatrix[hubs, i])

            PplusFietsautoafstandmatrix[i, j, :] = np.where(Fietstijdmatrix[i, hubs] <= Fietstijdmatrix[hubs, j],
                                                            Autoafstandmatrix[hubs, j],
                                                            Autoafstandmatrix[hubs, i])

    PplusRbestemmingstijdmatrix += transfer_time_pt
    PplusRherkomsttijdmatrix += transfer_time_pt
    PplusFietstijdmatrix += transfer_time_bike

    arrays = [
        PplusRherkomsttijdmatrix,
        PplusRbestemmingstijdmatrix,
        PplusFietstijdmatrix,
        PplusRherkomstafstandOVmatrix,
        PplusRherkomstafstandautomatrix,
        PplusRbestemmingsafstandOVmatrix,
        PplusRbestemmingsafstandautomatrix,
        PplusFietsautoafstandmatrix,
    ]
    for array in arrays:
        array[:] = np.round(array)

    # FIXME: The original implementation computed the minimum value by looping
    # over the arrays with an starting value of 9999. This initial value needs
    # to be kept when using numpy arrays as the contents _do_ exceed this value
    # and this should be verified.
    initial = 9999
    PplusRherkomsttijdtotaal = np.min(PplusRherkomsttijdmatrix, axis=2, initial=initial)
    PplusFietstijdtotaal = np.min(PplusFietstijdmatrix, axis=2, initial=initial)
    PplusRherkomstafstandOVtotaal = np.min(PplusRherkomstafstandOVmatrix, axis=2, initial=initial)
    PplusRbestemmingsafstandautototaal = np.min(PplusRbestemmingsafstandautomatrix, axis=2, initial=initial)
    PplusRbestemmingsafstandOVtotaal = np.min(PplusRbestemmingsafstandOVmatrix, axis=2, initial=initial)
    PplusFietsautoafstandtotaal = np.min(PplusFietsautoafstandmatrix, axis=2, initial=initial)
    PplusRbestemmingstijdtotaal = np.min(PplusRbestemmingstijdmatrix, axis=2, initial=initial)
    PplusRherkomstafstandautototaal = np.min(PplusRherkomstafstandautomatrix, axis=2, initial=initial)

    # Extract hubs at minimum values.
    rmin = np.argmin(PplusRbestemmingstijdmatrix, axis=2)
    fietsmin = np.argmin(PplusRherkomstafstandautomatrix, axis=2)
    PplusRhubplek = hubs[rmin]
    Pplusfietshubplek = hubs[fietsmin]

    # Convert hubs to one-base indexing before writing output.
    PplusRhubplek += 1
    Pplusfietshubplek += 1

    filename_and_data = [
        (f'PplusR_{name}_bestemmings_Tijd.csv', PplusRbestemmingstijdtotaal),
        (f'PplusR_{name}_bestemmings_Afstand_Auto.csv', PplusRbestemmingsafstandautototaal),
        (f'PplusR_{name}_bestemmings_Afstand_OV.csv', PplusRbestemmingsafstandOVtotaal),
        (f'PplusR_{name}_herkomst_Tijd.csv', PplusRherkomsttijdtotaal),
        (f'PplusR_{name}_herkomst_Afstand_Auto.csv', PplusRherkomstafstandautototaal),
        (f'PplusR_{name}_herkomst_Afstand_OV.csv', PplusRherkomstafstandOVtotaal),
        (f'Pplusfiets_{name}_Tijd.csv', PplusFietstijdtotaal),
        (f'Pplusfiets_{name}_Afstand_Auto.csv', PplusFietsautoafstandtotaal),
        (f'Pplusfiets_{name}_bestehubs.csv', Pplusfietshubplek),
        (f'PplusR_{name}_bestehubs.csv', PplusRhubplek),
    ]
    for filename, data in filename_and_data:
        write_csv(data, skims_directory / filename)


if __name__ == "__main__":
    skims_directory = pathlib.Path(ask_user_for_skims_directory())
    hubs = ask_user_for_hubs()
    hub_name = ask_user_for_hub_name()
    transfer_times = ask_user_for_transfer_times()
    chain_generator(skims_directory, hub_name, hubs, *transfer_times)
