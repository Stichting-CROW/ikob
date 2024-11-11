@echo off

set venvdir=venv

:: Move to the root directory of IKOB.
cd %~dp0\..

:: Ensure the virtual environment is activated.
if exist %venvdir% (
    call %venvdir%\Scripts\activate.bat
) else (
    goto :VIRTUALENV_NOT_PRESENT
)

:: Launch the config GUI.
python src\ikob\ikobrunner.py --verbose
goto :DONE

:VIRTUALENV_NOT_PRESENT
echo No virtual environment '%venvdir%' was found.
echo Please configure IKOB first using "setup.bat".

:: Keep the prompt open.
:DONE
echo Press any key to close.
pause >nul
exit
