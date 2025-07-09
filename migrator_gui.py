import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import migrator
import os
from migrator import log_message
import webbrowser
import threading
import traceback

# Global variables (used by migrator.py)
PLANKA_URL = ""
USERNAME = ""
PASSWORD = ""
APIKEY = ""
APITOKEN = ""
TRELLO_URL = "https://api.trello.com/1/"  # constant

# Start migration and pass input values
def start_migration():
    global PLANKA_URL, USERNAME, PASSWORD, APIKEY, APITOKEN

    PLANKA_URL = planka_url_entry.get().strip()
    if not PLANKA_URL.endswith("/api"):
        PLANKA_URL += "/api"

    USERNAME = username_entry.get().strip()
    PASSWORD = password_entry.get().strip()
    APIKEY = apikey_entry.get().strip()
    APITOKEN = apitoken_entry.get().strip()

    migrator.PLANKA_URL = PLANKA_URL
    migrator.USERNAME = USERNAME
    migrator.PASSWORD = PASSWORD
    migrator.APIKEY = APIKEY
    migrator.APITOKEN = APITOKEN
    migrator.TRELLO_URL = TRELLO_URL
    migrator.log_gui = lambda msg: log_box.insert(tk.END, msg + "\n") or log_box.see(tk.END)

    log_box.delete("1.0", tk.END)

    def run_migration():
        while True:
            try:
                migrator.migrate_workspaces()
                log_box.see(tk.END)
                messagebox.showinfo("Done", "Migration completed successfully.")
                break
            except Exception as e:
                tb = traceback.format_exc()
                log_box.insert(tk.END, f"Error:\n{tb}\n")
                log_box.see(tk.END)
                result = messagebox.askretrycancel(
                    "Error",
                    f"Something went wrong:\n{str(e)}\n\nFull traceback is shown in the log.\n\nRetry (try again) or Cancel (ignore this error and continue)?"
                )
                if result:
                    continue  # Retry the operation
                else:
                    break     # Ignore the error and continue

    threading.Thread(target=run_migration).start()

# Save log to file
def save_log():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(log_box.get("1.0", tk.END))
        messagebox.showinfo("Saved", "Log saved successfully.")

# Enable right-click paste and Ctrl+V support
def add_entry_context_menu(entry):
    menu = tk.Menu(entry, tearoff=0)
    menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    def paste_once(event):
        entry.event_generate("<<Paste>>")
        return "break"

    entry.bind("<Button-3>", show_menu)
    entry.bind("<Control-v>", paste_once)
    entry.bind("<Control-V>", paste_once)

# GUI layout
window = tk.Tk()
window.title("Trello to Planka Migrator")
window.geometry("700x670")

fields = [
    ("Planka URL (without /api):", "https://planka.com"),
    ("Planka Username:", ""),
    ("Planka Password:", ""),
    ("Trello API Key:", ""),
    ("Trello API Token:", "")
]

entries = []

for label_text, default in fields:
    frame = tk.Frame(window)
    frame.pack(pady=3, anchor="w")
    tk.Label(frame, text=label_text, width=25, anchor="w").pack(side="left")
    entry = tk.Entry(frame, width=50)
    entry.insert(0, default)
    entry.pack(side="left")
    entries.append(entry)

planka_url_entry, username_entry, password_entry, apikey_entry, apitoken_entry = entries
for entry in entries:
    add_entry_context_menu(entry)

# Buttons
btn_frame = tk.Frame(window)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Start Migration", command=start_migration).pack(side="left", padx=10)
tk.Button(btn_frame, text="Save Log", command=save_log).pack(side="left", padx=10)

# Log box
log_box = scrolledtext.ScrolledText(window, width=90, height=25, font=("Consolas", 10))
log_box.pack(padx=10, pady=10)

# Support link
def open_support_link():
    webbrowser.open_new("https://github.com/John-Gear#if-you-find-my-project-useful-you-can-support-my-work--even-a-small-donation-makes-a-difference")

support_link = tk.Label(
    window,
    text="Support the author",
    fg="blue",
    cursor="hand2",
    font=("Arial", 9, "underline")
)
support_link.pack(pady=(5, 10))
support_link.bind("<Button-1>", lambda e: open_support_link())

def other_project_link():
    webbrowser.open_new("https://github.com/John-Gear/Bot_checker_date_planka_2.0?tab=readme-ov-file#description")

other_link = tk.Label(
    window,
    text="Check out my other project: Telegram bot for querying tasks by date in Planka v2.0",
    fg="blue",
    cursor="hand2",
    font=("Arial", 9, "underline")
)
other_link.pack(pady=(5, 10))
other_link.bind("<Button-1>", lambda e: other_project_link())

window.mainloop()