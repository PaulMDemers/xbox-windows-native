# SPDX-License-Identifier: MIT
import struct,sys,unittest,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_blend as g

def frames():
    images=[]
    for color in (0x00ff00,0x00ff00,0x55aa55,0xaa55aa,0xff00ff,0xff00ff):
        b=bytearray(struct.pack('<I',0x00ff00)*4096)
        for y in range(8,56):
            for x in range(8,64-y):struct.pack_into('<I',b,(y*64+x)*4,color)
        images.append(b)
    return images

def record():
    f={k:'0' for k in g.HRESULTS}
    f.update(schema='xwn-d3d-blend-1',backend='default',scope='offscreen-rgb-software',width='64',height='64',exit='0',result='CAPTURED',end='complete',modules='1',
        **{'os.major':'5','os.minor':'0','os.build':'2195','window.created':'1','ddraw.load':'1','ddraw.entry':'1','ddraw.unload':'1','enum.matches':'1','enum.error':'0','enum.count':'1','vertex.stride':'20','vertex.fvf':'68','modules.ok':'1','modules.end_error':'18','release.device':'0','release.target':'0','release.ddraw':'0','release.d3d':'1','module0.path':b'C:\\WINNT\\system32\\ddraw.dll'.hex(),'module0.bytes':'4096'})
    caps=bytearray(236);caps[196:212]=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356').bytes_le
    for off,v in [(76,16),(80,32),(116,256)]:struct.pack_into('<I',caps,off,v)
    f['device.caps']=caps.hex()
    f['vertices']=b''.join(struct.pack('<ffffI',x,y,.5,1,(a<<24)|0xff00ff) for a in (0,85,170,255,85) for x,y in ((8,8),(56,8),(8,56))).hex()
    for stage,alpha,blend in [('clear',0,1),('a0',0,1),('a85',85,1),('a170',170,1),('a255',255,1),('disabled',85,0)]:
        f.update({stage+'.valid':'1',stage+'.pitch':'256',stage+'.caps':str(0x2840),stage+'.alpha':str(alpha),stage+'.blend':str(blend),stage+'.src':'5',stage+'.dest':'6'})
    return f

def encode(f):return ''.join(k+'='+v+'\r\n' for k,v in f.items()).encode()

class BlendTests(unittest.TestCase):
    def test_discriminators(self):
        images=frames();self.assertTrue(g.validate(encode(record()),images,'default',0)['passed'])
        for dest,source in [(1,4),(2,0),(2,3),(2,4),(3,2),(3,4),(4,2),(5,2)]:
            bad=list(images);bad[dest]=images[source]
            with self.assertRaises(ValueError):g.pixels(*bad)
        for i in range(6):
            bad=list(images);bad[i]=bad[i][:-1]
            with self.assertRaises(ValueError):g.pixels(*bad)
        at=(16*64+16)*4
        for stage,ideal in [(2,0x55aa55),(3,0xaa55aa)]:
            for channel in range(3):
                for delta in (-2,-1,1,2):
                    bad=[bytearray(b) for b in images];bad[stage][at+channel]+=delta
                    if abs(delta)==1:self.assertTrue(g.pixels(*bad))
                    else:
                        with self.assertRaises(ValueError):g.pixels(*bad)
        for frame in images:
            for at in range(3,len(frame),4):frame[at]=123
        self.assertTrue(g.pixels(*images))

    def test_row_channel_coverage(self):
        images=frames()
        # Every row, three x positions, all RGB channels, each of six stages.
        for frame in images:
            for y in range(64):
                for x in (0,16,63):
                    for channel in range(3):
                        at=(y*64+x)*4+channel;frame[at]^=16
                        with self.assertRaises(ValueError):g.pixels(*images)
                        frame[at]^=16

    def test_transport(self):
        f=record();images=frames();raw=encode(f)
        for key in f:
            bad=dict(f);del bad[key]
            for data in (encode(bad),raw+(key+'='+f[key]+'\r\n').encode()):
                with self.assertRaises(ValueError):g.validate(data,images,'default',0)
        for key in g.HRESULTS:
            bad=dict(f);bad[key]='1'
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)
        for i in range(300):
            bad=dict(f);v=bytearray.fromhex(f['vertices']);v[i]^=1;bad['vertices']=v.hex()
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)
        for key,value in [('a0.alpha','255'),('disabled.blend','1'),('a85.src','1'),('a170.dest','0'),('a255.valid','0'),('a0.caps','0'),('a85.pitch','255')]:
            bad=dict(f);bad[key]=value
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)
        for off in (76,80):
            bad=dict(f);caps=bytearray.fromhex(f['device.caps']);struct.pack_into('<I',caps,off,0);bad['device.caps']=caps.hex()
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)

if __name__=='__main__':unittest.main()
