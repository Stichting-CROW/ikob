@echo off

:: The name for the virtual environment directory.
set venvdir=venv

:: Check for Python installation.
python --version 2>NUL || (goto :PYTHON_NOT_PRESENT)

:: Move to the root directory of IKOB.
cd %~dp0\..

:: Warning if the virtual env directory is already present.
if exist %venvdir% (
    goto :VIRTUALENV_ALREADY_PRESENT
) else (
    python -m venv %venvdir%
    echo Configured virtual environment '%venvdir%'.
)

:: Activate virtual environment.
call %venvdir%\Scripts\activate.bat

:: Package setup and configuration.
echo Installing IKOB and its dependencies.
pip install -e .[dev] || (goto :PIP_INSTALL_FAILED)

echo Successfully installed IKOB.
goto :DONE

:VIRTUALENV_ALREADY_PRESENT
echo The virtual environment '%venvdir%' is already present.
echo Please remove virtual environment '%venvdir%' and start fresh.
goto :DONE

:PYTHON_NOT_PRESENT
echo The Python executable is not found on your system.
echo Please make sure that Python is installed.
echo See "https://www.python.org/downloads/windows".
goto :DONE

:PIP_INSTALL_FAILED
echo Installing IKOB and its dependencies failed.

:: Keep the prompt open.
:DONE
echo Press any key to close.
pause >nul
exit
