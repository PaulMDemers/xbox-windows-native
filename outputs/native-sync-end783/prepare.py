"""Source-only783 from closed781 frontend and closed782 qualified probe."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-sync-start781';C=K.parent/'vertical-sync-end782'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
names=['main.c','layout.c','layout.h','plan.c','plan.h','plan_test.py','page002.c','page.h','page_tool003.c','transaction.h','transaction781.c','bridge.S','fixture.S','link.ld','Makefile','payload_build003.py','host_build005.py','relocate003.py','cpu002.py','integration005.py','optical_oracle.py','optical_review002.py','build006.py','page_review003.py','plan_review003.py','linked_review004.py','physical003.py','audit_collection005.py','link_review005.py','source_review.py','review_prepare002.py']
for n in names:
 s=ns((O/n).read_text().replace('native-sync-start781','native-sync-end783'),'781','783')
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x6c8)','memset(p+0x5000,0,0x740)')
 with (K/n.replace('781','783')).open('x',newline='\n') as f:f.write(s)
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'782','783')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 (K/n).write_text(s,newline='\n')
s=ns((C/'model.py').read_text(),'782','783').replace('COFF','native ELF').replace('build001','payload003')
s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'payload.bin').read_bytes()\nsy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
a=s.index(' machine,nsec,');z=s.index(' c.mem_map(0x200000',a)
s=s[:a]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[z:]
s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0').replace("symbols['_probe783']","sy['probe783']")
s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20').replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
(K/'model.py').write_text(s,newline='\n')
old='0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x55ec,0x5664,0x5650,0x565c,0x5660'
new='0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x5664,0x56dc,0x56c8,0x56d4,0x56d8'
for n in ['bridge.S','optical_review002.py']:
 p=K/n;s=p.read_text();assert old in s;p.write_text(s.replace(old,new),newline='\n')
p=K/'physical003.py';s=p.read_text().replace('then NVVSYNCSTART724/489/724 with eight preserved neighbors','then NVVSYNCSTART724/489/724 and NVVSYNCEND729/492/729 with eight preserved neighbors');p.write_text(s,newline='\n')
p=K/'audit_collection005.py';s=p.read_text().replace('NVVSYNCSTART','NVVSYNCEND').replace('[724,489,724]','[729,492,729]').replace('target=489','target=492').replace('ten_other','eleven_other');p.write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent781':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'parent782':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['probe.c','probe.h','model.py']},'delta':'NVVSYNCEND729/492/729;400words5100..5740 initialized; nativeCPUguard;13 rows finalcode,eight masks,syncend triplet. Eleven masks omitted raw, final requiresall19. Payload14080 must pass fresh bounds.'},indent=2)+'\n')
print('Prepared783 native candidate, no hardware access')
