@echo off
echo ============================================
echo   Youth Support Platform - Reset Users
echo ============================================
echo.

call .\venv\Scripts\activate.bat
python reset_users.py

echo.
echo ============================================
echo Press any key to exit...
pause > nul
