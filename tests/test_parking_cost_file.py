import pathlib

from test_end_to_end import compare_directories, remove_directory

from ikob.ikobrunner import run_scripts


def test_config_with_parking_cost_file():
    case = "vlaanderen-with-parking-cost"
    test_dir = pathlib.Path("tests")
    project_dir = test_dir.joinpath(case).resolve()
    project = project_dir.joinpath(f"{case}.json")

    # Check if the first step runs OK with parking file provided.
    skip_steps = [True] * 8
    skip_steps[0] = False
    run_scripts(project, skip_steps=skip_steps, write_weights=False)

    dir_to_compare = "basis/werk/ervarenreistijd"
    reference_dir = project_dir / "reference" / dir_to_compare
    result_dir = project_dir / f"{case}" / dir_to_compare
    assert compare_directories(result_dir, reference_dir)

    # Clean up files if test succeeds
    remove_directory(result_dir)
