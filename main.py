"""
GIF to 32x64 LED Converter — entry point.

Opens file-picker dialogs to select the input GIF and the CSV save location,
then runs the conversion.
"""

import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from converter import GIFConverter


def pick_gif() -> str:
    path = filedialog.askopenfilename(
        title="Select GIF file",
        filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
    )
    return path


def pick_csv_save() -> str:
    path = filedialog.asksaveasfilename(
        title="Save CSV as",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )
    return path


def main():
    root = tk.Tk()
    root.withdraw()  # hide the empty root window; we only want the dialogs

    gif_path = pick_gif()
    if not gif_path:
        messagebox.showinfo("Cancelled", "No GIF selected. Exiting.")
        sys.exit(0)

    csv_path = pick_csv_save()
    if not csv_path:
        messagebox.showinfo("Cancelled", "No save location selected. Exiting.")
        sys.exit(0)

    try:
        converter = GIFConverter()

        print(f"Loading {gif_path} ...")
        converter.load_gif(gif_path)
        print(f"  {len(converter.frames)} frame(s) found")

        print(f"Exporting to {csv_path} ...")
        converter.export_csv(csv_path)

        messagebox.showinfo(
            "Done",
            f"Converted {len(converter.frames)} frame(s).\nSaved to:\n{csv_path}",
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))
        raise


if __name__ == "__main__":
    main()
