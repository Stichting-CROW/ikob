import pathlib
import shutil

from test_end_to_end import compare_directories

from ikob.chain_generator import chain_generator


def test_chain_generator(tmpdir):
    reference_dir = pathlib.Path("tests/chains/reference")
    skims_dir = pathlib.Path("tests/chains/restdag")
    result_dir = pathlib.Path(tmpdir) / "restdag"

    # Copy skims file into temporary dir
    shutil.copytree(skims_dir, result_dir, dirs_exist_ok=True)

    # Generate results
    hubs = [35, 40, 94, 105, 134, 153, 184, 193, 204, 249, 288]
    name = "Masterplan_hubset"
    transfer_time_pt = 8
    transfer_time_bike = 5

    chain_generator(result_dir,
                    name, hubs,
                    transfer_time_pt, transfer_time_bike)

    # Since output files are written back to input directory, the remaining
    # input files are removed before comparing output files with references.
    files_to_ignore_during_comparison = [
        "Auto_Afstand.csv",
        "Auto_Tijd.csv",
        "Fiets_Tijd.csv",
        "OV_Afstand.csv",
        "OV_Tijd.csv",
    ]
    for filename in files_to_ignore_during_comparison:
        (result_dir / filename).unlink()

    assert compare_directories(result_dir, reference_dir)
