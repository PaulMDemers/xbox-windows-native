"""Fresh native793 from closed791 frontend and closed792 probe source only."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vtotal-high791';C=K.parent/'crtc-vtotal-low792'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
layout={'19456':'20480','19455':'20479','19457':'20481','0x4c00':'0x5000','0x5c00':'0x6000','0x5c04':'0x6004','0x5c3c':'0x603c','0x5c40':'0x6040','0x6460':'0x68d8','0x6800':'0x7000','0x7000':'0x7800','0x7004':'0x7804','0x860':'0x8d8','2080':'2200'}
def remap(s):return re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,layout))+r')(?![0-9a-zA-Z])',lambda m:layout[m[0]],s)
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction791.c','bridge.S','fixture.S','link.ld','Makefile','payload_build005.py','host_build005.py','relocate003.py','relocate004.py','cpu002.py','integration007.py','optical_oracle.py','optical_review002.py','build007.py','page_review004.py','page_boundary005.py','plan_review003.py','linked_review004.py','physical004.py','link_review008.py']
old=','.join(hex(i) for i in [0x8d4]+[0x5c40+4*j for j in [30,100,108,237,261,435,465,495,490,493,494]])
offsets=[0,0x8d4]+[0x6040+4*i for i in [30,100,108,261,435,465,495,525,520,523,524]]
for n in names:
 s=ns((O/n).read_text(),'791','793').replace('native-vtotal-high793','native-vtotal-low793')
 if n in ['bridge.S','optical_review002.py']:
  assert old in s;s=s.replace(old,'OFFSETS_PLACEHOLDER')
 s=remap(s).replace('OFFSETS_PLACEHOLDER',','.join(hex(i) for i in offsets[1:]))
 if n=='integration007.py':s=s.replace("'<520I'","'<550I'").replace("'admitted_stack_bytes':4096","'admitted_stack_bytes':2048")
 if n=='bridge.S':s=s.replace('4KiB stack page','2KiB stack above IDT')
 if n=='physical004.py':s=s.replace('shared CR07 vertical-total','CR06 vertical-total low byte').replace('same-value write/drop indistinguishable','same-value CR07 write/drop indistinguishable; CR06 EC/0C/EC with eight neighbors and own recovery before CR07')
 with (K/n.replace('791','793')).open('x',newline='\n') as f:f.write(s)
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'792','793')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'792','793').replace('COFF','native ELF').replace('build001','payload005')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe793']","sy['probe793']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n');(K/'.gitignore').write_text('__pycache__/\nmodel001.json\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent791':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent792':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'candidate_layout':layout,'delta':'CR06 totalEC/0C/EC after secondCR07; reverse before secondCR07.550words2200bytes.20KiB payload,2KiB stack aboveIDT; fresh bounds and actual instruction checks required.','optical_offsets':offsets},indent=2)+'\n')
print('Prepared793 source only; no hardware access')
