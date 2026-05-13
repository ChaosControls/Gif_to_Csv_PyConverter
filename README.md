# GIF to 32×64 LED CSV Converter

Converts an animated GIF into a CSV file where each row represents one frame of the animation. Each pixel is encoded as a UDINT value and laid out in a 32×64 matrix with a bottom-left origin.

---

## Requirements

- Python 3.10 or newer
- [Pillow](https://python-pillow.org/) (installed via `requirements.txt`)
- `tkinter` (included in the Python standard library)

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/ChaosControls/Gif_to_Csv_PyConverter.git
cd Gif_to_Csv_PyConverter
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## Running the Program

```bash
python main.py
```

The program will guide you through three steps printed in the terminal:

1. **Select your GIF** — a file browser opens so you can navigate to and select any `.gif` file on your computer.
2. **Choose a save location** — a save dialog opens so you can pick a folder and filename for the output `.csv`.
3. **Conversion** — the program loads the GIF, processes every frame, and writes the CSV. Progress is printed to the terminal. A popup confirms when complete.

---

## Output Format

The CSV contains one row per GIF frame.

| Column | Description |
|---|---|
| `time_ms` | Cumulative elapsed time at the start of the frame (milliseconds) |
| `[1,1]` … `[32,64]` | UDINT pixel value for each LED in the matrix |

**Pixel encoding (UDINT)**
```
PixelColor = (Blue × 65536) + (Green × 256) + Red
```

**Array coordinate system**

```
[32,1]  ·  ·  ·  [32,64]   ← top row
  ·                  ·
  ·                  ·
[1,1]   ·  ·  ·   [1,64]   ← bottom row
```

- First index = row, `1` = bottom, `32` = top
- Second index = column, `1` = left, `64` = right
- Total columns in CSV: 1 (time) + 2048 (32 × 64 pixels) = **2049**
