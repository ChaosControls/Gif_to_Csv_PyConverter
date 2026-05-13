"""Sanity checks for coordinate mapping and UDINT formula."""

from PIL import Image
from converter import GIFConverter, WIDTH, HEIGHT


def make_test_converter() -> GIFConverter:
    """
    Build a converter with one synthetic frame where each pixel's colour
    directly encodes its PIL coordinates: R=pil_x, G=pil_y, B=0.
    Injected directly to avoid GIF palette quantisation.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    for pil_y in range(HEIGHT):
        for pil_x in range(WIDTH):
            img.putpixel((pil_x, pil_y), (pil_x, pil_y, 0))

    c = GIFConverter()
    c.frames = [img]
    c.durations = [100]
    return c


def test_udint():
    r, g, b = 1, 2, 3
    expected = (3 * 65536) + (2 * 256) + 1  # 197121
    assert GIFConverter._to_udint(r, g, b) == expected
    print("PASS: UDINT formula")


def test_coordinate_mapping():
    c = make_test_converter()
    arr = c.get_frame_array(0)
    # UDINT for colour (pil_x, pil_y, 0) = (0*65536) + (pil_y*256) + pil_x

    # array[1,1]  = bottom-left  -> pil_x=0,  pil_y=31
    assert arr[0][0]   == 31 * 256 + 0,  f"bottom-left  got {arr[0][0]}"
    print("PASS: array[1,1]  = bottom-left")

    # array[32,1] = top-left     -> pil_x=0,  pil_y=0
    assert arr[31][0]  == 0 * 256 + 0,   f"top-left     got {arr[31][0]}"
    print("PASS: array[32,1] = top-left")

    # array[1,64] = bottom-right -> pil_x=63, pil_y=31
    assert arr[0][63]  == 31 * 256 + 63, f"bottom-right got {arr[0][63]}"
    print("PASS: array[1,64] = bottom-right")

    # array[32,64]= top-right    -> pil_x=63, pil_y=0
    assert arr[31][63] == 0 * 256 + 63,  f"top-right    got {arr[31][63]}"
    print("PASS: array[32,64]= top-right")


if __name__ == "__main__":
    test_udint()
    test_coordinate_mapping()
    print("\nAll tests passed.")
