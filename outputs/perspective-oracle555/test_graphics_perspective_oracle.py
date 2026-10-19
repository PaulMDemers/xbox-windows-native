# SPDX-License-Identifier: MIT
"""Independent ray/plane reference and deliberately wrong image controls."""
from fractions import Fraction as F
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_perspective_oracle as g


def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def ray_uv(triangle,uv,p):
    # Object-space ray/plane intersection; no screen barycentrics, reciprocal-W
    # interpolation, or oracle projection helper used in this reference.
    direction=(F(p[0],32)-1,1-F(p[1],32),F(1))
    a,b,c=triangle;e0,e1=sub(b,a),sub(c,a);normal=cross(e0,e1)
    distance=dot(normal,a)/dot(normal,direction)
    q=sub(tuple(distance*d for d in direction),a)
    aa,ab,bb=dot(e0,e0),dot(e0,e1),dot(e1,e1)
    determinant=aa*bb-ab*ab
    s=(dot(q,e0)*bb-dot(q,e1)*ab)/determinant
    t=(dot(q,e1)*aa-dot(q,e0)*ab)/determinant
    return tuple((1-s-t)*uv[0][j]+s*uv[1][j]+t*uv[2][j] for j in range(2))


def capture(affine=False):
    return b''.join(struct.pack('<I',min(allowed)) for i in range(5)
                    for allowed,_ in g.pixels_for_stage(i,affine))


class OracleTests(unittest.TestCase):
    def test_ray_reference(self):
        count=0
        for stage in range(5):
            spec=g.geometry(stage)
            for triangle in spec['triangles']:
                points=g.project(triangle,spec['matrices'])
                for y in range(9,56,3):
                    for x in range(5,60,3):
                        if g.coverage(points,(x,y))=='in':
                            self.assertEqual(g.interpolate(points,spec['uv'],(x,y)),ray_uv(triangle,spec['uv'],(x,y)))
                            count+=1
        self.assertGreater(count,250)

    def test_fixed_footprint_scale_and_constant_control(self):
        shape=None
        for stage in range(5):
            spec=g.geometry(stage)
            got=tuple(tuple(p[:2] for p in g.project(t,spec['matrices'])) for t in spec['triangles'])
            if shape is None:shape=got
            self.assertEqual(got,shape)
        self.assertEqual(g.pixels_for_stage(0),g.pixels_for_stage(0,True))
        self.assertEqual(g.pixels_for_stage(1),g.pixels_for_stage(4))

    def test_robust_affine_discrimination(self):
        for stage in (1,2,3,4):
            count=sum(not(a & b) for (a,_),(b,_) in zip(g.pixels_for_stage(stage),g.pixels_for_stage(stage,True)))
            self.assertGreater(count,25,(stage,count))

    def test_synthetic_good_and_wrong_images(self):
        clear=struct.pack('<I',g.BG)*20480;source=g.sources(False);good=capture()
        self.assertTrue(g.validate(clear,good,source,source,False)['host_oracle_accepted'])
        for bad in (capture(True),clear,good[:-4],good+good[:4],good[16384:]+good[:16384]):
            with self.assertRaises(ValueError):g.validate(clear,bad,source,source,False)
        for before,after in ((source[:-1],source),(source,source[:-1]),(source,g.sources(True))):
            with self.assertRaises(ValueError):g.validate(clear,good,before,after,False)

    def test_bad_geometry_and_interior_pixel(self):
        for stage in (-1,5,True):
            with self.assertRaises(ValueError):g.geometry(stage)
        good=bytearray(capture());clear=struct.pack('<I',g.BG)*20480;source=g.sources(False)
        index=next(i for i,(_,tag) in enumerate(g.pixels_for_stage(1)) if tag=='interior')
        struct.pack_into('<I',good,16384+index*4,g.BG)
        with self.assertRaises(ValueError):g.validate(clear,good,source,source,False)


if __name__=='__main__':unittest.main()
