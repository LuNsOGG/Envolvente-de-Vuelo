@echo off
cd /d "%~dp0..\.."
call "%~dp0Ejecutar_python.cmd" tools/run_tests.py
pause
