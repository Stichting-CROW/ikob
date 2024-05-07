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
