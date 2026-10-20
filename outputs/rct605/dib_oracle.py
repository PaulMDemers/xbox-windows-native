"""Independent integer/signed decoder of bounded raw observer records."""
def decode_header(address,raw,recorded_status):
 assert 0<=address<=0xffffffff and all(0<=v<=0xffffffff for v in raw)
 if not address:assert not raw;return (1,0,0)
 if address>0xfffffffc:assert not raw;return (2,0,0)
 if not raw:assert recorded_status==3;return (3,0,0)
 if len(raw)==1:
  if raw[0]!=40:return (4,0,0)
  if address>0xffffffd8:return (2,0,0)
  assert recorded_status==3;return (3,0,0)
 assert len(raw)==10 and address<=0xffffffd8
 if raw[0]!=40:return (4,0,0)
 signed=lambda x:x if x<2**31 else x-2**32
 width,height=signed(raw[1]),signed(raw[2]);planes=raw[3]&0xffff;bpp=raw[3]>>16
 if width<=0 or height in [0,-2**31]:return (5,0,0)
 if planes!=1:return (6,0,0)
 if bpp not in [1,4,8,16,24,32]:return (7,0,0)
 if raw[4]!=0:return (8,0,0)
 if width>16384 or abs(height)>16384:return (9,0,0)
 stride=4*((width*bpp+31)//32);extent=stride*abs(height)
 if extent>64*1024*1024:return (9,stride,0)
 if raw[5] and not extent<=raw[5]<=64*1024*1024:return (10,stride,extent)
 if raw[8]>(2**bpp if bpp<=8 else 256):return (11,stride,extent)
 return (0,stride,extent)

def validate_headers(r):
 probes=[(i,c) for i,c in r['calls'].items() if c['api']==15]
 expected=[0,0,1,2,3,3,4,5,5,6,7,8,9,10,11]
 assert len(probes)==len(expected)
 for (i,c),status in zip(probes,expected):
  d=r['dibs'][i];assert d['status']==status and c['result']==0x604d1b00
 assert r['dibs'][probes[0][0]]['raw'][2]==0xfffffff8
 assert r['dibs'][probes[1][0]]['raw'][2]==8
 assert r['dibs'][probes[2][0]]['address']==0
 assert r['dibs'][probes[3][0]]['address']==0xffffffff
 unread=r['dibs'][probes[4][0]];trunc=r['dibs'][probes[5][0]]
 assert unread['address']%4096==0 and unread['raw']==[]
 assert trunc['address']==unread['address']-4 and trunc['raw']==[40]
 actual=[(i,c) for i,c in r['calls'].items() if c['api'] in [4,11]]
 assert [r['dibs'][i]['status'] for i,c in actual]==[4]+[0]*68
 for i,c in actual[1:]:
  d=r['dibs'][i];assert d['raw']==[40,8,0xfffffff8,0x200001,0,0,0,0,0,0]
  assert d['stride']==32 and d['extent']==256
