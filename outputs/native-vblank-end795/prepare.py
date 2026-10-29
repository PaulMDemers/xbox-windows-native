"""Fresh native795 from closed793 frontend and closed794 probe sources only."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vtotal-low793';C=K.parent/'crtc-vblank-end794'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
layout={'20480':'21504','20479':'21503','20481':'21505','0x5000':'0x5400','0x6000':'0x6400','0x6004':'0x6404','0x603c':'0x643c','0x6040':'0x6440','0x68d8':'0x6d50','0x8d8':'0x950','2200':'2320','550':'580'}
def remap(s):return re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,layout))+r')(?![0-9a-zA-Z])',lambda m:layout[m[0]],s)
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction793.c','bridge.S','fixture.S','link.ld','Makefile','payload_build005.py','host_build005.py','relocate003.py','relocate004.py','cpu002.py','integration008.py','optical_oracle.py','optical_review002.py','build008.py','page_review005.py','page_boundary006.py','plan_review003.py','linked_review004.py','physical006.py','link_review008.py']
old=','.join(hex(i) for i in [0x8d4]+[0x6040+4*j for j in [30,100,108,261,435,465,495,525,520,523,524]])
offsets=[0,0x8d4]+[0x6440+4*i for i in [30,100,108,435,465,495,525,555,550,553,554]]
for n in names:
 s=ns((O/n).read_text(),'793','795').replace('native-vtotal-low795','native-vblank-end795')
 if n in ['bridge.S','optical_review002.py']:
  assert old in s;s=s.replace(old,'OFFSETS_PLACEHOLDER')
 s=remap(s).replace('OFFSETS_PLACEHOLDER',','.join(hex(i) for i in offsets[1:]))
 if n=='integration008.py':s=s.replace("'<550I'","'<580I'")
 if n in ['page_review005.py','page_boundary006.py']:s=s.replace('payloadptr+21504==0x208000','payloadptr+21504==0x208400')
 if n=='link_review008.py':s=s.replace("'integration004','cpu-run001'","'integration006','cpu-run002'")
 if n=='physical006.py':s=s.replace('CR06 vertical-total low byte','CR16 vertical blank-end').replace('CR06 EC/0C/EC with eight neighbors and own recovery before CR07','CR16 ED/8C/ED preserving bit7, eight neighbors and own recovery before CR06')
 with (K/n.replace('793','795')).open('x',newline='\n') as f:f.write(s)
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'794','795')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'794','795').replace('COFF','native ELF').replace('build001','payload005')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe795']","sy['probe795']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
(K/'.gitignore').write_text('__pycache__/\nmodel001.json\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent793':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent794':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'candidate_layout':layout,'delta':'CR16 ED/8C/ED after CR06; restore first.580words2320bytes.21KiB payload,2KiB stack aboveIDT; independent actual memory and instruction checks required.','optical_offsets':offsets},indent=2)+'\n')
print('Prepared795 source only; no hardware access')
