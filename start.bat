@echo off
echo ========================================
echo Youth Support Platform - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    py -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show django >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if database exists
if not exist "db.sqlite3" (
    echo Setting up database...
    py setup.py
    echo.
)

REM Start the server
echo ========================================
echo Starting Django development server...
echo ========================================
echo.
echo Dashboard: http://127.0.0.1:8000/
echo Admin Panel: http://127.0.0.1:8000/admin/
echo API Docs: http://127.0.0.1:8000/api/docs/
echo.
echo Login credentials:
echo   admin / admin123 (Admin)
echo   supervisor1 / super123 (Supervisor)
echo   operator1 / oper123 (Operator)
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

py manage.py runserver
