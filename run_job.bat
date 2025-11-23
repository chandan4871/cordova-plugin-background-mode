@echo off
REM ========================================================================
REM Infrastructure Tagging Summary Generation - Windows Batch Script
REM ========================================================================
REM 
REM This batch file runs the infrastructure tagging summary generation
REM using the Python script. Edit the variables below to match your setup.
REM
REM Usage: run_job.bat
REM ========================================================================

echo ========================================================================
echo Infrastructure Tagging Summary Generation
echo ========================================================================
echo.

REM ========================================================================
REM CONFIGURATION - Edit these variables
REM ========================================================================

REM Path to Python executable (ArcGIS Pro Python)
SET PYTHON_EXE=C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe

REM Path to the script directory
SET SCRIPT_DIR=%~dp0

REM Configuration file path (relative to script directory)
SET CONFIG_FILE=%SCRIPT_DIR%config.json

REM Alternatively, you can specify connection details directly here:
REM SET CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DB;Trusted_Connection=yes;
REM SET SCHEMA_NAME=dbo

REM ========================================================================
REM END CONFIGURATION
REM ========================================================================

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python executable not found at: %PYTHON_EXE%
    echo Please update PYTHON_EXE variable in this batch file.
    echo.
    pause
    exit /b 1
)

REM Check if config file exists
if not exist "%CONFIG_FILE%" (
    echo ERROR: Configuration file not found at: %CONFIG_FILE%
    echo Please create config.json or update CONFIG_FILE variable.
    echo.
    pause
    exit /b 1
)

REM Run the script
echo Starting job...
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%run_infratagging_job.py" --config "%CONFIG_FILE%"

REM Capture exit code
SET EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================================================
if %EXIT_CODE% EQU 0 (
    echo Job completed successfully!
) else (
    echo Job failed with exit code: %EXIT_CODE%
)
echo ========================================================================
echo.

REM Uncomment the line below if you want the window to stay open
REM pause

exit /b %EXIT_CODE%
