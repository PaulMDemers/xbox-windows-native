"""Author749 from source-only747 frontend and748 probe; never reuse runtimes."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-crtc-end747';C=K.parent/'crtc-total748'
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction747.c','bridge.S','fixture.S','link.ld','Makefile','payload_build.py','host_build004.py','relocate003.py','cpu002.py','integration004.py','optical_oracle.py','optical_review002.py','build004.py','page_review002.py','plan_review002.py','linked_review002.py','physical002.py']
for n in names:
 s=(O/n).read_text().replace('native-crtc-end747','native-crtc-total749').replace('747','749')
 # Read text normalizes frozen743 CRCRLF; fresh747 code uses LF only.
 if n=='integration004.py':s='\n'.join(l for l in s.splitlines() if l.strip())+'\n'
 (K/n.replace('747','749')).write_text(s,newline='\n')
for n in ['probe.c','probe.h']:
 s=(C/n).read_text().replace('748','749')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
# Actual ELF function isolation uses the fully checked748 transaction harness,
# replacing only its COFF loader/entry and native CPU admission assumptions.
s=(C/'model.py').read_text().replace('748','749').replace('COFF','native ELF').replace('build001','payload001').replace("out=K/'model001.json'","out=K/'model001.json'")
s=s.replace("b=(P/'probe.obj').read_bytes()", "b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')", "'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe749']","sy['probe749']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20')
s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
oldoff='0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52b4,0x52c0,0x52c8,0x52bc,0x52cc,0x5170,0x512c'
newoff='0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x52d0,0x52dc,0x52e0,0x5170,0x512c,0x52ec'
for name in ['bridge.S','optical_review002.py']:
 p=K/name;s=p.read_text();assert oldoff[2:] in s;p.write_text(s.replace(oldoff[2:],newoff[2:]),newline='\n')
p=K/'physical002.py';s=p.read_text().replace('CR04 and CR05 bytes','CR04, CR05 and CR00 bytes');p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent747':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent748':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'native CR00 after prefix/H7/CR04/CR05;124word result,13 selected optical rows'},indent=2)+'\n',newline='\n')
print('Prepared749 source only')
