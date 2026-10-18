# SPDX-License-Identifier: MIT
"""Synthetic host-only scene discriminators; no captured guest inputs."""
from fractions import Fraction as F
import struct
import unittest
import oracle as o


def reference_frame(stage, identity_world=False, swap_layers=False):
    g=o.geometry(stage)
    if identity_world:g['matrices'][0][3][0]=0
    triangles=[o.project(t,g['matrices']) for t in g['triangles']]
    data=bytearray(struct.pack('<I',o.BG)*4096)
    if not g['clear_z']:return data
    for y in range(64):
        for x in range(64):
            layers=[]
            for layer,points in enumerate(triangles):
                u,v=o.uv(points,(x,y))
                if u>=0 and v>=0 and u+v<=1:layers.append((layer,u,v))
            if layers:
                chosen=min(layers,key=lambda row:triangles[row[0]][0][2]) if g['z_enabled'] else layers[-1]
                layer,u,v=chosen
                if swap_layers:layer=1-layer
                color=o.PALETTES[layer][2*int(v>=F(1,2))+int(u>=F(1,2))]
                struct.pack_into('<I',data,(y*64+x)*4,color)
    return data


def fixture():
    return (struct.pack('<I',o.BG)*(5*4096),
            b''.join(reference_frame(i) for i in range(5)),o.sources(False))


class SceneOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for stage in range(5):o.pixels_for_stage(stage)
        cls.clear,cls.draw,cls.source=fixture()

    def test_literal_projection(self):
        g=o.geometry(0);p=[o.project(t,g['matrices']) for t in g['triangles']]
        self.assertEqual(p[0],((F(64,5),F(16),F(2,5),F(5,4)),
                              (F(256,5),F(16),F(2,5),F(5,4)),
                              (F(64,5),F(272,5),F(2,5),F(5,4))))
        self.assertEqual(p[1],((F(88,3),F(56,3),F(2,3),F(3,2)),
                              (F(184,3),F(56,3),F(2,3),F(3,2)),
                              (F(88,3),F(152,3),F(2,3),F(3,2))))
        moved=o.geometry(4);p=o.project(moved['triangles'][0],moved['matrices'])
        self.assertEqual([v[0] for v in p],[F(32,5),F(224,5),F(32,5)])
        for i in range(5):
            mask=o.pixels_for_stage(i)
            self.assertEqual(len(mask),4096)
            if i!=3:
                for tag in ('near','far'):
                    self.assertGreaterEqual(sum(t==tag for _,t in mask),20)

    def test_positive_and_pixel_mutations(self):
        self.assertTrue(o.validate(self.clear,self.draw,self.source,self.source,False)['host_oracle_accepted'])
        # Three invalid RGB words at every pixel, including declared bands.
        for stage in range(5):
            for index in range(4096):
                for value in (0x123456,0x654321,0xabcdef):
                    with self.assertRaises(ValueError):o.validate_pixel(stage,index,value)
        # X is explicitly not RGB; varying it cannot create a failure claim.
        high=bytearray(self.draw)
        for index in range(3,len(high),4):high[index]=0x7f
        self.assertTrue(o.validate(self.clear,high,self.source,self.source,False)['host_oracle_accepted'])

    def test_different_scene_discriminators(self):
        # The two order controls must agree with depth enabled.
        self.assertEqual(self.draw[:16384],self.draw[16384:32768])
        # Each of these intentionally wrong, still plausible images must fail.
        for target,source in ((0,2),(1,2),(2,0),(3,0),(4,0),(0,3)):
            bad=bytearray(self.draw)
            bad[target*16384:(target+1)*16384]=self.draw[source*16384:(source+1)*16384]
            with self.assertRaises(ValueError,msg=(target,source)):
                o.validate(self.clear,bad,self.source,self.source,False)
        for changed in (reference_frame(0,identity_world=True),reference_frame(0,swap_layers=True)):
            bad=changed+self.draw[16384:]
            with self.assertRaises(ValueError):o.validate(self.clear,bad,self.source,self.source,False)
        # No missing primitive/clear-only frame can pass either rendered order case.
        for stage in (0,1,2,4):
            bad=bytearray(self.draw);bad[stage*16384:(stage+1)*16384]=self.clear[:16384]
            with self.assertRaises(ValueError):o.validate(self.clear,bad,self.source,self.source,False)

    def test_literal_pixels_and_texture_discriminators(self):
        # Hand-derived screen-space witnesses: the overlap at (36,24) belongs
        # to near quadrant1 with depth, but far quadrant0 without depth.
        for stage,x,y,color in ((0,24,24,0x206040),(0,48,24,0xc04080),
                                (0,36,24,0x40c080),(1,36,24,0x40c080),
                                (2,36,24,0x802060),(3,36,24,0x102030),
                                (0,28,24,0x206040),(4,28,24,0x40c080)):
            self.assertEqual(o.pixels_for_stage(stage)[y*64+x][0],frozenset((color,)))
            self.assertEqual(struct.unpack_from('<I',self.draw,stage*16384+(y*64+x)*4)[0],color)
        # A constant texture or missing primitive must not survive merely
        # because its geometry and the other layer look plausible.
        for layer,tag in enumerate(('near','far')):
            for constant in (o.BG,*o.PALETTES[layer]):
                bad=bytearray(self.draw)
                for index,(_,region) in enumerate(o.pixels_for_stage(0)):
                    if region==tag:struct.pack_into('<I',bad,index*4,constant)
                with self.assertRaises(ValueError,msg=(tag,constant)):
                    o.validate(self.clear,bad,self.source,self.source,False)

    def test_sources_extents_and_metadata_types(self):
        for alpha in (False,True):
            good=o.sources(alpha);o.validate_sources(good,good,alpha)
            for index in range(len(good)):
                bad=bytearray(good);bad[index]^=1
                for before,after in ((bad,good),(good,bad)):
                    with self.assertRaises(ValueError):o.validate_sources(before,after,alpha)
        for alpha in (0,1,None,'false'):
            with self.assertRaises(ValueError):o.sources(alpha)
        for stage in (-1,5,True,None):
            with self.assertRaises(ValueError):o.pixels_for_stage(stage)
        for index in (-1,4096,True,None):
            with self.assertRaises(ValueError):o.validate_pixel(0,index,o.BG)
        for value in (-1,2**32,True,None):
            with self.assertRaises(ValueError):o.validate_pixel(0,0,value)
        for a,b in ((self.clear[:-1],self.draw),(self.clear,self.draw+b'X')):
            with self.assertRaises(ValueError):o.validate(a,b,self.source,self.source,False)


if __name__=='__main__':unittest.main()
