@echo off
echo ================================================================================
echo  RESETTING DATABASE AND MIGRATIONS
echo  Youth Support Platform - SESAME University
echo ================================================================================
echo.

REM Stop any running Django server
echo [1/7] Stopping any running Django server...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM Delete SQLite database
echo [2/7] Deleting SQLite database...
if exist db.sqlite3 (
    del /F /Q db.sqlite3
    echo Database deleted.
) else (
    echo No database found.
)
echo.

REM Delete all migration files except __init__.py
echo [3/7] Deleting migration files...
for /d %%D in (accounts education health dashboard core ai_engine) do (
    if exist %%D\migrations (
        echo Cleaning %%D\migrations...
        for %%F in (%%D\migrations\*.py) do (
            if not "%%~nxF"=="__init__.py" (
                del /F /Q "%%F"
            )
        )
        for %%F in (%%D\migrations\*.pyc) do (
            del /F /Q "%%F"
        )
        if exist %%D\migrations\__pycache__ (
            rmdir /S /Q %%D\migrations\__pycache__
        )
    )
)
echo Done.
echo.

REM Activate virtual environment and run migrations
echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [5/7] Creating new migrations...
python manage.py makemigrations accounts
python manage.py makemigrations education
python manage.py makemigrations health
python manage.py makemigrations dashboard
python manage.py makemigrations core
python manage.py makemigrations ai_engine
echo.

echo [6/7] Applying migrations...
python manage.py migrate
echo.

echo [7/7] Setting up demo data...
python manage.py setup_demo
echo.

echo ================================================================================
echo  DATABASE RESET COMPLETE!
echo ================================================================================
echo.
echo You can now run the server with:
echo   python manage.py runserver
echo.
echo Login credentials:
echo   Admin:      admin / admin123
echo   Counselor:  counselor / counsel123
echo   Teacher:    teacher / teach123
echo.
echo Server URL: http://127.0.0.1:8000/
echo ================================================================================
pause
