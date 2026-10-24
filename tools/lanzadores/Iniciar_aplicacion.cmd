@echo off
cd /d "%~dp0..\.."
call "%~dp0Ejecutar_python.cmd" main.py
if errorlevel 1 pause
