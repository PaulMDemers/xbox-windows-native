"""Source-only777 from closed774 frontend and qualified776 probe; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vertical-total774';C=K.parent/'vertical-crtc776'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction774.c','bridge.S','fixture.S','link.ld','Makefile','payload_build002.py','host_build005.py','relocate003.py','cpu002.py','integration005.py','optical_oracle.py','optical_review002.py','build006.py','page_review003.py','plan_review003.py','linked_review004.py','physical003.py','audit_collection002.py']
for n in names:
 s=ns((O/n).read_text(encoding='utf-8').replace('native-vertical-total774','native-vertical-crtc777'),'774','777')
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x560)','memset(p+0x5000,0,0x5d8)')
 (K/n.replace('774','777')).write_text(s,encoding='utf-8',newline='\n')
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'776','777')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'776','777').replace('COFF','native ELF').replace('build001','payload002')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe777']","sy['probe777']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
old='0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x54b4,0x5514,0x5500,0x550c,0x5510'
new='0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x54b4,0x5514,0x5574,0x5560,0x556c,0x5570'
for n in ['bridge.S','optical_review002.py']:
 p=K/n;s=p.read_text();assert old in s;p.write_text(s.replace(old,new),newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then NVVDISPEND and NVVTOTAL749/524/749 with six preserved neighbors','then NVVDISPEND,NVVTOTAL and NVVCRTC719/479/719 with eight preserved neighbors');p.write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent774':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent776':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'NVVCRTC719/479/719,310words5100..55d8; initialized55d8. Payload extent14080ends4700 retained subject to fresh build bound.13rows finalcode,eight masks,CRTC triplet; eight masks omitted raw; final requiresall16.'},indent=2)+'\n')
print('Prepared777 source-only native candidate; no launch')
