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
                    overstaptijdov: int,
                    overstaptijdfiets: int):
    """Generate skim input files for chains (P+R)

    Note: The hubs are internally converted for zero-base indexing.
    """
    Skimsdirectory = skims_directory

    Hubset = [hub - 1 for hub in hubs]
    Hubsetnaam = name
    OverstaptijdOV = overstaptijdov
    Overstaptijdfiets = overstaptijdfiets

    Autotijdfilenaam = os.path.join(Skimsdirectory, 'Auto_Tijd.csv')
    Autotijdmatrix = read_csv(Autotijdfilenaam)
    Fietstijdfilenaam = os.path.join(Skimsdirectory, 'Fiets_Tijd.csv')
    Fietstijdmatrix = read_csv(Fietstijdfilenaam)
    OVtijdfilenaam = os.path.join(Skimsdirectory, 'OV_Tijd.csv')
    OVtijdmatrix = read_csv(OVtijdfilenaam)
    Autoafstandfilenaam = os.path.join(Skimsdirectory, 'Auto_Afstand.csv')
    Autoafstandmatrix = read_csv(Autoafstandfilenaam)
    OVafstandfilenaam = os.path.join(Skimsdirectory, 'OV_Afstand.csv')
    OVafstandmatrix = read_csv(OVafstandfilenaam)

    PplusRherkomsttijdmatrix = []
    PplusRbestemmingstijdmatrix = []
    PplusFietstijdmatrix = []
    PplusRherkomstafstandOVmatrix = []
    PplusRherkomstafstandautomatrix = []
    PplusRbestemmingsafstandOVmatrix = []
    PplusRbestemmingsafstandautomatrix = []
    PplusFietsautoafstandmatrix = []
    Pplusfietshubplek = []
    PplusRhubplek = []

    for h in range (len(Hubset)) :
        PplusRherkomsttijdmatrix.append([])
        PplusRbestemmingstijdmatrix.append([])
        PplusFietstijdmatrix.append([])
        PplusRherkomstafstandOVmatrix.append([])
        PplusRherkomstafstandautomatrix.append([])
        PplusRbestemmingsafstandOVmatrix.append([])
        PplusRbestemmingsafstandautomatrix.append([])
        PplusFietsautoafstandmatrix.append([])
        for i in range (len(Autotijdmatrix)) :
            PplusRbestemmingstijdmatrix[h].append([])
            PplusRherkomsttijdmatrix[h].append([])
            PplusFietstijdmatrix[h].append([])
            PplusFietsautoafstandmatrix[h].append ([])
            PplusRherkomstafstandOVmatrix[h].append([])
            PplusRherkomstafstandautomatrix[h].append([])
            PplusRbestemmingsafstandOVmatrix[h].append([])
            PplusRbestemmingsafstandautomatrix[h].append([])
            for j in range (len(Autotijdmatrix)) :
                if OVtijdmatrix [i][Hubset[h]] <= Autotijdmatrix [Hubset[h]][j]:
                    PplusRbestemmingstijdmatrix[h][i].append(round(OVtijdmatrix[i][Hubset[h]] + Autotijdmatrix[Hubset[h]][j]
                                                                   + OverstaptijdOV))
                    PplusRbestemmingsafstandautomatrix[h][i].append(round(Autoafstandmatrix [Hubset[h]][j]))
                    PplusRbestemmingsafstandOVmatrix[h][i].append(round(OVafstandmatrix [i][Hubset[h]]))
                    PplusRherkomsttijdmatrix[h][i].append (round(Autotijdmatrix[i][Hubset[h]] + OVtijdmatrix[Hubset[h]][j]
                                                                 + OverstaptijdOV))
                    PplusRherkomstafstandautomatrix[h][i].append(round(Autoafstandmatrix [i][Hubset[h]]))
                    PplusRherkomstafstandOVmatrix[h][i].append(round(OVafstandmatrix [Hubset[h]][j]))
                else:
                    PplusRbestemmingstijdmatrix[h][i].append(round(Autotijdmatrix[i][Hubset[h]] + OVtijdmatrix[Hubset[h]][j]
                                                                   + OverstaptijdOV))
                    PplusRbestemmingsafstandautomatrix[h][i].append(round(Autoafstandmatrix [i][Hubset[h]]))
                    PplusRbestemmingsafstandOVmatrix[h][i].append(round(OVafstandmatrix [Hubset[h]][j]))
                    PplusRherkomsttijdmatrix[h][i].append (round(OVtijdmatrix[i][Hubset[h]] + Autotijdmatrix[Hubset[h]][j]
                                                                 + OverstaptijdOV))
                    PplusRherkomstafstandautomatrix[h][i].append(round(Autoafstandmatrix [Hubset[h]][j]))
                    PplusRherkomstafstandOVmatrix[h][i].append(round(OVafstandmatrix [i][Hubset[h]]))
                if Fietstijdmatrix [i][Hubset[h]] <= Fietstijdmatrix [Hubset[h]][j]:
                    PplusFietstijdmatrix[h][i].append (round( Fietstijdmatrix[i][Hubset[h]] + Autotijdmatrix[Hubset[h]][j]
                                                              + Overstaptijdfiets))
                    PplusFietsautoafstandmatrix[h][i].append(round( Autoafstandmatrix[Hubset[h]][j]))
                else:
                    PplusFietstijdmatrix[h][i].append (round( Fietstijdmatrix[j][Hubset[h]] + Autotijdmatrix[Hubset[h]][i]
                                                              + Overstaptijdfiets))
                    PplusFietsautoafstandmatrix[h][i].append(round( Autoafstandmatrix[Hubset[h]][i]))

    PplusRherkomsttijdtotaal = []
    PplusRbestemmingstijdtotaal = []
    PplusFietstijdtotaal = []
    PplusRherkomstafstandOVtotaal = []
    PplusRherkomstafstandautototaal = []
    PplusRbestemmingsafstandOVtotaal = []
    PplusRbestemmingsafstandautototaal = []
    PplusFietsautoafstandtotaal = []
    for i in range (len(Autotijdmatrix)) :
        PplusRherkomsttijdtotaal.append([])
        PplusRbestemmingstijdtotaal.append([])
        PplusFietstijdtotaal.append([])
        PplusRherkomstafstandOVtotaal.append([])
        PplusRherkomstafstandautototaal.append([])
        PplusRbestemmingsafstandOVtotaal.append([])
        PplusRbestemmingsafstandautototaal.append([])
        PplusFietsautoafstandtotaal.append([])
        Pplusfietshubplek.append([])
        PplusRhubplek.append ( [] )
        for j in range (len(Autotijdmatrix)):
            minimum = 9999
            for h in range (len(Hubset)):
                minimum = min (minimum,PplusRherkomsttijdmatrix[h][i][j])
            PplusRherkomsttijdtotaal[i].append (minimum)
            minimum = 9999
            minimumoud = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusRbestemmingstijdmatrix[h][i][j])
                if minimum < minimumoud :
                    hbewaar = h
                    minimumoud = minimum
            PplusRhubplek[i].append ( Hubset[hbewaar] + 1 )
            PplusRbestemmingstijdtotaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusFietstijdmatrix[h][i][j])
            PplusFietstijdtotaal[i].append ( minimum )
            minimum = 9999
            minimoud = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusRherkomstafstandautomatrix[h][i][j])
                if minimum < minimumoud :
                    hbewaar = h
                    minimumoud = minimum
            Pplusfietshubplek[i].append ( Hubset[hbewaar] + 1 )
            PplusRherkomstafstandautototaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusRherkomstafstandOVmatrix[h][i][j])
            PplusRherkomstafstandOVtotaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusRbestemmingsafstandautomatrix[h][i][j])
            PplusRbestemmingsafstandautototaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusRbestemmingsafstandOVmatrix[h][i][j])
            PplusRbestemmingsafstandOVtotaal[i].append ( minimum )
            minimum = 9999
            for h in range ( len ( Hubset ) ):
                minimum = min ( minimum, PplusFietsautoafstandmatrix[h][i][j])
            PplusFietsautoafstandtotaal[i].append ( minimum )

    PplusRbestemmingstijdfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_bestemmings_Tijd.csv')
    write_csv(PplusRbestemmingstijdtotaal, PplusRbestemmingstijdfilenaam)
    PplusRbestemmingsafstandautofilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_bestemmings_Afstand_Auto.csv')
    write_csv(PplusRbestemmingsafstandautototaal, PplusRbestemmingsafstandautofilenaam)
    PplusRbestemmingsafstandOVfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_bestemmings_Afstand_OV.csv')
    write_csv(PplusRbestemmingsafstandOVtotaal, PplusRbestemmingsafstandOVfilenaam)
    PplusRherkomsttijdfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_herkomst_Tijd.csv')
    write_csv(PplusRherkomsttijdtotaal, PplusRherkomsttijdfilenaam)
    PplusRherkomstafstandautofilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_herkomst_Afstand_Auto.csv')
    write_csv(PplusRherkomstafstandautototaal, PplusRherkomstafstandautofilenaam)
    PplusRherkomstafstandOVfilenaam = os.path.join(Skimsdirectory, f'PplusR_{Hubsetnaam}_herkomst_Afstand_OV.csv')
    write_csv(PplusRherkomstafstandOVtotaal, PplusRherkomstafstandOVfilenaam)
    Pplusfietstijdfilenaam = os.path.join(Skimsdirectory,f'Pplusfiets_{Hubsetnaam}_Tijd.csv')
    write_csv(PplusFietstijdtotaal, Pplusfietstijdfilenaam)
    Pplusfietsautoafstandfilenaam = os.path.join(Skimsdirectory,f'Pplusfiets_{Hubsetnaam}_Afstand_Auto.csv')
    write_csv(PplusFietsautoafstandtotaal, Pplusfietsautoafstandfilenaam)
    Pplusfietshubplekfilenaam = os.path.join(Skimsdirectory,f'Pplusfiets_{Hubsetnaam}_bestehubs.csv')
    write_csv(Pplusfietshubplek, Pplusfietshubplekfilenaam)
    PplusRhubplekfilenaam = os.path.join(Skimsdirectory,f'PplusR_{Hubsetnaam}_bestehubs.csv')
    write_csv(PplusRhubplek, PplusRhubplekfilenaam)


if __name__ == "__main__":
    skims_directory = pathlib.Path(ask_user_for_skims_directory())
    hubs = ask_user_for_hubs()
    hub_name = ask_user_for_hub_name()
    transfer_times = ask_user_for_transfer_times()
    chain_generator(skims_directory, hub_name, hubs, *transfer_times)
