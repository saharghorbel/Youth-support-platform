@echo off
echo ========================================
echo   Multiplying Dataset
echo ========================================
echo.

call .\venv\Scripts\activate.bat

echo Generating batch 1...
python generate_sample_data.py

echo.
echo Generating batch 2...
python generate_sample_data.py

echo.
echo Generating batch 3...
python generate_sample_data.py

echo.
echo Generating batch 4...
python generate_sample_data.py

echo.
echo Generating batch 5...
python generate_sample_data.py

echo.
echo ========================================
echo   Dataset Multiplication Complete!
echo ========================================
echo.

python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings'); import django; django.setup(); from education.models import Student; from health.models import Patient; print(f'\nFinal Counts:'); print(f'  Students: {Student.objects.count()}'); print(f'  Patients: {Patient.objects.count()}')"

echo.
pause
