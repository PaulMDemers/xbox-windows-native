"""Fresh native797 sources; closed795 frontend and closed796 probe source only."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vblank-end795';C=K.parent/'crtc-vdisplay-high796'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
mapping={'21504':'22016','21503':'22015','21505':'22017','0x5400':'0x5600','0x6400':'0x6600','0x6404':'0x6604','0x643c':'0x663c','0x6440':'0x6640','0x6d50':'0x6fc8','0x950':'0x9c8','2320':'2440','580':'610','0x208400':'0x208600'}
def remap(s):return re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','plan_test002.py','page002.c','page.h','page_tool003.c','transaction.h','transaction795.c','bridge002.S','fixture.S','link.ld','Makefile','payload_build005.py','host_build006.py','relocate003.py','relocate004.py','cpu003.py','integration009.py','optical_oracle.py','optical_review003.py','build009.py','page_review006.py','page_boundary007.py','plan_review003.py','linked_review005.py','physical007.py','link_review009.py']
old=','.join(hex(i) for i in [0x8d4]+[0x6440+4*j for j in [30,100,108,435,465,495,525,555,550,553,554]])
new=[0,0x8d4]+[0x6640+4*j for j in [30,100,108,465,495,525,555,585,580,583,584]]
for n in names:
 s=ns((O/n).read_text(),'795','797').replace('native-vblank-end797','native-vdisplay-high797')
 if n in ['bridge002.S','optical_review003.py']:
  assert old in s;s=s.replace(old,'OFFSET_PLACEHOLDER')
 s=remap(s).replace('OFFSET_PLACEHOLDER',','.join(hex(i) for i in new[1:]))
 if n=='integration009.py':s=s.replace("'<580I'","'<610I'")
 if n=='physical007.py':s=s.replace('CR16 vertical blank-end','CR07 display-end overflow').replace('CR16 ED/8C/ED preserving bit7, eight neighbors and own recovery before CR06','CR07 74/36/74, eight neighbors and own recovery before CR16')
 p=K/n.replace('795','797');assert not p.exists();p.write_bytes(s.encode())
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'796','797')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_bytes(s.encode())
s=ns((C/'model002.py').read_text(),'796','797').replace('COFF','native ELF').replace('build001','payload005').replace("out=K/'model002.json'","out=K/'model001.json'")
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}").replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a);s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe797']","sy['probe797']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_bytes(s.encode());(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'__pycache__/\nmodel001.json\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent795':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent796':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model002.py']},'candidate_layout':mapping,'optical_offsets':new,'scope':'Candidate only; require fresh payload and full bounds qualification'},indent=2)+'\n')
print('Prepared797 sources; no hardware access')
