# SPDX-License-Identifier: MIT
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_sample as g


def fixture(rung='02'):
    f=dict(schema='xwn-graphics-ladder-1',rung=rung,backend='default',display='quiet',
           visual='UNVERIFIED',scope='user-mode-sample',exit='0',end='complete',
           result='INVENTORY_OK' if rung=='01' else 'PIXELS_OK')
    f.update({'os.api.major':'5','os.api.minor':'0','os.api.build':'2195','os.api.platform':'2',
              'window.create':'1','pixels.mismatches':'0'})
    if rung=='00':
        f.update({'gdi.'+name:'1' for name in ('dc','dib','select','blit','flush','cleanup')})
    else:
        f.update({key:'1' for key in ('ddraw.load','ddraw.entry','ddraw.unload')})
        f.update({key:'00000000' for key in ('ddraw.create','ddraw.cooperative','ddraw.caps','ddraw.mode')})
        for owner in ('hardware','hel'):
            for name in ('dwCaps','dwCaps2','dwCKeyCaps','dwFXCaps','dwPalCaps','dwVidMemTotal','dwVidMemFree'):
                f['caps.'+owner+'.'+name]='0'
        f.update({'mode.width':'1280','mode.height':'720','mode.bpp':'32','release.ddraw':'0'})
    if rung=='02':
        f.update({key:'00000000' for key in ('surface.source.create','surface.dest.create','surface.blit')})
        for owner,pitch in (('source',256),('dest',384)):
            f['release.'+owner]='0'
            for phase in ('write','read'):
                prefix=owner+'.'+phase
                f.update({prefix+'.lock':'00000000',prefix+'.unlock':'00000000',
                          prefix+'.layout':'1',prefix+'.pitch':str(pitch)})
    return f


def encode(fields):
    return ('\r\n'.join(k+'='+v for k,v in fields.items() if k!='end')+'\r\nend='+fields['end']+'\r\n').encode('ascii')


class GraphicsEvidence(unittest.TestCase):
    def test_all_rungs_and_scope(self):
        for rung in ('00','01','02'):
            f=g.decode(encode(fixture(rung)))
            s,d=(None,None) if rung=='01' else g.expected()
            result=g.validate(f,s,d,0)
            self.assertFalse(result['hardware_acceleration_proved'])
            self.assertFalse(result['nt5_or_xbox_qualified'])
            self.assertFalse(result['visual_qualified'])

    def test_terminal_identity_and_exit_negatives(self):
        f=fixture()
        for key,value in [('schema','2'),('rung','99'),('backend','gpu'),('display','auto'),
                          ('visual','PASS'),('exit','1'),('scope','xbox-qualified'),
                          ('end','pending'),('backend','hal')]:
            x=dict(f); x[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError): g.decode(encode(x))
        raw=encode(f)
        for bad in (raw[:-18],raw+b'exit=0\r\n',raw+b'extra=1\r\n',b'',raw+b'\x80',b'x'*32769):
            with self.assertRaises(ValueError): g.decode(bad)
        with self.assertRaises(ValueError): g.validate(f,*g.expected(),process_exit=3221225477)

    def test_every_required_operation_removed(self):
        for rung in ('00','01','02'):
            f=fixture(rung)
            s,d=(None,None) if rung=='01' else g.expected()
            metadata={'schema','rung','backend','display','visual','scope','exit','end','pixels.mismatches'}
            for key in f.keys()-metadata:
                x=dict(f); del x[key]
                with self.subTest(rung=rung,key=key),self.assertRaises(ValueError): g.validate(x,s,d)

    def test_hresult_pitch_layout_and_readback_negatives(self):
        f=fixture(); source,dest=g.expected()
        for key in ('surface.blit','source.read.lock','source.read.unlock','dest.write.unlock'):
            x=dict(f); x[key]='8876021C'
            with self.assertRaises(ValueError): g.validate(x,source,dest)
        for pitch in ('-256','0','255','258','65540'):
            x=dict(f); x['source.read.pitch']=pitch
            with self.assertRaises(ValueError): g.validate(x,source,dest)
        x=dict(f); x['dest.read.layout']='0'
        with self.assertRaises(ValueError): g.validate(x,source,dest)
        for a,b in ((source[:-1],dest),(source,dest+b'\0'),(dest,source)):
            with self.assertRaises(ValueError): g.validate(f,a,b)
        # Both the copied rectangle and untouched border must be checked.
        points=(0,3,31,1023,((10*96+8)*4),((41*96+55)*4),len(dest)-1)
        for pos in points:
            x=bytearray(dest); x[pos]^=1
            with self.assertRaises(ValueError): g.validate(f,source,bytes(x))
        for pos in (0,3,64*4-1,len(source)-1):
            x=bytearray(source); x[pos]^=1
            with self.assertRaises(ValueError): g.validate(f,bytes(x),dest)

    def test_oracle_landmarks(self):
        s,d=g.expected()
        self.assertEqual((len(s),len(d)),(12288,30720))
        self.assertEqual(s[:4],b'\0'*4)
        self.assertEqual(s[(4*64+3)*4:(4*64+3)*4+4],bytes((97,59,63,0)))
        self.assertEqual(d[(10*96+8)*4:(10*96+8)*4+4],bytes((97,59,63,0)))
        self.assertEqual(d[:4],bytes((0x47,0x29,0x13,0)))


if __name__=='__main__':
    unittest.main()
