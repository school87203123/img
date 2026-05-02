@echo off
title Frame to Video Assembler
color 0e

cd /d "%~dp0"

echo ---------------------------------------------------
echo       Initializing Frame Assembler...
echo ---------------------------------------------------
echo.

:: 執行 Python 腳本
python "Frames_to_Video_Ultra.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Assembly failed. Please check your image files.
    pause
)

echo.
echo [DONE] Task finished successfully.
pause