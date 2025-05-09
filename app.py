import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import subprocess
import sys

def select_b_folder():
    folder = filedialog.askdirectory(title="컨버팅된 폴더 선택")
    if folder:
        b_folder_var.set(folder)

def select_a_folder():
    folder = filedialog.askdirectory(title="원시데이터 폴더 선택")
    if folder:
        a_folder_var.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory(title="출력 폴더 선택")
    if folder:
        output_folder_var.set(folder)

def count_total_files(b_root):
    count = 0
    for b_dir_name in os.listdir(b_root):
        b_dir_path = os.path.join(b_root, b_dir_name)
        if os.path.isdir(b_dir_path):
            count += len([f for f in os.listdir(b_dir_path) if os.path.isfile(os.path.join(b_dir_path, f))])
    return count

def seconds_to_min_sec(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{int(minutes)}분 {int(sec)}초"

def open_folder(path):
    try:
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except Exception as e:
        print(f"폴더 열기 실패: {e}")

def process_files():
    b_root = b_folder_var.get()
    a_root = a_folder_var.get()
    output_root = output_folder_var.get()

    if not all([b_root, a_root, output_root]):
        messagebox.showerror("오류", "모든 폴더를 선택하세요.")
        return

    total_files = count_total_files(b_root)
    if total_files == 0:
        messagebox.showerror("오류", "b 폴더에 처리할 파일이 없습니다.")
        return

    progress_bar["maximum"] = total_files
    progress_bar["value"] = 0
    status_var.set("처리 시작...")

    start_time = time.time()
    processed_files = 0

    for b_dir_name in os.listdir(b_root):
        b_dir_path = os.path.join(b_root, b_dir_name)
        if not os.path.isdir(b_dir_path):
            continue

        match = re.match(r"(\d{6})-(\d{4})", b_dir_name)
        if not match:
            continue

        b_date, b_number = match.groups()
        
        # 6자리 b_date → 8자리 a_date (앞에 '20' 붙이기)
        a_date = '20' + b_date

        a_dir_path = os.path.join(a_root, a_date, "Single", b_number)
        if not os.path.exists(a_dir_path):
            print(f"a폴더에 {b_number} 폴더 없음, 건너뜀")
            continue

        a_files = os.listdir(a_dir_path)
        has_middle = any("middle" in f.lower() for f in a_files)
        has_high = any("high" in f.lower() for f in a_files)

        for b_file in os.listdir(b_dir_path):
            b_file_path = os.path.join(b_dir_path, b_file)
            if not os.path.isfile(b_file_path):
                print(f"[SKIP] 파일이 아님: {b_file_path}")
                continue

            suffix = ""
            if has_middle:
                suffix = "_m"
            elif has_high:
                suffix = "_h"

            # ✅ 🔽 여기부터 파일명 처리 방식 수정됨
            name_only = os.path.splitext(b_file)[0]  # ex: 'lumi_00'
            match = re.match(r"(.+)_([0-9]{2})$", name_only)
            if not match:
                print(f"[SKIP] 이름 형식 안 맞음: {b_file}")
                continue

            base_name, file_num = match.groups()

            # ✅ 최종 파일명: 중간에 suffix 삽입, 숫자는 뒤에 유지
            new_file_name = f"{b_date}-{b_number}-{base_name}{suffix}_{file_num}.{b_file.split('.')[-1]}"
            # ✅ 🔼 여기까지 수정 완료
            
            output_subdir = os.path.join(output_root, b_date, file_num)
            os.makedirs(output_subdir, exist_ok=True)

            output_file_path = os.path.join(output_subdir, new_file_name)
            # ✅ 복사 직전 디버깅 로그
            print(f"[COPY] {b_file_path} → {output_file_path}")
            shutil.copy2(b_file_path, output_file_path)

            processed_files += 1
            progress_bar["value"] = processed_files

            elapsed = time.time() - start_time
            avg_time = elapsed / processed_files if processed_files > 0 else 0
            remaining = total_files - processed_files
            est_remaining_time_sec = int(avg_time * remaining)
            est_time_str = seconds_to_min_sec(est_remaining_time_sec)

            status_var.set(f"진행: {processed_files}/{total_files} | 예상 남은 시간: {est_time_str}")
            root.update_idletasks()

    status_var.set("처리 완료!")
    messagebox.showinfo("완료", "파일 처리가 완료되었습니다.")
    open_folder(output_root)

# ------------------ GUI ------------------

root = tk.Tk()
root.title("a/b 폴더 파일 매칭 및 복사기")

b_folder_var = tk.StringVar()
a_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
status_var = tk.StringVar()

tk.Label(root, text="b 폴더:").grid(row=0, column=0, sticky='e')
tk.Entry(root, textvariable=b_folder_var, width=60).grid(row=0, column=1)
tk.Button(root, text="선택", command=select_b_folder).grid(row=0, column=2)

tk.Label(root, text="a 폴더:").grid(row=1, column=0, sticky='e')
tk.Entry(root, textvariable=a_folder_var, width=60).grid(row=1, column=1)
tk.Button(root, text="선택", command=select_a_folder).grid(row=1, column=2)

tk.Label(root, text="출력 폴더:").grid(row=2, column=0, sticky='e')
tk.Entry(root, textvariable=output_folder_var, width=60).grid(row=2, column=1)
tk.Button(root, text="선택", command=select_output_folder).grid(row=2, column=2)

tk.Button(root, text="실행", command=process_files, bg="lightgreen", width=20).grid(row=3, column=1, pady=10)

progress_bar = ttk.Progressbar(root, length=400)
progress_bar.grid(row=4, column=0, columnspan=3, pady=5)

tk.Label(root, textvariable=status_var).grid(row=5, column=0, columnspan=3)

root.mainloop()
