"""Fresh765 from763 frontend and764 probe/model sources; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-crtc-repeat763';C=K.parent/'crtc-reenable764'
def ns(s,old,new):return re.sub(r'(?<![0-9])'+old+r'(?![0-9])',new,re.sub(r'0x'+old+r'(?=[0-9a-f]*\b)','0x'+new,s))
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction763.c','bridge.S','fixture.S','link.ld','Makefile','payload_build.py','host_build005.py','relocate003.py','cpu002.py','integration004.py','optical_oracle.py','optical_review002.py','build005.py','page_review003.py','plan_review003.py','linked_review003.py','physical003.py']
for n in names:(K/n.replace('763','765')).write_text(ns((O/n).read_text().replace('native-crtc-repeat763','native-crtc-reenable765'),'763','765'),newline='\n')
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'764','765')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'764','765').replace('COFF','native ELF').replace('build001','payload001')
s=s.replace("b=(P/'probe.obj').read_bytes()", "b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')", "'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe765']","sy['probe765']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20')
s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
oldoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5378,0x53a4,0x53d4,0x53c0,0x53cc,0x53d0'
newoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x53d4,0x5404,0x53f0,0x53fc,0x5400'
for n in ['bridge.S','optical_review002.py']:
 p=K/n;s=p.read_text();assert oldoff[2:] in s;p.write_text(s.replace(oldoff[2:],newoff[2:]),newline='\n')
p=K/'page002.c';s=p.read_text();assert s.count('memset(p+0x5000,0,0x400)')==1;p.write_text(s.replace('memset(p+0x5000,0,0x400)','memset(p+0x5000,0,0x500)'),newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then later CR02 same-value write','then later CR02 same-value write then CR17 bit7 enable');p.write_text(s,newline='\n')
assert 'frequency!=3375000' in (K/'main.c').read_text()
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent763':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent764':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'native CR17 forward enable63/e3/63;200words5100..5420; initializedend5500;13rows finalcode,eight masks,CR17secondtriplet; CR03,secondCR05,firstCR17 masks unexposed; final requiresall11'},indent=2)+'\n',newline='\n')
