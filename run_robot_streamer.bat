@echo off
echo Activating virtual environment and starting robot streamer...
echo.

call .venv\Scripts\activate.bat
python robot_streamer.py

pause