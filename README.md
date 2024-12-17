# scripts

## IKOB - Integrale Kijk Op Bereikbaarheid

TODO: Introductie

## Installation and usage

The next section illustrates two approaches of setting up IKOB on your machine.
The first method relies on helper scripts provided in [`scripts`](scripts/),
while the second method follows a manual installation approach. 

> [!IMPORTANT]
> Before proceeding make sure [Python](https://www.python.org/) is installed on the system.
> IKOB supports versions 3.12.x and 3.13.1 (or newer).
> For Windows users relying on Python installers, make sure to enable the checkbox `"Add python.exe to PATH"` during installation.

> [!CAUTION]
> There is a known issue when working with Python version **3.13.0** (see [#74](https://github.com/Stichting-CROW/ikob/issues/74)).
> Users should therefore use for versions **3.12.x** or **>= 3.13.1**.

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
outlined in the [#Installation-and-usage] section. This should provide a
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

The current CI pipelines enforce code formatting through `autopep8` and `isort`. To ensure modified sources files adhere to the requirements of these linters, run

```sh
isort src/ikob/*.py tests/*.py
autopep8 --in-place --aggressive --aggressive src/ikob/*.py tests/*.py
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
