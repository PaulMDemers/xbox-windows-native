"""Fresh native791 source-only derivative; no closed runtime access or hardware action."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vsync-low789';C=K.parent/'crtc-vtotal-high790'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
layout={'18432':'19456','18431':'19455','18433':'19457','0x4800':'0x4c00','0x5800':'0x5c00','0x5804':'0x5c04','0x583c':'0x5c3c','0x5840':'0x5c40','0x5fe8':'0x6460','0x6000':'0x6800','0x6800':'0x7000','0x6804':'0x7004','0x7e8':'0x860','1960':'2080','6144':'4096'}
def remap(s):return re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,layout))+r')(?![0-9a-zA-Z])',lambda m:layout[m[0]],s)
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction789.c','bridge.S','fixture.S','link.ld','Makefile','payload_build005.py','host_build005.py','relocate003.py','relocate004.py','cpu002.py','integration007.py','optical_oracle.py','optical_review002.py','build007.py','page_review004.py','page_boundary005.py','plan_review003.py','linked_review004.py','physical004.py','link_review008.py']
old=','.join(hex(i) for i in [0x8d4]+[0x5840+4*j for j in [30,100,108,237,261,285,435,465,460,463,464]])
offsets=[0,0x8d4]+[0x5c40+4*i for i in [30,100,108,237,261,435,465,495,490,493,494]]
for n in names:
 s=ns((O/n).read_text(),'789','791').replace('native-vsync-low791','native-vtotal-high791')
 if n in ['bridge.S','optical_review002.py']:
  assert old in s;s=s.replace(old,'OFFSETS_PLACEHOLDER')
 s=remap(s).replace('OFFSETS_PLACEHOLDER',','.join(hex(i) for i in offsets[1:]))
 if n=='integration007.py':s=s.replace("'<490I'","'<520I'")
 if n=='bridge.S':s=s.replace('6KiB stack across two pages','4KiB stack page')
 if n=='physical004.py':
  s=s.replace('CR10 sync-start low-byte','shared CR07 vertical-total').replace('CR10 D4/E9/D4 with eight preserved CRTC neighbors','CR10 D4/E9/D4 followed by CR07 vertical-total74/74/74 with eight preserved CRTC neighbors; same-value write/drop indistinguishable')
 with (K/n.replace('789','791')).open('x',newline='\n') as f:f.write(s)
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'790','791')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'790','791').replace('COFF','native ELF').replace('build001','payload005')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe791']","sy['probe791']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'.gitignore').write_text('__pycache__/\nmodel001.json\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent789':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent790':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'candidate_layout':layout,'delta':'Shared CR07 verticaltotal74/74/74 afterCR10, reverse beforeCR10/earlierCR07; same-value limitation.520words2080bytes.19KiB payload,4KiB stack; all require fresh bounds and actual instruction verification.','optical_offsets':offsets},indent=2)+'\n')
print('Prepared791 source-only candidate; no hardware access')
