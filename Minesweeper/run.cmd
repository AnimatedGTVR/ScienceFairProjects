@echo off
rem Beginner note: this Windows Command Prompt launcher starts project.py.
rem Example: run.cmd train --episodes 100
cd /d "%~dp0"
python --version >nul 2>nul
if not errorlevel 1 (
  python project.py %*
  exit /b %errorlevel%
)
py -3 --version >nul 2>nul
if errorlevel 1 (
  echo Python 3 was not found. Install Python 3.10 or newer, then try again.
  exit /b 1
)
py -3 project.py %*
