# SPDX-License-Identifier: MIT
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_triangle as g


class TriangleTests(unittest.TestCase):
    def frames(self):
        clear=bytearray(struct.pack('<I',g.BG)*4096)
        draw=bytearray(clear)
        for y in range(8,56):
            for x in range(8,56-y+8):
                struct.pack_into('<I',draw,(y*64+x)*4,g.FG)
        return clear,draw

    def test_oracle_and_each_asserted_pixel(self):
        a,b=self.frames()
        r=g.pixels(a,b)
        self.assertEqual(r['clear_pixels'],4096)
        self.assertGreater(r['interior_pixels'],500)
        for y in range(64):
            for x in range(64):
                at=(y*64+x)*4
                a[at]^=1
                with self.assertRaises(ValueError):g.pixels(a,b)
                a[at]^=1
                b[at]^=1
                with self.assertRaises(ValueError):g.pixels(a,b)
                b[at]^=1

    def test_missing_triangle_and_lengths(self):
        a,b=self.frames()
        for x,y in [(a,a),(a[:-1],b),(a,b+b'\0'),(b,a)]:
            with self.assertRaises(ValueError):g.pixels(x,y)

    def test_unused_high_byte(self):
        a,b=self.frames()
        for i in range(3,len(a),4):a[i]=127;b[i]=201
        self.assertTrue(g.pixels(a,b))


if __name__=='__main__':unittest.main()
