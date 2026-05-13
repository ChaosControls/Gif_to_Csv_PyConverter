"""
GIF to 32x64 LED Converter — entry point.

Usage:
    python main.py <input.gif> <output.csv>
"""

import sys

from converter import GIFConverter


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input.gif> <output.csv>")
        sys.exit(1)

    gif_path, csv_path = sys.argv[1], sys.argv[2]

    converter = GIFConverter()

    print(f"Loading {gif_path} ...")
    converter.load_gif(gif_path)
    print(f"  {len(converter.frames)} frame(s) found")

    print(f"Exporting to {csv_path} ...")
    converter.export_csv(csv_path)


if __name__ == "__main__":
    main()
