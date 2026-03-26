# scripts

## IKOB - Integrale Kijk Op Bereikbaarheid

IKOB is an acronym for the Dutch term **Integrale Kijk Op Bereikbaarheid** which is best translated as **Integrative Takes On Accessibility**.
This software is meant to quickly assess the potential accessibility of amenities, stratified among groups within society. At this moment, it is based on datasets from Statistics Netherlands at the level of neighborhoods for input data.
This data is used to create accessibility profiles for several groups within society, so that their particular 'potential accessibility' can be assessed. For this, publicly available data for travel times for different transport modes are used, based on common (Dutch) transport models, such as LMS.
Potential accessibility is calculated in analogy with [Hansen (1958)](https://www.tandfonline.com/doi/abs/10.1080/01944365908978307 "Subscription needed"). It uses distance decay curves for each mode, based on time and cost (perception) by each group in society.
So, the further away an amenity (like a job location) is, the less it will count as a full option. The calculated potential accessibility, therefore, is a weighted amount.

### Nomenclature

Some commonly used abbreviations / jargon:
- TVOM: Time value of money, how much money a unit of time is worth.  
  Used to combine both travel time and travel costs into a single metric.
- SEGS: Sociaal-economische gegevens (Social-Economic data).  
  For example: Shops per zone, working population per zone, etc.
- skims: Data to determine an impedance ('friction') matrix from zone to zone.  
  For example: A matrix of distances via car from zone to zone, costs per kilometer of traveling by car, etc.
- GTR: Generalized travel time
- ICE: Internal combustion engine. Also referred to using fuel_kind 'fossiel'. 
- vk: (dutch) voorkeur / (english) preference
- groups: See [Groups](./README.md#groups)

In the past, IKOB was focussed on commuting trips. You might see this reflected in nomenclature where terms like 'employment', 'jobs' are used to indicate the traveling population and their destinations.
Ikob since has been generalized to allow for different motives, but you might see this remnants of this old approach. 

## Installation and usage

The next section illustrates two approaches of setting up IKOB on your machine.
The first method relies on helper scripts provided in [`scripts`](scripts/),
while the second method follows a manual installation approach.

> [!IMPORTANT]
> Before proceeding make sure [Python](https://www.python.org/) is installed on the system.
> IKOB supports versions 3.13.1 and newer.
> For Windows users relying on Python installers, make sure to enable the checkbox `"Add python.exe to PATH"` during installation.

### Using helper scripts

First obtain a copy of the source code by cloning the repository available at
[https://github.com/Stichting-CROW/ikob](github.com/Stichting-CROW/ikob). For
more information how to "clone" a repository, please consider the documentation
provided by GitHub: [Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

Use the file explorer to navigate to the directory containing the IKOB source
code. Then run the setup script: [`scripts/setup.bat`](scripts/setup.bat). This
opens a CMD prompt showing the installation process. If all goes well, IKOB is
successfully installed after running this script.

To run IKOB and use the `ikobconfig.py` `ikobrunner.py` user interfaces, two
additional scripts are provided, respectively
[`scripts/ikobconfig.bat`](scripts/ikobconfig.bat) and
[`scripts/ikobrunner.bat`](scripts/ikobrunner.bat). Running either script
should launch the corresponding IKOB GUI, leveraging the local installation
created during the previously step `scripts/setup.bat`.

### Manual installation

> [!NOTE]
> The manual installation assumes basic familiarity with Git and Python.

Obtain a copy of the source code by cloning the repository:

```sh
git clone https://github.com/Stichting-CROW/ikob
```

Create and activate a local virtual environment:

```sh
python3 -m venv venv
. venv/bin/activate
```

Then install IKOB with its dependencies:

```sh
pip install .
```

If you intend to install IKOB for development, or if you like to run the
existing IKOB test suite, then consider to install the development dependencies
too:

```sh
pip install -e .[dev]
```

To run IKOB and use the `ikobconfig.py` and `ikobrunner.py` user interfaces,
the GUIs can be launched by running the following commands within the activated
virtual environment:

```sh
# Ensure the virtual environment is activated.
. venv/bin/activate

# Run ikobconfig
python src/ikob/ikobconfig.py

# Run ikobrunner
python src/ikob/ikobrunner.py
```

## Development

For IKOB development first install IKOB following the manual installation
outlined in the [Installation and usage](#installation-and-usage) section. This should provide a
local, editable installation of IKOB. To verify all is setup well, you
can run the IKOB test suite through `pytest`.

```sh
python3 -m pytest
```

To enable logger output:

```sh
# log_file_level=error,warning,info,debug
python -m pytest -o log_cli=true -o log_file_level=info
```

The current CI pipelines enforce code formatting through `ruff`.
To ensure modified sources files adhere to the requirements of these linters, run

```sh
python -m ruff check
```

## Deployment

The Windows application can be build using
[`PyInstaller`](https://pyinstaller.org/en/stable/index.html), which is defined
as a deployment dependency, i.e. `pip install -e .[deploy]`. The Windows
executable must be generated on Windows and can be done through running the
following commands through powershell.

```powershell
# Setup and activate the virtual environment
python3 -m venv venv
. .\venv\Scripts\Activate.ps1

# Install development and deployment dependencies
python -m pip install -e .[dev,deploy]

# Verify ikob passes tests
python -m pytest

# Generate executable
pyinstaller --clean --onefile --windowed .\ikob\ikobrunner.py
```

This generates build artefacts under `build` and the bundled, distributable
application under `dist/ikob`. This directory contains the executable as
`dist/ikobrunner/ikobrunner.exe` with a corresponding set of "internal" files
in `dist/ikobrunner/_internal`. The full directory, i.e. `dist/ikobrunner` is
self contained and can be moved to the desired location. Running the executable
will run the typical `ikobrunner` script.

# Testing

## Test Types

- **Unit tests** (`tests/unit/`) - Test individual components using toy examples and monkey patching
- **E2E tests** (`tests/e2e/`) - Run the full ikobrunner script end-to-end

The remaining folders contain test projects and reference output.

## Reference Tests

There are some reference tests:
- tests/e2e/test_end_to_end.py
- tests/unit/test_chain_generator.py
- tests/unit/test_parking_cost_file.py
- tests/unit/test_group_distribution.py

These compare current output against stored reference output.
These detect when output has changed but don't verify expected behavior. 

To generate new reference data for these tests it's easiest to just run the test without deleting the computed results at the end. In general this boils down to removing the `remove_directory` call. If the test uses a [temporary test directory](https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture) or something similar, it's easiest to make that a concrete path and get the results from there. 

# Output

See OUTPUT.md for the structure of the output (results) directory. This file is also included in the output directory produced by the code.

# Groups 

The code uses the term 'groups' a lot to refer to different slices of the population. Income groups (income classes) are different from groups. 

The code uses the following income classes:
- low
- medium-low
- medium-high
- high

The groups are there to differentiate slices of the population with different modalities at their disposal and with different preferences.\
The code uses the following groups:
| Group | Description |
|---|---|
| GratisAuto | Those with a free car |
| GratisAuto_GratisOV | Those with a free car and free public transport |
| WelAuto_GratisOV | Those with a car and free public transport |
| WelAuto_vkAuto | Those with a car and a preference for car |
| WelAuto_vkNeutraal | Those with a car and a neutral preference |
| WelAuto_vkFiets | Those with a car and a preference for cycling |
| WelAuto_vkOV | Those with a car and a preference for public transport |
| GeenAuto_GratisOV | Those without a car and free public transport |
| GeenAuto_vkNeutraal | Those without a car and a neutral preference |
| GeenAuto_vkFiets | Those without a car and a preference for cycling |
| GeenAuto_vkOV | Those without a car and a preference for public transport |
| GeenRijbewijs_GratisOV | Those without a driver’s license and free public transport |
| GeenRijbewijs_vkNeutraal | Those without a driver’s license and a neutral preference |
| GeenRijbewijs_vkFiets | Those without a driver’s license and a preference for cycling |
| GeenRijbewijs_vkOV | Those without a driver’s license and a preference for public transport |

Where each group is additionally suffixed by an income class to split the population up further.\
In [distribute_over_groups.py](./src/ikob/distribute_over_groups.py) the population of each zone is distributed over these groups according to social-economic data.
# Motieven 

A run of ikob is always for a specific travel motive. In the project config you can configure the name of the motive, the corresponding traveling population and the destinations corresponding to the travel motive. In addition, it's also possible to configure the time value of money used for the motive, and the travel time decay curve to use.

When you run ikob for multiple different motives in sequence, the results are separated in the results directory (generally by a subdirectory with the motive name). 
