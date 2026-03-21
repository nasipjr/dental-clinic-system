import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "clinic_config.json")


def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_var.set(folder_selected)


def save_config():
    folder = path_var.get()

    if not folder:
        messagebox.showerror("Error", "Please select a folder first")
        return

    try:
        # Ensure the config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)

        config_data = {
            "log_directory": folder
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)

        messagebox.showinfo("Success", "Configuration saved successfully!")
        root.quit()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")


# GUI
root = tk.Tk()
root.title("Clinic System Setup")
root.geometry("400x200")
root.resizable(False, False)

path_var = tk.StringVar()

tk.Label(root, text="Select Log Directory:", font=("Arial", 12)).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Entry(frame, textvariable=path_var, width=30).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)

tk.Button(root, text="Save", command=save_config, bg="green", fg="white").pack(pady=20)

root.mainloop()