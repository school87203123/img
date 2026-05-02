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
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def get_video_info(yt_url):
    print("[偵查] 正在解析 YouTube 影片資訊...")
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

    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    url = simpledialog.askstring("FFmpeg 閃電模式", "1. 請貼上 YouTube 網址:")
    if not url: return

    try:
        real_video_url, ext, video_title = get_video_info(url)
    except Exception as e:
        messagebox.showerror("解析失敗", f"無法解析網址：{e}")
        return

    # 輸入設定
    start_t = simpledialog.askstring("時間設定", "2. 起始時間 (HH:MM:SS):", initialvalue="00:02:10")
    end_t = simpledialog.askstring("時間設定", "3. 結束時間 (HH:MM:SS):", initialvalue="00:02:20")
    frame_interval = simpledialog.askstring("影格設定", "4. 每隔幾幀抓一張？", initialvalue="1")
    
    if not all([start_t, end_t, frame_interval]): return

    final_output_dir = os.path.join(current_dir, video_title)
    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)
    
    temp_video = os.path.join(final_output_dir, f"source_video.{ext}")

    # --- 階段 1: IDM 下載 ---
    print(f"\n[階段 1] 啟動 IDM 下載中...")
    idm_cmd = [IDM_PATH, "/d", real_video_url, "/p", final_output_dir, "/f", f"source_video.{ext}", "/n", "/q"]
    subprocess.run(idm_cmd)

    print("等待下載完成...")
    while not os.path.exists(temp_video):
        time.sleep(2)
    
    last_size = -1
    while True:
        current_size = os.path.getsize(temp_video)
        if current_size == last_size and current_size > 0: break
        last_size = current_size
        time.sleep(3)
        print(f"下載中... 目前已載: {current_size // (1024*1024)} MB")

    # --- 階段 2: FFmpeg 閃電擷取 (關鍵改動：不經過 Python 迴圈) ---
    print(f"\n[階段 2] 啟動 FFmpeg 引擎進行精準擷取...")
    
    # -ss: 開始時間, -to: 結束時間, select: 每 N 幀選一張
    ffmpeg_cmd = [
        "ffmpeg", 
        "-ss", start_t, 
        "-to", end_t, 
        "-i", temp_video,
        "-vf", f"select='not(mod(n,{frame_interval}))'",
        "-vsync", "vfr",
        "-q:v", "2", 
        os.path.join(final_output_dir, "%05d.jpg")
    ]
    
    start_process_time = time.time()
    subprocess.run(ffmpeg_cmd)
    end_process_time = time.time()

    # --- 階段 3: 清理 ---
    keep_video = messagebox.askyesno("完成", f"處理耗時: {end_process_time - start_process_time:.2f} 秒\n\n是否保留原始影片檔？")
    if not keep_video:
        try: os.remove(temp_video)
        except: pass

if __name__ == "__main__":
    main()