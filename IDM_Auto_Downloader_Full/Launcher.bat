@echo off
title IDM Video Auto-Folder Scanner
color 0b

:: 1. 定位到當前資料夾
cd /d "%~dp0"

echo ========================================================
echo       IDM 影片自動下載與資料夾歸檔工具
echo ========================================================
echo.

:: 2. 環境自動檢查
echo [檢查] 正在確認必要套件 (yt-dlp, opencv, pillow)...
python -m pip install --upgrade pip >nul
python -m pip install yt-dlp opencv-python >nul
echo.

:: 3. 執行 Python 腳本
:: 請確認你的 Python 檔名與下方引號內一致
echo [啟動] 正在執行 IDM_Auto_Folder_GodMode.py ...
echo --------------------------------------------------------
python "IDM_Auto_Folder_GodMode.py"

:: 4. 錯誤偵測
if %errorlevel% neq 0 (
    echo.
    echo --------------------------------------------------------
    echo [ERROR] 程式意外結束！
    echo 可能原因：
    echo 1. IDMan.exe 路徑設定錯誤 (請檢查 .py 內的 IDM_PATH)
    echo 2. FFmpeg 未安裝或未加入環境變數
    echo 3. 網路連線異常或 YouTube 網址失效
    echo --------------------------------------------------------
    pause
) else (
    echo.
    echo [完成] 掃描任務已成功結束。
    timeout /t 5
)

exit