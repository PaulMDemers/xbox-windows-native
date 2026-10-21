"""Synthetic log rejection tests; constructs no hardware programming artifact."""
import copy,hashlib,json
from pathlib import Path
from decode import decode
K=Path(__file__).resolve().parent
f=json.loads((K.parent/'hd-profile310/profile-facts.json').read_text())
v=json.loads((K.parent/'mode-switch631/physical-collection002.json').read_text())['decoded']['stages'][0]
g={'CR':dict(zip(f['crtc_indices'],f['profiles'][0]['crtc'])),'MM':dict(zip(f['mmio_offsets'],f['profiles'][0]['mmio'])),'EN':{}}
for n,x in v['crtc'].items():g['CR'][int(n)]=x
g['CR'][0x19]&=0xe0;g['CR'][0x2d]&=1
for i,x in enumerate(v['fp']):
 off=0x680800+4*i
 if off in g['MM']:g['MM'][off]=x
old=json.loads((K.parent/'hd-matrix309/source-review001.json').read_text())['independent_matrix'][2]
g['EN']=dict(zip([i for i in f['encoder_indices'] if i!=0x6c],old));g['EN'][0x6c]=0x46
def encode(gs):
 lines=['XWN_FACTS632 version=1 kernel=1.0.4034.1 error=0 reads=17']
 for kind,indices,key in [('CR',f['crtc_indices'],'index'),('MM',f['mmio_offsets'],'offset'),('EN',f['encoder_indices'],'index')]:
  w=8 if kind=='MM' else 2
  for i in indices:lines.append(f'{kind} {key}={i:0{w}x} value={gs[kind][i]:0{w}x}')
 return ('\r\n'.join(lines+['COMPLETE error=0 log_ok=1'])+'\r\n').encode()
data=encode(g);assert decode(data)['passed'];rejected=0
def reject(b):
 global rejected
 try:decode(b)
 except (AssertionError,UnicodeError,ValueError,KeyError):rejected+=1
 else:raise AssertionError('Bad fixture accepted')
for i in range(79):
 lines=data.splitlines(keepends=True);reject(b''.join(lines[:i]+lines[i+1:]))
for needle,replacement in [(b'4034',b'4627'),(b'error=0',b'error=1'),(b'reads=17',b'reads=16'),(b'log_ok=1',b'log_ok=0')]:reject(data.replace(needle,replacement))
for index in v['crtc']:
 i=int(index);bit={0x19:0x20,0x2d:1}.get(i,1);bad=copy.deepcopy(g);bad['CR'][i]^=bit;reject(encode(bad))
for i in f['encoder_indices']:
 bad=copy.deepcopy(g);bad['EN'][i]^=1;reject(encode(bad))
for i in range(16):
 off=0x680800+4*i
 if off in g['MM']:bad=copy.deepcopy(g);bad['MM'][off]^=1;reject(encode(bad))
reject(data+data);reject(b'\xff'+data)
r=dict(passed=True,synthetic_positive=True,negative_cases=rejected,actual_physical_facts=False,decoder_sha256=hashlib.sha256((K/'decode.py').read_bytes()).hexdigest())
p=K/'decoder-tests001.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(r)
