from ikob.Routines import csvintlezen, csvwegschrijven
import logging
import pathlib
import sys
from tkinter import filedialog


logger = logging.getLogger(__name__)


def stedelijkheid_to_parkeerzoektijd(stedelijkheidsgraad: [int]) -> [[int]]:
    # TODO: This conversion is missing documentation. Why these values?
    omzetting = {1: 12, 2: 8, 3: 4, 4: 0, 5: 0}

    parkeerzoektijden = []
    for i, sg in enumerate(stedelijkheidsgraad):
        aankomst = omzetting[sg]
        vertrek = round(omzetting[sg] / 4)
        parkeerzoektijden.append([i + 1, aankomst, vertrek])

    return parkeerzoektijden


def stedelijkheidfile_to_parkeerzoektijdenfile(
    infile: pathlib.Path, outfile: pathlib.Path
):
    logger.info("Converting: '%s' to '%s.csv'", infile, outfile)
    stedelijkheidsgraad = csvintlezen(infile)
    parkeerzoektijden = stedelijkheid_to_parkeerzoektijd(stedelijkheidsgraad)

    header = ["Zone", "AankomstZT", "VertrekZT"]
    csvwegschrijven(parkeerzoektijden, outfile, header=header)


# TODO: Remove script interface once conversion is embedded within GUI.
if __name__ == "__main__":
    if len(sys.argv) == 1:
        infile = filedialog.askopenfilename(title="Selecteer de Stedelijkheidsfile")
        infile = infile.replace(".csv", "")
    else:
        infile = sys.argv[1]

    infile = pathlib.Path(infile)
    outfile = pathlib.Path(infile.parent / "Parkeerzoektijd")
    stedelijkheidfile_to_parkeerzoektijdenfile(infile, outfile)
