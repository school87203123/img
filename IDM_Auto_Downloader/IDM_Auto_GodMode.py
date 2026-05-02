import os
import subprocess
import time
import cv2
import yt_dlp
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox

# 【設定】請確認你的 IDM 安裝路徑
IDM_PATH = r"E:\應用程式\Internet Download Manager\IDMan.exe"

def get_real_url(yt_url):
    """解鎖 4K/8K：抓取最高解析度的影像軌"""
    print("[偵查] 正在解析 YouTube 隱藏的最高畫質連結...")
    ydl_opts = {
        # 'bestvideo' 會抓取最高解析度 (4K/8K)，不再受限於 MP4 的 1080p 限制
        'format': 'bestvideo', 
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=False)
        width = info.get('width')
        height = info.get('height')
        print(f"✅ 成功偵測到目標解析度: {width} x {height}")
        return info['url'], info.get('ext', 'mp4')

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    url = simpledialog.askstring("IDM 神級模式", "1. 請貼上 YouTube 網址:")
    if not url: return

    # 獲取真實直連位址
    try:
        real_video_url, ext = get_real_url(url)
    except Exception as e:
        messagebox.showerror("解析失敗", f"無法解析網址：{e}")
        return

    start_t = simpledialog.askstring("時間", "2. 起始時間 (HH:MM:SS):", initialvalue="00:02:10")
    end_t = simpledialog.askstring("時間", "3. 結束時間 (HH:MM:SS):", initialvalue="00:02:20")
    
    output_dir = filedialog.askdirectory(title="4. 選擇儲存資料夾")
    if not output_dir: return

    # 建立一個唯一的暫存檔名，避免衝突
    temp_video = os.path.join(output_dir, f"raw_video_temp.{ext}")

    # 呼叫 IDM 下載
    print(f"\n[階段 1] 正在啟動 IDM 暴力下載 (最高畫質)...")
    idm_cmd = [IDM_PATH, "/d", real_video_url, "/p", output_dir, "/f", f"raw_video_temp.{ext}", "/n", "/q"]
    subprocess.run(idm_cmd)

    # 監控下載進度
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

    # [階段 2] 極致噴圖
    print("\n[階段 2] 下載完成，開始噴圖...")
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
        
        filename = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
        _, im_buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        im_buf.tofile(filename)
        saved_count += 1
        if saved_count % 50 == 0:
            print(f"已存 {saved_count} 張照片...", end='\r')

    cap.release()
    print("\n[完成] 影格擷取完畢。")

    # ==========================================
    # 新功能：自動問詢是否刪除影片
    # ==========================================
    keep_video = messagebox.askyesno("任務完成", f"共產出 {saved_count} 張最高畫質照片！\n\n是否要保留下載的原始影片檔？\n(選「否」將自動刪除以節省空間)")
    
    if not keep_video:
        try:
            if os.path.exists(temp_video):
                os.remove(temp_video)
                print(f"[清理] 已刪除暫存影片：{temp_video}")
        except Exception as e:
            print(f"[警告] 無法刪除檔案: {e}")
    else:
        print(f"[保留] 影片檔已存於: {temp_video}")

if __name__ == "__main__":
    main()