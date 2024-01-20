@echo off
setlocal enabledelayedexpansion

rem Check if Python is installed
python3 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install it and try again.
    echo Download Python by pressing Enter.
    pause >nul
    start "" "https://apps.microsoft.com/detail/9NRWMJP3717K?hl=fr-ca&gl=US"
    exit /b
)

rem Check if the required Python modules are installed
python -c "import pkg_resources" >nul 2>&1
if %errorlevel% neq 0 (
    echo An error occurred while checking for pkg_resources.
    pause
    exit /b
)

rem Install Python dependencies one by one from requirements.txt
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo An error occurred during the installation of the dependencies.
    pause
    exit /b
)

echo All Python dependencies have been successfully installed.

rem Launch the Python script
python VRChatScanner.py

rem Pause to display results (you can remove this if you wish)
pause