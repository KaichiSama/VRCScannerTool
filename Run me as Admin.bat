@echo off
setlocal enabledelayedexpansion

rem Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installé. Veuillez l'installer et réessayer.
    pause
    exit /b
)

rem Vérifier si les modules Python requis sont installés
python -c "import pkg_resources" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installation des dépendances Python en cours...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Une erreur s'est produite lors de l'installation des dépendances Python.
        pause
        exit /b
    )
    echo Installation des dépendances Python terminée avec succès.
)

rem Lancer le script Python
python VRChatScanner.py

rem Pause pour afficher les résultats (vous pouvez le supprimer si vous le souhaitez)
pause
