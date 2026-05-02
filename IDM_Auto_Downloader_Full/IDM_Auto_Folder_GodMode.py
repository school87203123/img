import os
import subprocess
import time
import yt_dlp
import re
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

# 【設定】請確認你的 IDM 安裝路徑
IDM_PATH = r"E:\應用程式\Internet Download Manager\IDMan.exe"

def sanitize_filename(filename):
    """過濾 Windows 不允許的資料夾命名符號"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def get_video_info(yt_url):
    print("[偵查] 正在獲取影片資訊...")
    ydl_opts = {'format': 'bestvideo', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=False)
        title = info.get('title', 'Untitled_Video')
        clean_title = sanitize_filename(title)
        return info['url'], info.get('ext', 'mp4'), clean_title

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # 1. 自動獲取執行路徑
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    url = simpledialog.askstring("極致歸檔模式", "1. 請貼上 YouTube 網址:")
    if not url: return

    try:
        real_video_url, ext, video_title = get_video_info(url)
    except Exception as e:
        messagebox.showerror("解析失敗", f"無法解析：{e}")
        return

    frame_interval = simpledialog.askstring("擷取設定", "2. 每隔幾幀抓一張？", initialvalue="30")
    if not frame_interval: return

    # 2. 建立資料夾
    final_output_dir = os.path.join(current_dir, video_title)
    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)
    
    temp_video = os.path.join(final_output_dir, f"original_video.{ext}")

    # --- 階段 1: IDM 暴力下載 ---
    print(f"\n[階段 1] IDM 全速下載中 -> {video_title}")
    # /d 網址 /p 路徑 /f 檔名 /n 自動開始 /q 下載完關閉
    idm_cmd = [IDM_PATH, "/d", real_video_url, "/p", final_output_dir, "/f", f"original_video.{ext}", "/n", "/q"]
    subprocess.run(idm_cmd)

    print("等待下載結束與檔案合併...")
    while not os.path.exists(temp_video):
        time.sleep(2)
    
    last_size = -1
    while True:
        current_size = os.path.getsize(temp_video)
        if current_size == last_size and current_size > 0: break
        last_size = current_size
        time.sleep(3)
        print(f"進度：檔案已載入 {current_size // (1024*1024)} MB")

    # --- 階段 2: FFmpeg 閃電擷取 (流水號命名) ---
    print(f"\n[階段 2] FFmpeg 引擎啟動：正在生成流水號影格...")
    
    # 輸出的檔名改為純數字流水號 %05d.jpg
    # -q:v 2 代表極高畫質，-vsync vfr 確保不會產生重複影格
    ffmpeg_cmd = [
        "ffmpeg", "-i", temp_video,
        "-vf", f"select='not(mod(n,{frame_interval}))'",
        "-vsync", "vfr",
        "-q:v", "2",
        os.path.join(final_output_dir, "%05d.jpg")
    ]
    
    start_time = time.time()
    subprocess.run(ffmpeg_cmd)
    end_time = time.time()

    # --- 階段 3: 完成與清理 ---
    print(f"\n[完成] 處理耗時: {end_time - start_time:.2f} 秒")
    keep_video = messagebox.askyesno("任務成功", f"資料夾：{video_title}\n圖片已用流水號存檔完畢。\n\n是否保留原始影片檔？")
    
    if not keep_video:
        try: os.remove(temp_video)
        except: pass

if __name__ == "__main__":
    main()