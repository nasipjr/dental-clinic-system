@echo off
title Dental Clinic MS - Build Windows App
echo =======================================================
echo   Dental Clinic Management System - Build Script
echo =======================================================
echo.

if exist "venv\Scripts\python.exe" (
    set PYCMD="venv\Scripts\python.exe"
) else (
    set PYCMD=python
)

echo [1/2] Checking packager dependencies...
%PYCMD% -m pip install pyinstaller pywebview

echo.
echo [2/2] Building standalone EXE application...
%PYCMD% -m PyInstaller "Clinic MS.spec" --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed! Check error details above.
) else (
    echo.
    echo =======================================================
    echo   BUILD COMPLETED SUCCESSFULLY!
    echo   Target location: dist\Clinic MS.exe
    echo =======================================================
)
pause
