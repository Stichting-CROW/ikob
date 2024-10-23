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

    Pplusfietshubplek = []
    PplusRhubplek = []
    PplusRherkomsttijdtotaal = []
    PplusRbestemmingstijdtotaal = []
    PplusFietstijdtotaal = []
    PplusRherkomstafstandOVtotaal = []
    PplusRherkomstafstandautototaal = []
    PplusRbestemmingsafstandOVtotaal = []
    PplusRbestemmingsafstandautototaal = []
    PplusFietsautoafstandtotaal = []

    for i in range(n_car_times):
        PplusRherkomsttijdtotaal.append([])
        PplusRbestemmingstijdtotaal.append([])
        PplusFietstijdtotaal.append([])
        PplusRherkomstafstandOVtotaal.append([])
        PplusRherkomstafstandautototaal.append([])
        PplusRbestemmingsafstandOVtotaal.append([])
        PplusRbestemmingsafstandautototaal.append([])
        PplusFietsautoafstandtotaal.append([])
        Pplusfietshubplek.append([])
        PplusRhubplek.append([])

        for j in range(n_car_times):
            minimum = 9999
            for h in range (len(hubs)):
                minimum = min (minimum,PplusRherkomsttijdmatrix[h, i, j])
            PplusRherkomsttijdtotaal[i].append (minimum)
            minimum = 9999
            minimumoud = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusRbestemmingstijdmatrix[h, i, j])
                if minimum < minimumoud :
                    hbewaar = h
                    minimumoud = minimum
            PplusRhubplek[i].append ( hubs[hbewaar] + 1 )
            PplusRbestemmingstijdtotaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusFietstijdmatrix[h, i, j])
            PplusFietstijdtotaal[i].append ( minimum )
            minimum = 9999
            minimoud = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusRherkomstafstandautomatrix[h, i, j])
                if minimum < minimumoud :
                    hbewaar = h
                    minimumoud = minimum
            Pplusfietshubplek[i].append ( hubs[hbewaar] + 1 )
            PplusRherkomstafstandautototaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusRherkomstafstandOVmatrix[h, i, j])
            PplusRherkomstafstandOVtotaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusRbestemmingsafstandautomatrix[h, i, j])
            PplusRbestemmingsafstandautototaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusRbestemmingsafstandOVmatrix[h, i, j])
            PplusRbestemmingsafstandOVtotaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( hubs ) ):
                minimum = min ( minimum, PplusFietsautoafstandmatrix[h, i, j])
            PplusFietsautoafstandtotaal[i].append ( minimum )

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
