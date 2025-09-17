@echo off
echo YouTube Downloader - Building Executable
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run the build script
echo Building executable...
python build_executable.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable is located in the 'dist' folder
echo.
pause
