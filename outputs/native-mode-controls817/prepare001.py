"""Source-only derivative: kernel816 controls in a newly qualified 40KiB bridge."""
from pathlib import Path
import re,json,hashlib,subprocess,sys
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-low813';B=K.parent/'crtc-mode-controls816'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert read(A/'closed001.json')['passed'] and read(B/'closed001.json')['passed']
pins={}
def ns(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x817',p).replace('0x'+old+'0000d','0x8170000d') if i%2 else p.replace(old,'817') for i,p in enumerate(parts)).replace('native-linecompare-low817','native-mode-controls817').replace('crtc-mode-controls817','native-mode-controls817')
def take(root,n):
 manifest=read(root/'sources001.json');manifest=manifest.get('files',manifest)
 assert sha(root/n)==manifest[n],n
 pins[str((root/n).relative_to(K.parent))]=sha(root/n)
 return ns((root/n).read_text(),'813' if root==A else '816')
def put(n,s):
 p=K/n;assert not p.exists(),n;p.write_bytes(s.encode())
for n in ['.gitattributes','.gitignore']:put(n,(A/n).read_text())
for n in ['probe.h','probe.c']:
 s=take(B,n)
 if n=='probe.c':
  old='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)';assert s.count(old)==1
  s=s.replace(old,'(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 put('probe-native.c' if n=='probe.c' else n,s)
for n in ['transaction813.c','transaction.h','bitmap001.py','compact_recovery001.py','measure001.py']:
 s=take(A,n)
 if n=='bitmap001.py':s=s.replace('==820','==917').replace('[0]*26','[0]*29').replace('sentinel_bits[26]','sentinel_bits[29]').replace('i<820','i<917')
 put(n.replace('813','817'),s)
subprocess.run([sys.executable,'-B',str(K/'bitmap001.py')],check=True)
subprocess.run([sys.executable,'-B',str(K/'compact_recovery001.py')],check=True)
# Eight displayed recovery masks, three CR1A values. Other masks aggregate-only.
rows=[30,100,108,675,735,795,915,916,820,835,905]
hexmap={'0x1ff8000':'0x1ff6000','0x67c0':'0x77c0','0x67c4':'0x77c4','0x6800':'0x7800','0x74d0':'0x8654','0x7500':'0x8700','0x7d00':'0x8f00','0x7d04':'0x8f04','0x7ffc':'0x9ffc','0x8000':'0xa000','0x5ec0':'0x6ec0','0xd10':'0xe94'}
def layout(s):
 s=re.sub(r'0x[0-9a-fA-F]+',lambda m:hexmap.get(m[0],m[0]),s)
 return re.sub(r'\b(24255|24256|24257|32768|32832|3280)\b',lambda m:{'24255':'28351','24256':'28352','24257':'28353','32768':'40960','32832':'41024','3280':'3668'}[m[0]],s).replace('<820I','<917I')
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','page_tool003.c','bridge003.S','fixture.S','link.ld','Makefile','payload_build008.py','host_build009.py','plan_test004.py','relocate003.py','relocate004.py','cpu006.py','optical_oracle.py','optical_review005.py','build015.py','link_review012.py','linked_review007.py','page_review008.py','page_boundary009.py','plan_review003.py']
for n in names:
 s=take(A,n)
 if n!='layout004.c':s=layout(s)
 if n in ['plan.c','plan.h','main004.c']:s=s.replace('i<8','i<10').replace('alias[8],alias_last[8]','alias[10],alias_last[10]').replace('words[31]','words[35]')
 if n=='main004.c':s=s.replace('report[40960], verify[40960]','report[32768], verify[32768]')
 if n in ['plan_test004.py','plan_review003.py']:
  s=s.replace('range(8)','range(10)').replace('range(31)','range(35)').replace('c_uint32*31','c_uint32*35').replace('<31L','<35L')
  s=re.sub(r'v\[(20|28|29|30)(\+i)?\]',lambda m:'v['+str(int(m[1])+ (2 if m[1]=='20' else 4))+(m[2] or '')+']',s)
 if n=='page002.c':
  # Correct the previously unused selector08 descriptor. The old status namespace
  # rewrite had moved its low dword to813; selectors10/18 were unaffected.
  assert 'w32(p,0x817,0xffff)' in s;s=s.replace('w32(p,0x817,0xffff)','w32(p,0x808,0xffff)')
 if n=='fixture.S':s=s.replace('mov ecx,10240','mov ecx,12288').replace('mov ecx,21504','mov ecx,22528').replace('mov edx,8','mov edx,10').replace('mov ecx,8\n','mov ecx,10\n').replace('/4096+7)','/4096+9)')
 if n=='cpu006.py':
  s=s.replace("spec['base']-4096,40960","spec['base']-4096,49152").replace("73728 if spec['alias']!=spec['base'] else 40960","90112 if spec['alias']!=spec['base'] else 49152").replace('range(8)','range(10)').replace('alias[36864:40960]','alias[45056:49152]')
 if n=='bridge003.S':
  a=s.index('report_offsets:\n');z=s.index('bridge_code_end:',a)
  s=s[:a]+'report_offsets:\n .long '+','.join(hex(x) for x in [0,0x8d4]+[0x7800+4*j for j in rows])+'\n'+s[z:]
  s=s.replace('768-byte stack','4352-byte stack')
 if n=='optical_review005.py':
  a=s.index('offsets = (');z=s.index('\nr =',a);s=s[:a]+'offsets = '+repr(tuple([0x8d4]+[0x7800+4*j for j in rows]))+s[z:]
 put(n,s)
for n in ['tail002.py','prefix002.py']:
 s=take(B,n).replace("P=Path('C:/xwn817/build002')","P=Path('C:/xwn817/payload008')")
 s=s.replace("b=(P/'probe.obj').read_bytes()","b=(P/'native.bin').read_bytes();symbols={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}")
 s=s.replace("'object_sha256':sha(P/'probe.obj')","'ELF_sha256':sha(P/'native.elf')")
 start=s.index(' machine,nsec,');end=s.index(' c.mem_map(0x200000',start)
 s=s[:start]+" c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)\n"+s[end:]
 s=re.sub(r"symbols\['_([^']+)'\]",r"symbols['\1']",s)
 s=s.replace('flags=0x246,cpu0=0x80010031,cpu3=0xf000','flags=0x46,cpu0=0x4001003b,cpu3=0')
 s=s.replace('cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20','cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or bool(flags&0x200) or cpu4&0x20')
 s=s.replace('[0,1,0x40000001,0x80000000]','[0,1,0x80010031,0x80000000]').replace("run('cpu-unpaged',cpu0=0x10031)","run('cpu-paged',cpu0=0x80010031)")
 put(n,s)
put('derivation001.json',json.dumps(dict(source_only=True,runtime_parent=False,physical_access=False,parents=pins,words=917,bytes=3668,rows=rows,allocation=40960,payload=[2304,30656],request=[30656,30716],result=[30720,34388],idt=[34560,36608],stack=[36608,40960],gdt_unused_selector08_correction=True),indent=2)+'\n')
print('Prepared817 source only; relocation cardinality requires fresh build review')
