@echo off
echo Music Tagger Background Launcher
echo ================================

:: Find pythonw.exe
SET PYTHONW=

:: Try standard installation paths
IF EXIST "C:\Python313\pythonw.exe" SET PYTHONW="C:\Python313\pythonw.exe"
IF EXIST "C:\Program Files\Python313\pythonw.exe" SET PYTHONW="C:\Program Files\Python313\pythonw.exe"

:: Check the user's PATH for python
FOR /F "tokens=*" %%i IN ('where python 2^>nul') DO SET PYTHON_PATH=%%i
IF DEFINED PYTHON_PATH (
    SET PYTHON_DIR=%PYTHON_PATH:~0,-10%
    IF EXIST "%PYTHON_DIR%pythonw.exe" SET PYTHONW="%PYTHON_DIR%pythonw.exe"
)

:: If pythonw wasn't found, try regular python
IF NOT DEFINED PYTHONW (
    echo Warning: pythonw.exe not found. Falling back to python.exe
    SET PYTHONW=python
)

echo Using Python: %PYTHONW%
echo Starting Music Tagger in background mode...

:: Run the background script
start "Music Tagger Background" /MIN %PYTHONW% "%~dp0music_tagger_background.pyw"

echo Music Tagger is now running in the background.
echo Activity logs can be found in: music_tagger_background.log

:: Check if it started correctly by looking for log file updates
timeout /t 3 >nul
echo.
echo Checking if the application started correctly...
IF EXIST "%~dp0music_tagger_background.log" (
    echo Log file found. Application appears to have started.
) ELSE (
    echo Warning: Log file not found. The application may not have started correctly.
    echo Try running: python music_tagger_background.pyw
    echo to see any error messages.
)

pause
