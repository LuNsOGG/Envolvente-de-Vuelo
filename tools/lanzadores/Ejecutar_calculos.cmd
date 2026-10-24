@echo off
cd /d "%~dp0..\.."
call "%~dp0Ejecutar_python.cmd" main.py --project data/proyecto_inicial.json --all
pause
