@echo off
cd /d "%~dp0"

echo Building FishingAssistant.exe...

python -m PyInstaller --onefile --noconsole ^
    --icon=assets/fish.ico ^
    --add-data "assets/fish.ico;assets" ^
    --add-data "config.json;." ^
    --name FishingAssistant ^
    main.py

if %ERRORLEVEL% == 0 (
    echo.
    echo Build successful! Output: dist\FishingAssistant.exe
) else (
    echo.
    echo Build failed. Check the output above for errors.
)

pause
