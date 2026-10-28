"""Fresh source-only787 frontend and CR07 probe. No runtime or physical access."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-valid-end785';C=K.parent/'crtc-vsync-high786'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction785.c','bridge.S','fixture.S','link.ld','Makefile','payload_build005.py','host_build005.py','relocate003.py','cpu002.py','integration005.py','optical_oracle.py','optical_review002.py','build006.py','page_review003.py','plan_review003.py','linked_review004.py','physical003.py','audit_collection006.py','link_review007.py']
old='0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x56dc,0x5754,0x5740,0x574c,0x5750'
offsets=[0,0x8d4]+[0x5040+4*i for i in [30,100,108,237,261,285,405,435,430,433,434]]
new=','.join(hex(i) for i in offsets[1:])
for n in names:
 s=ns((O/n).read_text(),'785','787').replace('native-valid-end787','native-vsync-high787')
 s=s.replace('15360','16384').replace('0x5100','0x5040').replace('0x57b8','0x5770').replace('0x7b8','0x770')
 if n in ['bridge.S','optical_review002.py']:
  assert old in s;s=s.replace(old,new)
 if n=='integration005.py':s=s.replace('op+1720','op+1840').replace("'<430I'","'<460I'")
 with (K/n.replace('785','787').replace('006.py','006.py')).open('x',newline='\n') as f:f.write(s)
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'786','787')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'786','787').replace('COFF','native ELF').replace('build001','payload005')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe787']","sy['probe787']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then NVVVALIDEND719/479/719 with eight preserved neighbors','then NVVVALIDEND719/479/719 and CR07 F0/74/F0 with eight preserved neighbors');p.write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent785':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent786':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'CR07 F0/74/F0,460words5040..5770; nativeCPUguard; payloadreserve16384ends5000, request5000..503c, guard503c..5040,resultguard5770..5800,IDT5800..6000,stack6000..8000. All require fresh qualification.','optical_offsets':offsets},indent=2)+'\n')
print('Prepared787 candidate; no physical access')
