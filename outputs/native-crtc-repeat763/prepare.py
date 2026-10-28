"""Fresh763 from761 frontend and762 probe/model sources; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-crtc-end761';C=K.parent/'crtc-repeat-blank762'
def ns(s,old,new):return re.sub(r'(?<![0-9])'+old+r'(?![0-9])',new,re.sub(r'0x'+old+r'(?=[0-9a-f]*\b)','0x'+new,s))
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction761.c','bridge.S','fixture.S','link.ld','Makefile','payload_build.py','host_build005.py','relocate003.py','cpu002.py','integration004.py','optical_oracle.py','optical_review002.py','build005.py','page_review003.py','plan_review003.py','linked_review003.py','physical003.py']
for n in names:(K/n.replace('761','763')).write_text(ns((O/n).read_text().replace('native-crtc-end761','native-crtc-repeat763'),'761','763'),newline='\n')
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'762','763')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'762','763').replace('COFF','native ELF').replace('build001','payload001')
s=s.replace("b=(P/'probe.obj').read_bytes()", "b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')", "'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe763']","sy['probe763']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20')
s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
oldoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5378,0x53a4,0x5390,0x539c,0x53a0'
newoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5378,0x53a4,0x53d4,0x53c0,0x53cc,0x53d0'
for n in ['bridge.S','optical_review002.py']:
 p=K/n;s=p.read_text();assert oldoff[2:] in s;p.write_text(s.replace(oldoff[2:],newoff[2:]),newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then CR01 display end','then CR01 display end then later CR02 same-value write');p.write_text(s,newline='\n')
assert 'frequency!=3375000' in (K/'main.c').read_text()
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent761':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent762':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'native laterCR02 own-value capture/target59/recovery;188words5100..53f0; zero5400 retained;13rows finalcode,eight masks,CR02secondtriplet; CR03 and secondCR05 masks unexposed; final success requires all ten masks; same-value dropped write/undo unobservable'},indent=2)+'\n',newline='\n')
