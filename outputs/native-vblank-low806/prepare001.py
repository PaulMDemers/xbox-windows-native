"""Fresh native806 source derivation and size study, no runtime access."""
from pathlib import Path
import re,json,hashlib,subprocess,sys
K=Path(__file__).resolve().parent; A=K.parent/'native-vblank-overflow804'; B=K.parent/'crtc-vblank-low805'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rename(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x806',p) if i%2 else p.replace(old,'806') for i,p in enumerate(parts))
r={'source_only':True,'physical_access':False,'parents':{},'outputs':{}}
for root,name,dest in [(A,'transaction804.c','transaction806.c'),(A,'transaction.h','transaction.h'),(B,'probe.c','probe-native.c'),(B,'probe.h','probe.h'),(A,'compact001.py','compact001.py'),(A,'measure001.py','measure001.py')]:
 p=root/name; s=rename(p.read_text(), '804' if root==A else '805');r['parents'][str(p.relative_to(K.parent))]=sha(p)
 if dest=='probe-native.c':
  old='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)'
  assert old in s
  s=s.replace(old,'(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (o->flags&0x200) || (o->cr4&0x20)')
 if dest=='measure001.py':
  s=s.replace("'probe-compact-native.c','probe.h'","'probe-compact-native.c','probe-shared-native.c','probe.h'")
  s=s.replace("[('original-native',[]),('compact-native',[]),('compact-no-unwind',['-fno-asynchronous-unwind-tables','-fno-unwind-tables'])]","[('original-native',[]),('compact-native',[]),('shared-native',[]),('shared-no-unwind',['-fno-asynchronous-unwind-tables','-fno-unwind-tables'])]")
  s=s.replace("'probe-native.c' if name=='original-native' else 'probe-compact-native.c'","'probe-native.c' if name=='original-native' else ('probe-compact-native.c' if name=='compact-native' else 'probe-shared-native.c')")
 out=K/dest;assert not out.exists();out.write_bytes(s.encode());r['outputs'][dest]=sha(out)
subprocess.run([sys.executable,'-B',str(K/'compact001.py')],check=True)
s=(K/'probe-compact-native.c').read_text()
for a,b in [('static uint8_t cr(', 'static __attribute__((noinline)) uint8_t cr('),('static void cw(', 'static __attribute__((noinline)) void cw(')]:
 assert a in s;s=s.replace(a,b)
(K/'probe-shared-native.c').write_bytes(s.encode())
r['outputs']['probe-shared-native.c']=sha(K/'probe-shared-native.c')
(K/'derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Fresh806 sources derived; no build, physical access or launch')
