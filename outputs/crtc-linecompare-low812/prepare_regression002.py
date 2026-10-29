"""Retain809 full prefix oracle against812 compiled object, adding a CR18 boundary check."""
from pathlib import Path
import re,hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1]
parent=W/'outputs/crtc-linecompare-bit809/model006.py'
s=parent.read_text(encoding='utf-8');tail=s[s.index(" v=list(struct.unpack('<790I'"):]
tail=re.sub(r'0x809(?=[0-9a-f]{0,2}\b)','0x812',tail)
tail=tail.replace('actual809','actual812').replace('0x201c58,0x53a8','0x201cd0,0x5330')
head=(K/'model001.py').read_text(encoding='utf-8').split(" v=list(struct.unpack('<820I'")[0]
head=head.replace("out=K/'model001.json'","out=K/'model002.json'")
head=head.replace('Actual812 COFF narrow CR18 tail validation; full prefix regression still required.',
 'Actual812 compiled full inherited prefix regression with independently checked CR18 boundary.')
boundary=''' extra=list(struct.unpack('<30I',c.mem_read(0x201000+790*4,120)))
 # Previous oracle checks every preceding transaction. Remove only the two
 # explicitly checked new CR18 writes before comparing its complete trace.
 tailwrites=[a for a in writes if a[:2]==['cr',24]]
 if extra[2]:
  assert extra[:6]==[255,255,1,255,255,0],(name,extra[:6])
  assert extra[6:]==[v for n in [12,62,64,233,223,223,140,16] for v in [n,n,n]]
  assert tailwrites==[['cr',24,255]]*2
  assert state['cl18writes']==2
  writes=[a for a in writes if a[:2]!=['cr',24]]
 else:
  assert not tailwrites and not state['cl18writes']
  assert extra==[0,0,0,0xffffffff,0xffffffff,0]+[v for _ in range(8) for v in [0,0xffffffff,0xffffffff]],(name,extra)
'''
tail=boundary+tail
out=K/'model002.py';assert not out.exists();out.write_text(head+tail,encoding='utf-8')
(K/'regression-lineage002.json').write_text(json.dumps({'source_only_parent':str(parent.relative_to(W)),
 'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
 'model001_sha256':hashlib.sha256((K/'model001.py').read_bytes()).hexdigest(),
 'harness_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n')
