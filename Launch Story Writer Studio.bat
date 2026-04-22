@echo off
setlocal

REM Always run from this file's folder so the user never needs to cd first.
cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py"

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo Python was not found on this computer.
    echo.
    echo Install Python from https://www.python.org/downloads/
    echo and make sure "Add python.exe to PATH" is enabled during install.
    echo.
    pause
    exit /b 1
)

"%PYTHON_CMD%" story_writer_studio.py
set "STUDIO_EXIT_CODE=%ERRORLEVEL%"

if not "%STUDIO_EXIT_CODE%"=="0" (
    echo.
    echo The story writer studio closed with an error.
    echo If this is your first time using it, install the SDK with:
    echo     pip install openai
    echo.
    pause
)

exit /b %STUDIO_EXIT_CODE%
