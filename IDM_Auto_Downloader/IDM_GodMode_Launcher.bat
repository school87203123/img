@echo off
title IDM + FFmpeg + Python Ultra Pipeline
color 0b

:: 1. 切換到當前資料夾
cd /d "%~dp0"

echo ========================================================
echo       神級自動化工作流：IDM 下載 + 影格擷取
echo ========================================================
echo.

:: 2. 自動修復 OpenCV 環境 (解決你剛才看到的 cv2 報錯)
echo [步驟 1] 檢查並安裝必要套件...
python -m pip install --upgrade pip
python -m pip install opencv-python yt-dlp
echo.

:: 3. 執行 Python 腳本
echo [步驟 2] 啟動自動化流程...
echo --------------------------------------------------------
:: 請確保你的 Python 檔名與下方一致
python "IDM_Auto_GodMode.py"

:: 4. 錯誤處理
if %errorlevel% neq 0 (
    echo.
    echo --------------------------------------------------------
    echo [ERROR] 程式執行失敗！
    echo 請檢查：
    echo 1. IDM 路徑是否正確 (檢查 .py 內的 IDM_PATH)
    echo 2. 是否有安裝 FFmpeg 並加入環境變數
    echo 3. 網址與時間格式是否正確
    echo --------------------------------------------------------
    pause
)

exit