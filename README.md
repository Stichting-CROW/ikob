# scripts

## IKOB - Integrale Kijk Op Bereikbaarheid

TODO: Introductie

## Hoe te gebruiken

## Installation

Create and activate a virtual environment:

```sh
python3 -m venv venv
. venv/bin/activate
```

Install IKOB within virtual environment:

```sh
# For normal use
pip install .

# For development with development dependencies
pip install -e .[dev]
```

Running tests:

```sh
python3 -m pytest
```

Running tests with direct logging:
```sh
# log_file_level=error,warning,info,debug
python -m pytest -o log_cli=true -o log_file_level=info
```

Reformatting source code using `ruff`:

```sh
ruff format path/to/source.py
```

## Deployment

The Windows application can be build using [`PyInstaller`](https://pyinstaller.org/en/stable/index.html),
which is defined as a deployment dependency, i.e. `pip install -e .[deploy]`. The Windows executable
must be generated on Windows and can be done through running the following commands through powershell.

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
