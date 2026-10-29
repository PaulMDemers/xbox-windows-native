"""Fresh CR18 native derivative. Source-only parents; no hardware operations."""
from pathlib import Path
import re,json,hashlib,subprocess,sys
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-bit811';B=K.parent/'crtc-linecompare-low812'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
assert read(A/'closed001.json')['passed'] and read(B/'closed001.json')['passed']
pins={}
def ns(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x813',p).replace('0x'+old+'0000d','0x8130000d') if i%2 else p.replace(old,'813') for i,p in enumerate(parts)).replace('native-linecompare-bit813','native-linecompare-low813').replace('crtc-linecompare-low813','native-linecompare-low813')
def take(root,n,dest=None):
 manifest=read(root/'sources001.json');manifest=manifest.get('files',manifest)
 assert sha(root/n)==manifest[n],n
 pins[str((root/n).relative_to(K.parent))]=sha(root/n)
 return ns((root/n).read_text(encoding='utf-8'),'811' if root==A else '812')
def put(n,s):
 p=K/n;assert not p.exists(),n;p.write_bytes(s.encode())
for n in ['.gitattributes','.gitignore']:
 put(n,(A/n).read_text())
for n in ['probe.h','probe.c']:
 s=take(B,n)
 if n=='probe.c':
  old='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)'
  assert s.count(old)==1
  s=s.replace(old,'(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 put('probe-native.c' if n=='probe.c' else n,s)
for n in ['transaction811.c','transaction.h','bitmap001.py','compact_recovery001.py','measure001.py']:
 s=take(A,n)
 if n=='bitmap001.py':
  s=s.replace('==790','==820').replace('==416','==434').replace('[0]*25','[0]*26').replace('sentinel_bits[25]','sentinel_bits[26]').replace('i<790','i<820')
 if n=='compact_recovery001.py':s=s.replace('len(groups)==19','len(groups)==20')
 put(n.replace('811','813'),s)
subprocess.run([sys.executable,'-B',str(K/'bitmap001.py')],check=True)
subprocess.run([sys.executable,'-B',str(K/'compact_recovery001.py')],check=True)
rows=[30,100,108,675,705,735,765,795,790,793,794]
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','page_tool003.c','bridge003.S','fixture.S','link.ld','Makefile','payload_build008.py','host_build009.py','plan_test004.py','relocate003.py','relocate004.py','cpu006.py','optical_oracle.py','optical_review005.py','build014.py','link_review012.py','linked_review007.py','page_review008.py','page_boundary009.py','plan_review003.py']
for n in names:
 s=take(A,n)
 if n!='layout004.c':
  s=s.replace('0x7458','0x74d0').replace('0xc98','0xd10').replace('<790I','<820I')
  s=re.sub(r'\b3160\b','3280',s)
 if n=='bridge003.S':
  a=s.index('report_offsets:\n');z=s.index('bridge_code_end:',a)
  s=s[:a]+'report_offsets:\n .long '+','.join(hex(x) for x in [0,0x8d4]+[0x6800+4*j for j in rows])+'\n'+s[z:]
 if n=='optical_review005.py':
  a=s.index('offsets = (');z=s.index('\nr =',a);s=s[:a]+'offsets = '+repr(tuple([0x8d4]+[0x6800+4*j for j in rows]))+s[z:]
 put(n,s)
for old,new in [('model004.py','tail001.py'),('model005.py','prefix001.py')]:
 s=take(B,old).replace("P=Path('C:/xwn813/build002')","P=Path('C:/xwn813/payload008')")
 s=s.replace("out=K/'"+old.replace('.py','.json')+"'","out=K/'"+new.replace('.py','.json')+"'")
 s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'native.bin').read_bytes();symbols={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
 s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
 start=s.index(' machine,nsec,');end=s.index(' c.mem_map(0x200000',start)
 s=s[:start]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[end:]
 s=s.replace("symbols['_probe813']","symbols['probe813']")
 s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0')
 s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or bool(flags&0x200) or cpu4&0x20')
 s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]')
 s=s.replace("run('cpu-unpaged',cpu0=0x10031)","run('cpu-paged',cpu0=0x80010031)")
 put(new,s)
put('derivation001.json',json.dumps(dict(source_only=True,runtime_parent=False,physical_access=False,parents=pins,words=820,bytes=3280,rows=rows,limits=['CR18 same-value FF write/drop effectiveness unproved','No complete native mode or Windows proof']),indent=2)+'\n')
print('Prepared813 sources; no physical admission')
