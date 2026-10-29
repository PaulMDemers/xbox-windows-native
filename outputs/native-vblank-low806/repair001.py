"""Preserve failed size build and correct a nonexistent CPU-flags member."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'failure':'measure001 compiler rejected nonexistent result806.flags member; no binary or launch', 'failed_receipt_sha256':sha(K/'measure001.json'),'before':{},'after':{}}
for n in ['probe-native.c','probe-compact-native.c','probe-shared-native.c']:
 p=K/n;r['before'][n]=sha(p);s=p.read_text();assert ' || (o->flags&0x200)' in s
 # Existing flags_critical guard immediately following this clause checks IF.
 s=s.replace(' || (o->flags&0x200)','');p.write_bytes(s.encode());r['after'][n]=sha(p)
p=K/'measure002.py';assert not p.exists();p.write_bytes((K/'measure001.py').read_bytes().replace(b'measure001',b'measure002'))
(K/'qualification-failure001.json').write_text(json.dumps(r,indent=2)+'\n')
