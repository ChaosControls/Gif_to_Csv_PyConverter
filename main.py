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

    print("=" * 50)
    print("  GIF to 32x64 LED CSV Converter")
    print("=" * 50)

    print("\nStep 1/3 — Select your GIF file.")
    print("  A file browser window will open. Navigate to your GIF and select it.")
    gif_path = pick_gif()
    if not gif_path:
        print("  No GIF selected. Exiting.")
        messagebox.showinfo("Cancelled", "No GIF selected. Exiting.")
        sys.exit(0)
    print(f"  GIF selected: {gif_path}")

    print("\nStep 2/3 — Choose where to save the CSV.")
    print("  A save dialog will open. Pick a folder and filename for the output CSV.")
    csv_path = pick_csv_save()
    if not csv_path:
        print("  No save location selected. Exiting.")
        messagebox.showinfo("Cancelled", "No save location selected. Exiting.")
        sys.exit(0)
    print(f"  CSV will be saved to: {csv_path}")

    print("\nStep 3/3 — Converting ...")
    try:
        converter = GIFConverter()

        print(f"  Loading GIF ...")
        converter.load_gif(gif_path)
        print(f"  {len(converter.frames)} frame(s) found  |  "
              f"total duration: {sum(converter.durations)} ms")

        print(f"  Building pixel arrays and writing CSV ...")
        converter.export_csv(csv_path)

        print(f"\nDone! CSV saved to: {csv_path}")
        print("=" * 50)

        messagebox.showinfo(
            "Done",
            f"Converted {len(converter.frames)} frame(s).\nSaved to:\n{csv_path}",
        )
    except Exception as e:
        print(f"\nERROR: {e}")
        messagebox.showerror("Error", str(e))
        raise


if __name__ == "__main__":
    main()
