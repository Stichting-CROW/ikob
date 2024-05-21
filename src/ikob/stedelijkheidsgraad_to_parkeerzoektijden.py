from ikob.Routines import csvintlezen, csvwegschrijven
import logging
import pathlib
import sys
from tkinter import filedialog


logger = logging.getLogger(__name__)


def stedelijkheid_to_parkeerzoektijden(infile: pathlib.Path, outfile: pathlib.Path):
    stedelijkheidsgraad = csvintlezen(infile)
    header = ["Zone", "AankomstZT", "VertrekZT"]

    # TODO: This conversion is missing documentation. Why these values?
    omzetting = {1: 12, 2: 8, 3: 4, 4: 0, 5: 0}

    parkeerzoektijden = []
    for i, sg in enumerate(stedelijkheidsgraad):
        parkeerzoektijden.append([i + 1, omzetting[sg], round(omzetting[sg] / 4)])

    csvwegschrijven(parkeerzoektijden, outfile, header)
    logger.info("Converted: '%s' to '%s.csv'", infile, outfile)


# TODO: Remove script interface once conversion is embedded within GUI.
if __name__ == "__main__":
    if len(sys.argv) == 1:
        infile = filedialog.askopenfilename(title="Selecteer de Stedelijkheidsfile")
        infile = infile.replace(".csv", "")
    else:
        infile = sys.argv[1]

    infile = pathlib.Path(infile)
    outfile = pathlib.Path(infile.parent / "Parkeerzoektijd")
    stedelijkheid_to_parkeerzoektijden(infile, outfile)
