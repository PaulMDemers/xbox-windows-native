"""Use805 device oracle with independent native ELF loader and CPU admission."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-overflow804';B=K.parent/'crtc-vblank-low805'
def rename(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x806',p) if i%2 else p.replace(old,'806') for i,p in enumerate(parts))
s=rename((B/'model005.py').read_text(),'805').replace('COFF','native ELF')
s=s.replace("P=Path('C:/xwn806/build002')","P=Path('C:/xwn806/measure003/original-native')").replace("out=K/'model005.json'","out=K/'model001.json'")
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'native.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0')
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace("symbols['_probe806']","sy['probe806']").replace('count=20000','count=30000')
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or bool(flags&0x200) or cpu4&0x20')
s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
for n,t in [('model001.py',s),('model002.py',s.replace('original-native','shared-native').replace('model001.json','model002.json'))]:
 assert not (K/n).exists();(K/n).write_bytes(t.encode())
s=rename((A/'equivalence001.py').read_text(),'804').replace('894','934').replace('700_dword','730_dword')
(K/'equivalence001.py').write_bytes(s.encode())
