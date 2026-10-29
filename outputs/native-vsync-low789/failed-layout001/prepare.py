"""Fresh native789 candidate from closed787 sources and closed788 probe; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vsync-high787';C=K.parent/'crtc-vsync-low788'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
layout={'16384':'18432','0x5000':'0x5800','0x503c':'0x583c','0x5040':'0x5840','0x5770':'0x5fe8','0x5800':'0x6000','0x6000':'0x6800','0x6004':'0x6804','0x770':'0x7e8'}
def remap(s):return re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,layout))+r')(?![0-9a-zA-Z])',lambda m:layout[m[0]],s)
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction787.c','bridge.S','fixture.S','link.ld','Makefile','payload_build005.py','host_build005.py','relocate003.py','cpu002.py','integration005.py','optical_oracle.py','optical_review002.py','build006.py','page_review003.py','page_boundary004.py','plan_review003.py','linked_review004.py','physical003.py','audit_collection006.py','link_review007.py']
old=','.join(hex(i) for i in [0x8d4]+[0x5040+4*j for j in [30,100,108,237,261,285,405,435,430,433,434]])
offsets=[0,0x8d4]+[0x5840+4*i for i in [30,100,108,237,261,285,435,465,460,463,464]]
new=','.join(hex(i) for i in offsets[1:])
for n in names:
 s=ns((O/n).read_text(),'787','789').replace('native-vsync-high789','native-vsync-low789')
 if n in ['bridge.S','optical_review002.py']:
  assert old in s;s=s.replace(old,new)
 s=remap(s)
 if n=='integration005.py':s=s.replace('op+1840','op+1960').replace("'<460I'","'<490I'")
 if n=='bridge.S':s=s.replace('Touch both stack pages','Touch the endpoints of the 6KiB stack across two pages')
 if n=='link_review007.py':s=s.replace("==15992<=18432","<=18432")
 with (K/n.replace('787','789')).open('x',newline='\n') as f:f.write(s)
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'788','789')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'788','789').replace('COFF','native ELF').replace('build001','payload005')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe789']","sy['probe789']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
p=K/'physical003.py';s=p.read_text().replace('CR07 sync-overflow','CR10 sync-start low-byte').replace('then CR07 F0/74/F0 with eight preserved CRTC neighbors','then CR07 F0/74/F0 followed by CR10 D4/E9/D4 with eight preserved CRTC neighbors');p.write_text(s,newline='\n')
p=K/'audit_collection006.py';s=p.read_text().replace('CR07','CR10').replace('[240,116,240]','[212,233,212]');p.write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent787':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent788':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'candidate_layout':layout,'delta':'CR10 D4/E9/D4;490word result5840..5fe8; nativeCPUguard. Refined from initial proposal: keep32KiB owned allocation; payload18432ends5800, request5800..583c, resultguard5fe8..6000,IDT6000..6800,stack6800..8000 (6KiB across2pages). All require fresh bounds/stack-write qualification.','optical_offsets':offsets},indent=2)+'\n')
print('Prepared789 candidate; no physical access')
