@echo off
echo ========================================
echo Running Tests - Youth Support Platform
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running all tests with coverage...
py manage.py test --verbosity=2

echo.
echo ========================================
echo Test run complete!
echo ========================================
echo.
echo To run specific tests:
echo   py manage.py test accounts
echo   py manage.py test education
echo   py manage.py test health
echo.
pause
