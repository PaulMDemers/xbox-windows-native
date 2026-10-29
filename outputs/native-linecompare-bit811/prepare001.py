"""Host-only811 sizing; physical admission blocked pending cold-control810 result."""
from pathlib import Path
import re,json,hashlib,subprocess,sys
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-high808';B=K.parent/'crtc-linecompare-bit809'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x811',p) if i%2 else p.replace(old,'811') for i,p in enumerate(parts)).replace('native-linecompare-high811','native-linecompare-bit811')
r=dict(source_only=True,runtime_parent=False,physical_access=False,admitted=False,parents={})
for root,name,dest in [(A,'transaction808.c','transaction811.c'),(A,'transaction.h','transaction.h'),(B,'probe.c','probe-native.c'),(B,'probe.h','probe.h'),(A,'compact001.py','compact001.py'),(A,'measure001.py','measure001.py'),(A,'bitmap001.py','bitmap001.py')]:
 s=ns((root/name).read_text(),'808' if root==A else '809');r['parents'][str((root/name).relative_to(K.parent))]=sha(root/name)
 if dest=='probe-native.c':
  guard='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)';assert s.count(guard)==1
  s=s.replace(guard,'(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 if dest=='bitmap001.py':
  s=s.replace('==760','==790').replace('==398','==416').replace('[0]*24','[0]*25').replace('bits[24]','bits[25]').replace('i<760','i<790')
 assert not (K/dest).exists();(K/dest).write_bytes(s.encode())
subprocess.run([sys.executable,'-B',str(K/'compact001.py')],check=True)
s=(K/'probe-compact-native.c').read_text().replace('static uint8_t cr(','static __attribute__((noinline)) uint8_t cr(').replace('static void cw(','static __attribute__((noinline)) void cw(')
(K/'probe-shared-native.c').write_bytes(s.encode())
subprocess.run([sys.executable,'-B',str(K/'bitmap001.py')],check=True)
(K/'derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
