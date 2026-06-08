@echo off
echo ========================================
echo Youth Support Platform - Status Check
echo ========================================
echo.

echo Checking Python installation...
py --version
echo.

echo Checking virtual environment...
if exist venv\Scripts\activate.bat (
    echo [OK] Virtual environment found
) else (
    echo [ERROR] Virtual environment not found
)
echo.

echo Checking database...
if exist db.sqlite3 (
    echo [OK] Database file exists
) else (
    echo [WARNING] Database file not found - run reset_db.bat
)
echo.

echo Checking migrations folders...
if exist accounts\migrations (
    echo [OK] accounts/migrations exists
) else (
    echo [ERROR] accounts/migrations not found
)

if exist education\migrations (
    echo [OK] education/migrations exists
) else (
    echo [ERROR] education/migrations not found
)

if exist health\migrations (
    echo [OK] health/migrations exists
) else (
    echo [ERROR] health/migrations not found
)
echo.

echo Checking logs folder...
if exist logs (
    echo [OK] logs folder exists
) else (
    echo [ERROR] logs folder not found
)
echo.

echo Activating virtual environment and checking Django...
call venv\Scripts\activate.bat
py -m django --version 2>nul
if %errorlevel% equ 0 (
    echo [OK] Django is installed
) else (
    echo [ERROR] Django not found - run: pip install -r requirements.txt
)
echo.

echo ========================================
echo Status check complete!
echo ========================================
echo.
echo Next steps:
echo 1. If database not found: run reset_db.bat
echo 2. If Django not installed: run pip install -r requirements.txt
echo 3. If everything OK: run start.bat
echo.
pause
