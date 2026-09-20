@echo off
setlocal

cd /d "%~dp0"
title Build PixelCrypt Image Encryption

echo =============================================
echo   PixelCrypt Image Encryption - EXE Builder
echo =============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo Install Python 3.8 or newer and select "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/3] Installing application requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

echo [2/3] Installing or updating PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo [ERROR] PyInstaller installation failed.
    pause
    exit /b 1
)

echo [3/3] Building the executable...
python -m PyInstaller --noconfirm --clean --onefile --windowed --collect-all PIL --name "PixelCrypt" pixelcrypt.py
if errorlevel 1 (
    echo [ERROR] The build failed. Review the messages above.
    pause
    exit /b 1
)

echo.
echo =============================================
echo   Build completed successfully.
echo   Output: dist\PixelCrypt.exe
echo =============================================
echo.
pause
endlocal
