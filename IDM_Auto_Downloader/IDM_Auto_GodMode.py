import os
import subprocess
import time
import cv2
import yt_dlp
import re
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

# 【設定】請確認你的 IDM 安裝路徑
IDM_PATH = r"E:\應用程式\Internet Download Manager\IDMan.exe"

def sanitize_filename(filename):
    """資管系專業：過濾 Windows 不允許的資料夾命名符號"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def get_video_info(yt_url):
    """偵查：獲取真實連結與影片標題"""
    print("[偵查] 正在解析 YouTube 影片資訊...")
    ydl_opts = {
        'format': 'bestvideo', 
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=False)
        title = info.get('title', 'Untitled_Video')
        clean_title = sanitize_filename(title)
        width = info.get('width')
        height = info.get('height')
        print(f"✅ 標題: {clean_title}")
        print(f"✅ 解析度: {width} x {height}")
        return info['url'], info.get('ext', 'mp4'), clean_title

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # 1. 自動獲取目前程式執行的目錄
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 輸入網址
    url = simpledialog.askstring("IDM 特定秒數模式", "1. 請貼上 YouTube 網址:")
    if not url: return

    # 解析影片資訊
    try:
        real_video_url, ext, video_title = get_video_info(url)
    except Exception as e:
        messagebox.showerror("解析失敗", f"無法解析網址：{e}")
        return

    # 3. 輸入時間
    start_t = simpledialog.askstring("時間設定", "2. 起始時間 (HH:MM:SS):", initialvalue="00:02:10")
    end_t = simpledialog.askstring("時間設定", "3. 結束時間 (HH:MM:SS):", initialvalue="00:02:20")
    if not start_t or not end_t: return

    # 4. 自動建立影片標題資料夾 (零點擊邏輯)
    final_output_dir = os.path.join(current_dir, video_title)
    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)
        print(f"[建立] 已自動創建資料夾：{video_title}")

    # 暫存檔路徑
    temp_video = os.path.join(final_output_dir, f"raw_video_source.{ext}")

    # --- 階段 1: IDM 下載 ---
    print(f"\n[階段 1] 啟動 IDM 下載中...")
    idm_cmd = [IDM_PATH, "/d", real_video_url, "/p", final_output_dir, "/f", f"raw_video_source.{ext}", "/n", "/q"]
    subprocess.run(idm_cmd)

    print("等待下載完成...")
    while not os.path.exists(temp_video):
        time.sleep(2)
    
    last_size = -1
    while True:
        current_size = os.path.getsize(temp_video)
        if current_size == last_size and current_size > 0:
            break
        last_size = current_size
        time.sleep(3)
        print(f"下載中... 目前已載: {current_size // (1024*1024)} MB")

    # --- 階段 2: 精準噴圖 (流水號命名) ---
    print(f"\n[階段 2] 開始擷取影格...")
    cap = cv2.VideoCapture(temp_video)
    
    # 時間跳轉邏輯
    h, m, s = map(int, start_t.split(':'))
    start_msec = (h*3600 + m*60 + s) * 1000
    cap.set(cv2.CAP_PROP_POS_MSEC, start_msec)
    
    end_h, end_m, end_s = map(int, end_t.split(':'))
    end_msec = (end_h*3600 + end_m*60 + end_s) * 1000

    saved_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        curr_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        
        if not ret or curr_msec > end_msec:
            break
        
        # 存檔名稱改為純數字流水號 00001.jpg
        saved_count += 1
        filename = os.path.join(final_output_dir, f"{saved_count:05d}.jpg")
        
        _, im_buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        im_buf.tofile(filename)
        
        if saved_count % 50 == 0:
            print(f"已噴出 {saved_count} 張照片...", end='\r')

    cap.release()
    print(f"\n[完成] 影格擷取完畢，共產出 {saved_count} 張照片。")

    # --- 階段 3: 清理 ---
    keep_video = messagebox.askyesno("任務完成", f"已在資料夾「{video_title}」中存入 {saved_count} 張最高畫質照片！\n\n是否要保留下載的影片檔？")
    
    if not keep_video:
        try:
            if os.path.exists(temp_video):
                os.remove(temp_video)
                print(f"[清理] 已刪除暫存影片。")
        except Exception as e:
            print(f"[警告] 無法刪除檔案: {e}")

    print("\n[結束] 所有檔案已歸檔於：" + final_output_dir)

if __name__ == "__main__":
    main()