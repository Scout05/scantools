import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

def run_tools():
    # 1. Grab inputs from the UI
    target = url_entry.get().strip()
    proj_name = name_entry.get().strip()
    base_path = path_entry.get().strip()

    if not target or not proj_name or not base_path:
        messagebox.showwarning("Error", "Fill in all the boxes first.")
        return

    # 2. Setup the folder
    full_path = os.path.join(base_path, proj_name)
    os.makedirs(full_path, exist_ok=True)

    # 3. The background logic (NESTED inside run_tools so it can see the variables)
    def execute():
        log_box.insert(tk.END, f"[*] Project Folder: {full_path}\n")
        log_box.see(tk.END)
        
        discovery_files = [
            f"{full_path}/subs.txt",
            f"{full_path}/wayback.txt",
            f"{full_path}/katana.txt"
        ]
        
        cmds = [
            f"subfinder -d {target} -o {discovery_files[0]}",
            f"waybackurls {target} > {discovery_files[1]}",
            f"katana -u {target} -o {discovery_files[2]}"
        ]

        # Run Discovery
        for cmd in cmds:
            tool_name = cmd.split(' ')[0]
            log_box.insert(tk.END, f"[>] Running: {tool_name}...\n")
            log_box.see(tk.END)
            subprocess.run(cmd, shell=True, capture_output=True)

        # Merge & Clean
        log_box.insert(tk.END, "[*] Merging and cleaning results...\n")
        log_box.see(tk.END)
        raw_combined = f"{full_path}/raw_combined.txt"
        
        unique_urls = set()
        for file in discovery_files:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    unique_urls.update(line.strip() for line in f if line.strip())
        
        with open(raw_combined, 'w') as f:
            f.write("\n".join(unique_urls))

        # Probing Phase
        log_box.insert(tk.END, "[*] Running httpx probes (this may take a minute)...\n")
        log_box.see(tk.END)
        
        # Output 1: 200 OK only (Clean)
        file_200 = f"{full_path}/httpx_200_clean.txt"
        subprocess.run(f"httpx -l {raw_combined} -mc 200 -o {file_200} -silent -nc", shell=True)
        
        # Output 2: All with Status (httpx_all.txt)
        file_all_status = f"{full_path}/httpx_all.txt"
        subprocess.run(f"httpx -l {raw_combined} -status-code -o {file_all_status} -silent -nc", shell=True)
        
        # Output 3: All Clean
        file_all_clean = f"{full_path}/httpx_all_clean.txt"
        subprocess.run(f"httpx -l {raw_combined} -o {file_all_clean} -silent -nc", shell=True)

        log_box.insert(tk.END, "\n[+] TASK COMPLETE!\n")
        log_box.insert(tk.END, f"Check: {full_path}\n")
        log_box.see(tk.END)

    # 4. START THE THREAD (This makes the 'black box' actually update!)
    threading.Thread(target=execute).start()

# --- UI Setup (The '95 Aesthetic) ---
root = tk.Tk()
root.title("Bloodhound Automator v1.1")
root.geometry("550x550")
root.configure(bg="#d9d9d9")

label_style = {"bg": "#d9d9d9", "font": ("MS Sans Serif", 8)}

tk.Label(root, text="Project Name:", **label_style).pack(pady=2)
name_entry = tk.Entry(root, width=60)
name_entry.pack()

tk.Label(root, text="Base Save Path:", **label_style).pack(pady=2)
path_entry = tk.Entry(root, width=60)
path_entry.pack()
tk.Button(root, text="Browse Folder", command=lambda: path_entry.insert(0, filedialog.askdirectory()), bg="#c0c0c0").pack(pady=2)

tk.Label(root, text="Target Domain/URL:", **label_style).pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack()

run_btn = tk.Button(root, text="START HUNTING", command=run_tools, bg="#c0c0c0", relief="raised", bd=3, width=20, height=2)
run_btn.pack(pady=15)

# The "Black Box" Terminal Output
log_box = tk.Text(root, height=15, width=70, bg="black", fg="#00ff00", font=("Consolas", 9))
log_box.pack(pady=5)

root.mainloop()
