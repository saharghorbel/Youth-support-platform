@echo off
chcp 65001 >nul
echo ========================================
echo   CREATION DU ZIP POUR L'EXAMEN
echo ========================================
echo.

cd /d "%~dp0"
cd ..

set "zipName=Youth_Support_Platform_Exam.zip"

if exist "%zipName%" (
    echo Suppression de l'ancien ZIP...
    del "%zipName%"
)

echo Creation du ZIP...
echo Cela peut prendre quelques instants...
echo.

powershell -Command "Compress-Archive -Path 'django\*' -DestinationPath '%zipName%' -Force -CompressionLevel Optimal"

if exist "%zipName%" (
    echo.
    echo ========================================
    echo   ZIP CREE AVEC SUCCES!
    echo ========================================
    echo.
    echo Fichier: %zipName%
    for %%A in ("%zipName%") do echo Taille: %%~zA bytes
    echo.
    echo ATTENTION: Le ZIP contient TOUT (y compris venv/)
    echo.
    echo Pour reduire la taille, supprimez manuellement:
    echo   - Le dossier venv/
    echo   - Les dossiers __pycache__/
    echo.
    echo Mais GARDEZ:
    echo   - db.sqlite3 (base de donnees)
    echo   - README.md
    echo   - Tous les autres fichiers
    echo.
    echo Le ZIP est dans: %CD%
    echo.
) else (
    echo ERREUR: Impossible de creer le ZIP
)

pause
