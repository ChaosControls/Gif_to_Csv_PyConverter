"""
GIF to 32x64 LED matrix converter.

Array coordinate system (1-indexed):
  row  1 = bottom row,  row 32 = top row
  col  1 = left column, col 64 = right column

  array[1,  1] = bottom-left   pixel
  array[32, 1] = top-left      pixel
  array[1, 64] = bottom-right  pixel
  array[32,64] = top-right     pixel

PIL images are (0,0) = top-left, so the mapping is:
  pil_x = col - 1
  pil_y = HEIGHT - row          (row 1 -> pil_y 31, row 32 -> pil_y 0)

UDINT formula: (Blue * 65536) + (Green * 256) + Red
"""

import csv

from PIL import Image, ImageSequence


WIDTH = 64
HEIGHT = 32


class GIFConverter:

    def __init__(self):
        self.frames: list[Image.Image] = []
        self.durations: list[int] = []  # per-frame duration in ms

    def load_gif(self, path: str) -> None:
        gif = Image.open(path)
        self.frames = []
        self.durations = []
        for frame in ImageSequence.Iterator(gif):
            duration = frame.info.get("duration", 100)
            resized = frame.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
            self.frames.append(resized)
            self.durations.append(int(duration))

    @staticmethod
    def _to_udint(r: int, g: int, b: int) -> int:
        return (b * 65536) + (g * 256) + r

    def get_frame_array(self, frame_index: int) -> list[list[int]]:
        """
        Return a 2D list indexed as array[row_0][col_0] (0-based internally),
        where row_0=0 corresponds to logical row 1 (bottom) and
        row_0=31 corresponds to logical row 32 (top).
        """
        frame = self.frames[frame_index]
        result = []
        for row in range(1, HEIGHT + 1):        # 1 (bottom) .. 32 (top)
            pil_y = HEIGHT - row                 # row 1 -> pil_y 31, row 32 -> pil_y 0
            row_data = []
            for col in range(1, WIDTH + 1):      # 1 (left) .. 64 (right)
                pil_x = col - 1
                r, g, b = frame.getpixel((pil_x, pil_y))
                row_data.append(self._to_udint(r, g, b))
            result.append(row_data)
        return result   # result[0] = logical row 1 (bottom), result[31] = logical row 32 (top)

    def export_csv(self, output_path: str) -> None:
        """
        Write one row per GIF frame.
        Columns: time_ms, [1,1], [1,2], ..., [1,64], [2,1], ..., [32,64]
        time_ms is the cumulative elapsed time at the start of each frame.
        """
        header = ["time_ms"]
        for row in range(1, HEIGHT + 1):
            for col in range(1, WIDTH + 1):
                header.append(f"[{row},{col}]")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            elapsed_ms = 0
            for i, duration in enumerate(self.durations):
                frame_array = self.get_frame_array(i)
                row_data = [elapsed_ms]
                for row_0 in range(HEIGHT):
                    row_data.extend(frame_array[row_0])
                writer.writerow(row_data)
                elapsed_ms += duration

        print(f"Exported {len(self.frames)} frames -> {output_path}")
