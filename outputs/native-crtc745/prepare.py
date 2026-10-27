"""Author745 from source-only743 frontend and744 probe; never reuse runtimes."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-horizontal743';C=K.parent/'crtc-start744'
assert not (K/'main.c').exists()
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction743.c','bridge.S','fixture.S','link.ld','Makefile','payload_build.py','host_build004.py','relocate003.py','cpu002.py','integration004.py','optical_oracle.py','optical_review002.py','build004.py','page_review002.py','plan_review002.py','linked_review002.py','physical002.py']
for n in names:
 s=(O/n).read_text().replace('native-horizontal743','native-crtc745').replace('743','745')
 # Read text normalizes frozen743 CRCRLF; fresh745 code uses LF only.
 if n=='integration004.py':s='\n'.join(l for l in s.splitlines() if l.strip())+'\n'
 (K/n.replace('743','745')).write_text(s,newline='\n')
for n in ['probe.c','probe.h']:
 s=(C/n).read_text().replace('744','745')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
# Actual ELF function isolation uses the fully checked744 transaction harness,
# replacing only its COFF loader/entry and native CPU admission assumptions.
s=(C/'model004.py').read_text().replace('744','745').replace('COFF','native ELF').replace('build001','payload001').replace("out=K/'model004.json'","out=K/'model001.json'")
s=s.replace("b=(P/'probe.obj').read_bytes()", "b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')", "'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe745']","sy['probe745']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20')
s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
oldoff='0,0x880,0x8d4,0x5104,0x5110,0x528c,0x5178,0x5290,0x5170,0x512c,0x5130,0x5134,0x5288'
newoff='0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52a0,0x52a4,0x52a8,0x5170,0x512c,0x5130,0x5134'
p=K/'bridge.S';s=p.read_text();assert oldoff in s;p.write_text(s.replace(oldoff,newoff),newline='\n')
p=K/'optical_review002.py';s=p.read_text().replace(oldoff[2:],newoff[2:]);p.write_text(s,newline='\n')
p=K/'cpu002.py';s=p.read_text().replace('[0x7450000d,2,0,0,0,0,0,0,0,0,0,0,0]','[0x7450000d,0,0,0,0,0,0,0,0,0,0,0,0]');p.write_text(s,newline='\n')
p=K/'physical002.py';s=p.read_text().replace('seven horizontal timing words, own saved-value recovery','seven horizontal timing words and one CR04 byte, own saved-value recovery');p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent743':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent744':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model004.py']},'delta':'native CR04 after prefix/H7; 112-word result and 13-row selected optical fields'},indent=2)+'\n',newline='\n')
print('Prepared745 source; no build, stage or hardware launch')
