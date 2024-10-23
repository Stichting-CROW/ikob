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
    hubs = [hub - 1 for hub in hubs]

    Autotijdmatrix = read_csv(skims_directory / 'Auto_Tijd.csv')
    Fietstijdmatrix = read_csv(skims_directory / 'Fiets_Tijd.csv')
    OVtijdmatrix = read_csv(skims_directory / 'OV_Tijd.csv')
    Autoafstandmatrix = read_csv(skims_directory / 'Auto_Afstand.csv')
    OVafstandmatrix = read_csv(skims_directory / 'OV_Afstand.csv')

    n_hubs = len(hubs)
    n_car_times = len(Autotijdmatrix)

    PplusRherkomsttijdmatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusRbestemmingstijdmatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusFietstijdmatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusRherkomstafstandOVmatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusRherkomstafstandautomatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusRbestemmingsafstandOVmatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusRbestemmingsafstandautomatrix = np.zeros((n_hubs, n_car_times, n_car_times))
    PplusFietsautoafstandmatrix = np.zeros((n_hubs, n_car_times, n_car_times))

    for h, hub in enumerate(hubs):
        for i in range(n_car_times):
            for j in range(n_car_times):
                if OVtijdmatrix[i, hub] <= Autotijdmatrix[hub, j]:
                    PplusRbestemmingstijdmatrix[h, i, j] = OVtijdmatrix[i, hub] + Autotijdmatrix[hub, j]
                    PplusRbestemmingsafstandautomatrix[h, i, j] = Autoafstandmatrix[hub, j]
                    PplusRbestemmingsafstandOVmatrix[h, i, j] = OVafstandmatrix[i, hub]
                    PplusRherkomsttijdmatrix[h, i, j] = Autotijdmatrix[i, hub] + OVtijdmatrix[hub, j]
                    PplusRherkomstafstandautomatrix[h, i, j] = Autoafstandmatrix[i, hub]
                    PplusRherkomstafstandOVmatrix[h, i, j] = OVafstandmatrix[hub, j]
                else:
                    PplusRbestemmingstijdmatrix[h, i, j] = Autotijdmatrix[i, hub] + OVtijdmatrix[hub, j]
                    PplusRbestemmingsafstandautomatrix[h, i, j] = Autoafstandmatrix[i, hub]
                    PplusRbestemmingsafstandOVmatrix[h, i, j] = OVafstandmatrix[hub, j]
                    PplusRherkomsttijdmatrix[h, i, j] = OVtijdmatrix[i, hub] + Autotijdmatrix[hub, j]
                    PplusRherkomstafstandautomatrix[h, i, j] = Autoafstandmatrix[hub, j]
                    PplusRherkomstafstandOVmatrix[h, i, j] = OVafstandmatrix[i, hub]

    for h, hub in enumerate(hubs):
        for i in range(n_car_times):
            for j in range(n_car_times):
                if Fietstijdmatrix[i, hub] <= Fietstijdmatrix[hub, j]:
                    PplusFietstijdmatrix[h, i, j] = Fietstijdmatrix[i, hub] + Autotijdmatrix[hub, j]
                    PplusFietsautoafstandmatrix[h, i, j] = Autoafstandmatrix[hub, j]
                else:
                    PplusFietstijdmatrix[h, i, j] = Fietstijdmatrix[j, hub] + Autotijdmatrix[hub, i]
                    PplusFietsautoafstandmatrix[h, i, j] = Autoafstandmatrix[hub, i]

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
    PplusRherkomsttijdtotaal = np.min(PplusRherkomsttijdmatrix, axis=0, initial=initial)
    PplusFietstijdtotaal = np.min(PplusFietstijdmatrix, axis=0, initial=initial)
    PplusRherkomstafstandOVtotaal = np.min(PplusRherkomstafstandOVmatrix, axis=0, initial=initial)
    PplusRbestemmingsafstandautototaal = np.min(PplusRbestemmingsafstandautomatrix, axis=0, initial=initial)
    PplusRbestemmingsafstandOVtotaal = np.min(PplusRbestemmingsafstandOVmatrix, axis=0, initial=initial)
    PplusFietsautoafstandtotaal = np.min(PplusFietsautoafstandmatrix, axis=0, initial=initial)
    PplusRbestemmingstijdtotaal = np.min(PplusRbestemmingstijdmatrix, axis=0, initial=initial)
    PplusRherkomstafstandautototaal = np.min(PplusRherkomstafstandautomatrix, axis=0, initial=initial)

    Pplusfietshubplek = np.zeros((n_car_times, n_car_times))
    PplusRhubplek = np.zeros((n_car_times, n_car_times))

    for i in range(n_car_times):
        for j in range(n_car_times):
            index = np.argmin(PplusRbestemmingstijdmatrix[:, i, j])
            PplusRhubplek[i, j] = hubs[index]

            index = np.argmin(PplusRherkomstafstandautomatrix[:, i, j])
            Pplusfietshubplek[i, j] = hubs[index]

    # Convert to one-base indexing before writing output.
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
