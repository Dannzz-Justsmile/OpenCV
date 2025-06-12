import os
import shutil
import tkinter as tk
from tkinter import simpledialog, messagebox, Listbox, END, filedialog
from PIL import Image, ImageDraw
import numpy as np
import cv2
import subprocess
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "finger_db")
MAIN_EXE = os.path.join(BASE_DIR, "main.exe")

PRIMARY = "#00ffe7"
BG = "#232837"
BTN_BG = "#232837"
BTN_FG = "#00ffe7"
BTN_ACTIVE_BG = "#00ffe7"
BTN_ACTIVE_FG = "#232837"
CANVAS_BG = "#181c24"
HEADER_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 12)
BTN_FONT = ("Segoe UI", 11, "bold")
LIST_FONT = ("Segoe UI", 11)
ENTRY_FONT = ("Segoe UI", 11)

def get_descriptors(img_path):
    img = cv2.imread(img_path, 0)
    if img is None:
        messagebox.showerror("Error", f"Could not read image:\n{img_path}")
        return None
    sift = cv2.SIFT_create()
    kp, des = sift.detectAndCompute(img, None)
    return des

def match_descriptors(des1, des2):
    if des1 is None or des2 is None:
        return []
    bf = cv2.BFMatcher()
    matches = bf.match(des1, des2)
    return matches

class FingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Finger Identification App")
        self.root.geometry("370x480")
        self.root.configure(bg=BG)
        os.makedirs(DATA_DIR, exist_ok=True)

        # Header
        tk.Label(root, text="Fingerprint Access", font=HEADER_FONT, bg=BG, fg=PRIMARY).pack(pady=(24, 8))

        # Status
        self.status_label = tk.Label(root, text="Welcome!", font=LABEL_FONT, bg=BG, fg=PRIMARY)
        self.status_label.pack(pady=(0, 18))

        # Buttons
        self._modern_btn(root, "Create Profile", self.create_profile).pack(pady=8)
        self._modern_btn(root, "Login", self.login_profile).pack(pady=8)
        self._modern_btn(root, "Import Image Login", self.import_image_login).pack(pady=8)
        self._modern_btn(root, "Exit", root.quit, color="#ff4c4c", fg=BG).pack(pady=18)
        self.canvas = None

    def _modern_btn(self, parent, text, cmd, width=22, color=BTN_BG, fg=BTN_FG):
        return tk.Button(
            parent, text=text, command=cmd, width=width, font=BTN_FONT,
            bg=color, fg=fg, activebackground=BTN_ACTIVE_BG, activeforeground=BTN_ACTIVE_FG,
            bd=0, highlightthickness=0, relief="flat", cursor="hand2"
        )

    def create_profile(self):
        username = simpledialog.askstring("Create Profile", "Enter username (letters and numbers only):")
        if not username or not username.isalnum():
            messagebox.showerror("Error", "Invalid username. Use only letters and numbers.")
            return
        user_dir = os.path.join(DATA_DIR, username)
        if os.path.exists(user_dir):
            messagebox.showerror("Error", "Profile already exists.")
            return
        self._scan_screen(lambda img_path: self._save_profile(username, img_path), mode="create")

    def _save_profile(self, username, img_path):
        user_dir = os.path.join(DATA_DIR, username)
        if not img_path:
            self.status_label.config(text="Profile creation cancelled.", fg="#ff4c4c")
            return
        os.makedirs(user_dir, exist_ok=True)
        save_path = os.path.join(user_dir, "fingerprint.png")
        shutil.copy(img_path, save_path)
        des = get_descriptors(save_path)
        np.save(os.path.join(user_dir, "desc.npy"), des)
        self.status_label.config(text=f"Profile '{username}' created!", fg="#00ff99")

    def login_profile(self):
        profiles = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
        if not profiles:
            messagebox.showerror("Error", "No profiles found. Please create one first.")
            return
        win = tk.Toplevel(self.root)
        win.title("Select Profile")
        win.geometry("300x320")
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text="Select profile", font=HEADER_FONT, bg=BG, fg=PRIMARY).pack(pady=(18, 8))
        lb = Listbox(
            win, font=LIST_FONT, bg=CANVAS_BG, fg=PRIMARY, selectbackground=PRIMARY,
            selectforeground=BG, selectmode=tk.SINGLE, activestyle="dotbox", bd=0, highlightthickness=0
        )
        for p in profiles:
            lb.insert(END, p)
        lb.pack(pady=8, fill="both", expand=True, padx=24)
        lb.focus_set()

        def do_login():
            sel = lb.curselection()
            if not sel:
                messagebox.showerror("Error", "No profile selected.")
                return
            username = lb.get(sel[0])
            win.destroy()
            self._scan_screen(lambda img_path: self._check_login(username, img_path), mode="login")

        self._modern_btn(win, "Login", do_login, width=14).pack(pady=8)
        self._modern_btn(win, "Cancel", win.destroy, width=14, color="#ff4c4c", fg=BG).pack()
        lb.bind('<Double-1>', lambda e: do_login())

    def import_image_login(self):
        profiles = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
        if not profiles:
            messagebox.showerror("Error", "No profiles found. Please create one first.")
            return
        win = tk.Toplevel(self.root)
        win.title("Select Profile")
        win.geometry("300x320")
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text="Select profile", font=HEADER_FONT, bg=BG, fg=PRIMARY).pack(pady=(18, 8))
        lb = Listbox(
            win, font=LIST_FONT, bg=CANVAS_BG, fg=PRIMARY, selectbackground=PRIMARY,
            selectforeground=BG, selectmode=tk.SINGLE, activestyle="dotbox", bd=0, highlightthickness=0
        )
        for p in profiles:
            lb.insert(END, p)
        lb.pack(pady=8, fill="both", expand=True, padx=24)
        lb.focus_set()

        def do_import():
            sel = lb.curselection()
            if not sel:
                messagebox.showerror("Error", "No profile selected.")
                return
            username = lb.get(sel[0])
            img_path = filedialog.askopenfilename(
                title="Select Image for Login",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
            )
            if not img_path:
                return
            win.destroy()
            self._check_login(username, img_path)

        self._modern_btn(win, "Import Image & Login", do_import, width=18).pack(pady=8)
        self._modern_btn(win, "Cancel", win.destroy, width=14, color="#ff4c4c", fg=BG).pack()
        lb.bind('<Double-1>', lambda e: do_import())

    def _scan_screen(self, callback, mode="login"):
        scan_win = tk.Toplevel(self.root)
        scan_win.title("Draw your fingerprint")
        scan_win.geometry("300x370")
        scan_win.configure(bg=BG)
        scan_win.resizable(False, False)
        tk.Label(scan_win, text="Draw your fingerprint\n(hold and drag mouse)", font=LABEL_FONT, bg=BG, fg=PRIMARY).pack(pady=(18, 8))
        frame = tk.Frame(scan_win, bg=BG, bd=0, highlightthickness=0)
        frame.pack(pady=8)
        canvas = tk.Canvas(frame, width=220, height=220, bg=CANVAS_BG, bd=0, highlightthickness=2, highlightbackground=PRIMARY, cursor="pencil")
        canvas.pack()
        img = Image.new("L", (220, 220), 255)
        draw = ImageDraw.Draw(img)
        last = [None]
        def on_down(event):
            last[0] = (event.x, event.y)
        def on_move(event):
            if last[0]:
                canvas.create_line(last[0][0], last[0][1], event.x, event.y, fill=PRIMARY, width=4, capstyle=tk.ROUND, smooth=True)
                draw.line([last[0], (event.x, event.y)], fill=0, width=8)
                last[0] = (event.x, event.y)
        def on_up(event):
            last[0] = None
        canvas.bind("<Button-1>", on_down)
        canvas.bind("<B1-Motion>", on_move)
        canvas.bind("<ButtonRelease-1>", on_up)
        def save_and_close():
            temp_path = os.path.join(DATA_DIR, "temp_scan.png")
            img.save(temp_path)
            scan_win.destroy()
            callback(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        def cancel():
            scan_win.destroy()
            callback(None)
        self._modern_btn(scan_win, "Scan", save_and_close, width=14).pack(pady=8)
        self._modern_btn(scan_win, "Cancel", cancel, width=14, color="#ff4c4c", fg=BG).pack()

        scan_win.transient(self.root)
        scan_win.grab_set()
        scan_win.wait_window()

    def _check_login(self, username, img_path):
        user_dir = os.path.join(DATA_DIR, username)
        profile_img = os.path.join(user_dir, "fingerprint.png")
        desc_path = os.path.join(user_dir, "desc.npy")
        if not img_path or not os.path.exists(profile_img) or not os.path.exists(desc_path):
            self.status_label.config(text="Login cancelled.", fg="#ff4c4c")
            return
        des1 = np.load(desc_path, allow_pickle=True)
        des2 = get_descriptors(img_path)
        matches = match_descriptors(des1, des2)
        if matches:
            avg_dist = np.mean([m.distance for m in matches])
        else:
            avg_dist = 999
        threshold = 200  # Accepts similar, not exact, drawings/images
        # Show the score to the user for transparency
        if avg_dist < threshold:
            self.status_label.config(text=f"✔ Access Granted! (similarity score: {avg_dist:.1f})", fg="#00ff99")
            self.root.after(1200, self._launch_main)
        else:
            self.status_label.config(text=f"✖ Access Denied (similarity score: {avg_dist:.1f})", fg="#ff4c4c")

    def _launch_main(self):
        if os.path.exists(MAIN_EXE):
            subprocess.Popen([MAIN_EXE])
            self.root.destroy()
        else:
            messagebox.showerror("Error", f"main.exe not found at:\n{MAIN_EXE}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FingerApp(root)
    root.mainloop()