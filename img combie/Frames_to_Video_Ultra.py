import cv2
import os
import re
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# ==========================================
# 1. 資管系專業排序邏輯 (Natural Sort)
# ==========================================
def natural_sort_key(s):
    """
    確保排序為 1, 2, 3... 10，而不是 1, 10, 2
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # 1. 選擇來源資料夾
    img_dir = filedialog.askdirectory(title="1. 請選擇包含影格圖片的資料夾")
    if not img_dir: return

    # 2. 獲取所有圖片檔案 (支援 jpg, png)
    extensions = ("*.jpg", "*.jpeg", "*.png")
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(img_dir, ext)))

    if not image_files:
        messagebox.showerror("錯誤", "資料夾內找不到圖片檔案！")
        return

    # 3. 進行精準排序
    image_files.sort(key=natural_sort_key)

    # 4. 讀取第一張圖來獲取影片寬高
    first_image = cv2.imread(image_files[0])
    height, width, layers = first_image.shape

    # 5. 設定參數
    fps = simpledialog.askstring("影片設定", "請輸入影片 FPS (建議與原始影片一致，如 60):", initialvalue="60")
    if not fps: return
    fps = float(fps)

    output_path = filedialog.asksaveasfilename(
        title="2. 請選擇影片存檔位置",
        defaultextension=".mp4",
        filetypes=[("MP4 Video", "*.mp4"), ("AVI Video", "*.avi")]
    )
    if not output_path: return

    # 6. 初始化影片寫入器 (使用 XVID 或 mp4v 編碼)
    print(f"\n[啟動] 正在合成影片...")
    print(f"解析度: {width} x {height} | FPS: {fps}")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # 強力壓縮且畫質優良的編碼
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total = len(image_files)
    for i, file_path in enumerate(image_files):
        frame = cv2.imread(file_path)
        out.write(frame)
        
        # 顯示進度
        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"進度: [{(i + 1) / total * 100:>5.1f}%] - 已處理 {i + 1}/{total} 張影格", end='\r')

    out.release()
    print(f"\n\n[成功] 影片已生成：{os.path.basename(output_path)}")
    messagebox.showinfo("合成完畢", f"影片合成成功！\n\n檔名：{os.path.basename(output_path)}\n總影格數：{total}")

if __name__ == "__main__":
    main()