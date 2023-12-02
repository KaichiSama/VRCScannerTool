@echo off
rem Get the path to the Python interpreter from the Microsoft Store
for /f "tokens=*" %%i in ('where python') do set "python_exe=%%i"

rem Check if the Python interpreter is available
if "%python_exe%"=="" (
    echo Python interpreter not found. Make sure it is installed.
    pause
    exit /b
)

rem Find the directory path of the .bat script
set "script_dir=%~dp0"

rem Install required dependencies if not already installed
echo Installing dependencies...
pip install colorama requests keyboard vrchatapi pyfiglet UnityPy

rem Check if any of the required packages failed to install
if %errorlevel% neq 0 (
    echo Failed to install one or more required packages. Check the error messages above.
    pause
    exit /b
)

rem Search for a .py file in the same directory as the .bat script
for %%f in ("%script_dir%*.py") do (
    echo Running Python script: %%f
    "%python_exe%" "%%f"
)

rem Pause to keep the console open after execution
pause
