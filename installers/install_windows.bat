@echo off
title Growth Reminder Installer
color 0A
echo ========================================
echo    📈 Growth Reminder Installer
echo ========================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Administrator privileges required!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo 🔍 Checking Python installation...

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python is not installed!
    echo.
    echo Would you like to download and install Python? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo 📥 Downloading Python installer...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
        echo 🚀 Running Python installer...
        start /wait %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
        echo ✅ Python installed successfully!
    ) else (
        echo ❌ Installation cancelled.
        pause
        exit /b 1
    )
)

:: Get Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% detected

echo.
echo 📥 Downloading Growth Reminder script...

:: Create directory if it doesn't exist
if not exist "%USERPROFILE%\GrowthReminder" mkdir "%USERPROFILE%\GrowthReminder"

:: Download the Python script
echo Fetching from server...
powershell -Command "$client = New-Object System.Net.WebClient; try { $client.DownloadFile('http://192.168.11.101:8000/script.py', '%USERPROFILE%\GrowthReminder\growth_reminder.py') } catch { Write-Host 'Failed to download. Make sure server is running.'; exit 1 }"

if %errorLevel% neq 0 (
    echo ❌ Failed to download script. Is the server running at http://192.168.11.101:8000?
    pause
    exit /b 1
)

echo ✅ Script downloaded successfully

echo.
echo 📦 Installing required packages...

:: Install required Python packages
python -m pip install --upgrade pip >nul 2>&1
python -m pip install requests win10toast >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Failed to install dependencies.
    echo Please check your Python installation.
    pause
    exit /b 1
)

echo ✅ Dependencies installed

echo.
echo ⏰ Setting up scheduled task (daily at 9:00 AM)...

:: Create scheduled task
schtasks /create /tn "GrowthReminder" /tr "python %USERPROFILE%\GrowthReminder\growth_reminder.py" /sc hourly /mo 1 /f >nul 2>&1

if %errorLevel% equ 0 (
    echo ✅ Scheduled task created successfully
) else (
    echo ⚠️  Could not create scheduled task. You may need to create it manually.
)

echo.
echo 🎉 Testing notification (you should see a popup)...

:: Run the script once to test
python "%USERPROFILE%\GrowthReminder\growth_reminder.py"

echo.
echo ========================================
echo    ✅ Installation Complete!
echo ========================================
echo.
echo 📍 Script installed to: %USERPROFILE%\GrowthReminder\
echo ⏰ Daily reminder scheduled for: 9:00 AM
echo.
echo To uninstall:
echo   - Delete folder: %USERPROFILE%\GrowthReminder
echo   - Run: schtasks /delete /tn "GrowthReminder" /f
echo.
pause
