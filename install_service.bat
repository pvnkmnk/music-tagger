@echo off
echo Music Tagger Service Installer
echo ============================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script requires administrator privileges.
    echo Please right-click on this file and select "Run as administrator".
    pause
    exit /b 1
)

echo Installing required dependencies...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Installing Music Tagger service...
python music_tagger_service.py install
if %errorLevel% neq 0 (
    echo Error: Failed to install service.
    pause
    exit /b 1
)

echo.
echo Starting Music Tagger service...
python music_tagger_service.py start
if %errorLevel% neq 0 (
    echo Error: Failed to start service.
    pause
    exit /b 1
)

echo.
echo Music Tagger service has been installed and started successfully.
echo The service will automatically start when Windows boots.
echo.
echo You can check the service status in Windows Services manager
echo or by using these commands:
echo.
echo   python music_tagger_service.py status
echo   python music_tagger_service.py stop
echo   python music_tagger_service.py restart
echo.
echo Activity logs can be found in: music_tagger_service.log
echo.
pause
