"""Source-only774 from closed772 frontend and qualified773 probe; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vertical-end772';C=K.parent/'vertical-total773'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction772.c','bridge.S','fixture.S','link.ld','Makefile','payload_build002.py','host_build005.py','relocate003.py','cpu002.py','integration004.py','optical_oracle.py','optical_review002.py','build005.py','page_review003.py','plan_review003.py','linked_review004.py','physical003.py','audit_collection.py']
for n in names:
 s=ns((O/n).read_text(encoding='utf-8').replace('native-vertical-end772','native-vertical-total774'),'772','774')
 if n in ['main.c','page002.c','page_tool003.c','page_review003.py','bridge.S','payload_build002.py']:s=s.replace('12800','14080').replace('12799','14079')
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x500)','memset(p+0x5000,0,0x560)')
 (K/n.replace('772','774')).write_text(s,encoding='utf-8',newline='\n')
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'773','774')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'773','774').replace('COFF','native ELF').replace('build001','payload002')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe774']","sy['probe774']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
# Keep the eight-mask optical budget: replace raw CR13 mask with prior vertical mask,
# and use the newest mask plus own total triplet. Final success requires all15.
old='0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x5474,0x54b4,0x54a0,0x54ac,0x54b0'
new='0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x54b4,0x5514,0x5500,0x550c,0x5510'
for n in ['bridge.S','optical_review002.py']:
 p=K/n;s=p.read_text();assert old in s;p.write_text(s.replace(old,new),newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then CR13 low stride and NVVDISPEND719/479/719 with six preserved neighbors','then NVVDISPEND and NVVTOTAL749/524/749 with six preserved neighbors');p.write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent772':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent773':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'NVVTOTAL749/524/749,280words5100..5560; initialized5560. Padded payload14080ends4700.13rows finalcode,eight masks,total triplet; seven masks omitted raw; final requiresall15.'},indent=2)+'\n')
print('Prepared774 source-only native candidate; no launch')
