"""Independent image contract: binary strings into bounded pixel-row slices."""
import struct

def paint_report(image, words):
    assert len(image) == 1280 * 720 * 4 and len(words) == 13
    gray = struct.pack('<I', 0xff808080)
    black = struct.pack('<I', 0xff000000)
    white = struct.pack('<I', 0xffffffff)
    for y in range(104, 640):
        image[(y * 1280 + 112) * 4:(y * 1280 + 1168) * 4] = gray * 1056
    for row, value in enumerate(words):
        assert 0 <= value <= 0xffffffff
        line = bytearray(gray * 1056)
        for column, digit in enumerate(format(value, '032b')):
            start = (16 + column * 32) * 4
            line[start:start + 80] = (white if digit == '1' else black) * 20
        for y in range(120 + row * 40, 140 + row * 40):
            image[(y * 1280 + 112) * 4:(y * 1280 + 1168) * 4] = line
