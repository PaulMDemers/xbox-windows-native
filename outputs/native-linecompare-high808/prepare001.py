"""Derive808 from closed806/807 SOURCES only; no runtime access."""
from pathlib import Path
import re,json,hashlib,subprocess,sys
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-low806';B=K.parent/'crtc-linecompare-high807'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x808',p) if i%2 else p.replace(old,'808') for i,p in enumerate(parts)).replace('native-vblank-low808','native-linecompare-high808').replace('crtc-linecompare-high808','native-linecompare-high808')
r=dict(source_only=True,physical_access=False,parents={})
for root,name,dest in [(A,'transaction806.c','transaction808.c'),(A,'transaction.h','transaction.h'),(B,'probe.c','probe-native.c'),(B,'probe.h','probe.h'),(A,'compact001.py','compact001.py'),(A,'measure001.py','measure001.py')]:
 s=ns((root/name).read_text(),'806' if root==A else '807');r['parents'][str((root/name).relative_to(K.parent))]=sha(root/name)
 if dest=='probe-native.c':
  old='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)';assert old in s
  s=s.replace(old,'(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert not (K/dest).exists();(K/dest).write_bytes(s.encode())
subprocess.run([sys.executable,'-B',str(K/'compact001.py')],check=True)
s=(K/'probe-compact-native.c').read_text().replace('static uint8_t cr(','static __attribute__((noinline)) uint8_t cr(').replace('static void cw(','static __attribute__((noinline)) void cw(')
(K/'probe-shared-native.c').write_bytes(s.encode())
(K/'derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('808 sources prepared, no runtime or physical access')
