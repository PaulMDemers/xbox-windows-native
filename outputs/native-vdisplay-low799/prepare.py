"""Source-only closed797 frontend and closed798 probe derivation; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vdisplay-high797';C=K.parent/'crtc-vdisplay-low798'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
mapping={'22272':'23040','22271':'23039','22273':'23041','0x5700':'0x5a00','0x6700':'0x6a00','0x6704':'0x6a04','0x673c':'0x6a3c','0x6740':'0x6a40','0x70c8':'0x7440','0x9c8':'0xa40','2440':'2560','0x7100':'0x7500','0x7900':'0x7d00','0x7904':'0x7d04','0x208700':'0x208a00','1792':'768'}
def remap(s):return re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','plan_test002.py','page002.c','page.h','page_tool003.c','transaction.h','transaction797.c','bridge002.S','fixture.S','link.ld','Makefile','payload_build006.py','host_build006.py','relocate003.py','relocate004.py','cpu003.py','integration010.py','optical_oracle.py','optical_review003.py','build010.py','page_review006.py','page_boundary007.py','plan_review003.py','linked_review005.py','physical007.py','link_review010.py']
old=','.join(hex(i) for i in [0x8d4]+[0x6740+4*j for j in [30,100,108,465,495,525,555,585,580,583,584]])
new=[0,0x8d4]+[0x6a40+4*j for j in [30,100,108,495,525,555,585,615,610,613,614]]
for n in names:
 s=ns((O/n).read_text(),'797','799').replace('native-vdisplay-high799','native-vdisplay-low799')
 if n in ['bridge002.S','optical_review003.py']:
  assert old in s;s=s.replace(old,'OFFSET_PLACEHOLDER')
 s=remap(s).replace('OFFSET_PLACEHOLDER',','.join(hex(i) for i in new[1:]))
 if n=='integration010.py':s=s.replace("'<610I'","'<640I'")
 if n=='physical007.py':s=s.replace('CR07 display-end overflow','CR12 display-end low byte').replace('CR07 74/36/74, eight neighbors and own recovery before CR16','CR12 CF/DF/CF, eight neighbors and own recovery before thirdCR07')
 p=K/n.replace('797','799');assert not p.exists();p.write_bytes(s.encode())
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'798','799')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_bytes(s.encode())
s=ns((C/'model002.py').read_text(),'798','799').replace('COFF','native ELF').replace('build001','payload006').replace("out=K/'model002.json'","out=K/'model001.json'")
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}").replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a);s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe799']","sy['probe799']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_bytes(s.encode());(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'__pycache__/\nmodel001.json\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent797':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent798':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model002.py']},'candidate_layout':mapping,'optical_offsets':new,'scope':'Candidate only; fresh payload and full bounds qualification required'},indent=2)+'\n')
print('Prepared799 sources; no hardware access')
