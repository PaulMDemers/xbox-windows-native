"""Restore native entry-IF rejection, then remeasure immutable fresh builds."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'issue':'repair001 removed the nonexistent member but must retain native entry-IF rejection, before probe CLI', 'measurement_only_receipt':sha(K/'measure002.json'),'before':{},'after':{}}
for n in ['probe-native.c','probe-compact-native.c','probe-shared-native.c']:
 p=K/n;r['before'][n]=sha(p);s=p.read_text();a='o->cr3!=0 || (o->cr4&0x20)';assert a in s
 s=s.replace(a,'o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)');p.write_bytes(s.encode());r['after'][n]=sha(p)
(K/'measure003.py').write_bytes((K/'measure002.py').read_bytes().replace(b'measure002',b'measure003'))
(K/'qualification-failure002.json').write_text(json.dumps(r,indent=2)+'\n')
