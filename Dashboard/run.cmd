@echo off
rem Starts the progress website from Windows Command Prompt.
rem Open http://127.0.0.1:8080 and press Ctrl+C here to stop the server.
cd /d "%~dp0"
python server.py

