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
    """過濾 Windows 不允許的資料夾命名符號"""
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

    # 1. 自動定位路徑
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 獲取網址與影片資訊
    url = simpledialog.askstring("IDM 幀數自選模式", "1. 請貼上 YouTube 網址:")
    if not url: return

    try:
        real_video_url, ext, video_title = get_video_info(url)
    except Exception as e:
        messagebox.showerror("解析失敗", f"無法解析網址：{e}")
        return

    # 3. 輸入設定：時間範圍 + 影格間隔
    start_t = simpledialog.askstring("時間設定", "2. 起始時間 (HH:MM:SS):", initialvalue="00:02:10")
    end_t = simpledialog.askstring("時間設定", "3. 結束時間 (HH:MM:SS):", initialvalue="00:02:20")
    frame_interval = simpledialog.askstring("影格設定", "4. 每隔幾幀抓一張？\n(1=全抓, 30=約半秒一張, 60=約一秒一張)", initialvalue="1")
    
    if not all([start_t, end_t, frame_interval]): return
    frame_interval = int(frame_interval)

    # 4. 建立資料夾
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

    # --- 階段 2: 幀數跳轉擷取 ---
    print(f"\n[階段 2] 開始依照間隔 {frame_interval} 擷取影格...")
    cap = cv2.VideoCapture(temp_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # 換算起始與結束幀
    h, m, s = map(int, start_t.split(':'))
    start_frame = int((h*3600 + m*60 + s) * fps)
    
    eh, em, es = map(int, end_t.split(':'))
    end_frame = int((eh*3600 + em*60 + es) * fps)

    current_f = start_frame
    saved_count = 0

    while current_f <= end_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_f)
        ret, frame = cap.read()
        if not ret: break
        
        saved_count += 1
        # 存檔依然使用流水號，保持資料夾整潔
        filename = os.path.join(final_output_dir, f"{saved_count:05d}.jpg")
        _, im_buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        im_buf.tofile(filename)
        
        current_f += frame_interval # 跳轉到下一目標幀
        
        if saved_count % 20 == 0:
            print(f"已噴出 {saved_count} 張照片... 目前幀數: {current_f}", end='\r')

    cap.release()
    print(f"\n[完成] 任務結束，共存下 {saved_count} 張照片。")

    # --- 階段 3: 清理 ---
    keep_video = messagebox.askyesno("完成", f"已在「{video_title}」存入 {saved_count} 張照片！\n\n是否要保留原始影片檔？")
    if not keep_video:
        try: os.remove(temp_video)
        except: pass

if __name__ == "__main__":
    main()