@echo off
title Dental Clinic MS Flask
cd /d "%~dp0"
echo Starting Dental Clinic MS Flask...
start http://127.0.0.1:5000
venv\Scripts\python.exe app.py
pause
