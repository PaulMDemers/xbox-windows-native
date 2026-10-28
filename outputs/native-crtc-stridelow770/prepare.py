"""Source-only770: reviewed767 frontend plus qualified769 CR13 probe."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-crtc-stride767';C=K.parent/'crtc-stride-cold769'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction767.c','bridge.S','fixture.S','link.ld','Makefile','payload_build.py','host_build005.py','relocate003.py','cpu002.py','integration004.py','optical_oracle.py','optical_review002.py','build005.py','page_review003.py','plan_review003.py','linked_review004.py','physical003.py']
for n in names:(K/n.replace('767','770')).write_text(ns((O/n).read_text(encoding='utf-8').replace('native-crtc-stride767','native-crtc-stridelow770'),'767','770'),encoding='utf-8',newline='\n')
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'769','770')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'769','770').replace('COFF','native ELF').replace('build001','payload001')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe770']","sy['probe770']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
old='0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x5404,0x5434,0x5420,0x542c,0x5430'
new='0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x5434,0x5474,0x5460,0x546c,0x5470'
for n in ['bridge.S','optical_review002.py']:
 p=K/n;s=p.read_text();assert old in s;p.write_text(s.replace(old,new),newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then CR19 upper stride with CR13 read-only','then CR19 upper stride then CR13 low stride80/68/80');p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent767':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent769':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'Native CR13 low stride80/68/80 after CR19=30;232words5100..54a0, initialized5500;13rows finalcode,eight masks,CR13triplet. Five other masks unexposed; final requiresall13.'},indent=2)+'\n')
