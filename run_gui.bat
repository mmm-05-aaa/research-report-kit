@echo off
setlocal
set PYTHONPATH=
set PYTHONHOME=
cd /d "%~dp0"

py -3 -m reportkit.gui 2>nul
if %ERRORLEVEL% EQU 0 exit /b 0

python -m reportkit.gui
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Could not start Data Quality Inspector.
  echo Install Python 3.10 or newer, then try again.
  pause
  exit /b 1
)