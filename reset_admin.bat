@echo off
title Reset Admin Password - Dental Clinic MS
echo ===================================================
echo   Dental Clinic MS - Emergency Admin Password Reset
echo ===================================================
echo.
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe reset_admin_password.py %1
) else (
    python reset_admin_password.py %1
)
echo.
pause
