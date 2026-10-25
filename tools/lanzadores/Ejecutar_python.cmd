@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0..\.."
set "ENVOLVENTES_ROOT=%CD%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONIOENCODING=utf-8"
set "TEMP=%ENVOLVENTES_ROOT%\.runtime\tmp"
set "TMP=%TEMP%"
if exist "%ENVOLVENTES_ROOT%\.venv\Scripts\python.exe" (
  "%ENVOLVENTES_ROOT%\.venv\Scripts\python.exe" -B %*
  exit /b !errorlevel!
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -B %*
  exit /b !errorlevel!
)
python -B %*
