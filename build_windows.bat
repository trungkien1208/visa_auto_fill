@echo off
REM Windows build script for Visa GUI Application
REM This batch file automates the build process on Windows

echo ========================================
echo Visa GUI Application - Windows Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/downloads/windows/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

REM Install/upgrade required packages
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Install PyInstaller if not present
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install Playwright if not present  
echo Checking Playwright...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo Installing Playwright...
    pip install playwright
)

REM Ask user if they want to install browsers
echo.
set /p install_browsers=Install/update Playwright browsers? (y/N): 
if /i "%install_browsers%"=="y" (
    echo Installing Playwright browsers...
    python -m playwright install chromium
    if errorlevel 1 (
        echo WARNING: Browser installation failed, but continuing...
    ) else (
        echo Browsers installed successfully!
    )
)

REM Build the application
echo.
echo ========================================
echo Building application...
echo ========================================

REM Check if spec file exists
if not exist "visa_gui_windows.spec" (
    echo ERROR: visa_gui_windows.spec not found!
    echo Make sure you're running this from the project directory.
    pause
    exit /b 1
)

REM Clean build
echo Building with PyInstaller...
pyinstaller visa_gui_windows.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Your application is ready: dist\visa_gui.exe
echo.
echo To run the application:
echo   dist\visa_gui.exe
echo.
echo Or double-click on visa_gui.exe in the dist folder.
echo.

REM Ask if user wants to run the app
set /p run_app=Run the application now? (y/N): 
if /i "%run_app%"=="y" (
    if exist "dist\visa_gui.exe" (
        echo Starting application...
        start "" "dist\visa_gui.exe"
    ) else (
        echo ERROR: Built application not found at dist\visa_gui.exe
    )
)

echo.
echo Build script completed!
pause 