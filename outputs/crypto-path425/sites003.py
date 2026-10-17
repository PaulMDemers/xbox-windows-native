"""Review exact owned native stubs, process layouts and checkpoint code before runtime."""
import hashlib,json,re,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn425/modules001')
sys.path.insert(0,str(W/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert P.exists() and not (K/'sites003.json').exists()
source=Path('/mnt/e/xwn406/runs/nt5-validation406-emu001/hdd.qcow2')
expected=json.loads((W/'outputs/install-validation406/emu001/audit.json').read_text())['disk_sha256'];assert json.loads((K/'modules001.json').read_text())['source_sha256']==expected
prior=json.loads((W/'outputs/shutdown-popup-workload/site-review.json').read_text())
build=json.loads((K/'build002.json').read_text());exe=Path(build['rows'][0]['path'].replace('/mnt/e/','E:/'));assert sha(exe)==build['rows'][0]['sha256']
pe=pefile.PE(str(exe));assert pe.OPTIONAL_HEADER.ImageBase==0x17000000
mp=(exe.parent/'trace.map').read_text();addresses={}
for name in ['xwn_checkpoint425@4','xwn_record425']:
 matches=re.findall(r'^\s+(0x[0-9a-f]+)\s+'+re.escape(name)+r'\s*$',mp,re.M);assert len(matches)==1;addresses[name]=int(matches[0],16)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def stub(pe,rva):
 instructions=[];raw=b''
 for ins in md.disasm(pe.get_data(rva,64),rva):
  raw+=ins.bytes;instructions.append([ins.address,ins.mnemonic,ins.op_str])
  if ins.mnemonic=='ret':break
 assert instructions[-1][1]=='ret' and len(raw)<=32
 return {'rva':rva,'bytes':raw.hex(),'instructions':instructions,'return_rva':instructions[-1][0]}
mods={}
def module(name):
 name=name.lower()
 if name not in mods:
  data=(P/name).read_bytes();assert hashlib.sha256(data).hexdigest()==json.loads((K/'modules001.json').read_text())['modules'][name];x=pefile.PE(data=data)
  mods[name]=(x,{s.name.decode():s for s in x.DIRECTORY_ENTRY_EXPORT.symbols if s.name},hashlib.sha256(data).hexdigest())
 return mods[name]
ntdll,exports,h=module('ntdll.dll');assert h==prior['binaries']['ntdll.dll']['sha256']
kernel=(P/'ntoskrnl.exe').read_bytes();assert hashlib.sha256(kernel).hexdigest()==prior['kernel_sha256']
def resolve(dll,name,depth=0):
 assert depth<8
 x,es,h=module(dll);e=es[name]
 if e.forwarder:
  target,sym=e.forwarder.decode().rsplit('.',1);return [(dll,name,h)]+resolve(target+'.dll',sym,depth+1)
 return [(dll,name,h)]
imports=[resolve(d.dll.decode(),s.name.decode()) for d in pe.DIRECTORY_ENTRY_IMPORT for s in d.imports]
apis=[]
for name,argc,oa in [('NtCreateFile',11,2),('NtOpenFile',6,2),('NtQueryAttributesFile',2,0),('NtQueryFullAttributesFile',2,0)]:
 s=stub(ntdll,exports[name].address);assert int(s['instructions'][-1][2],0)==argc*4
 assert any(i[1:] == ['int','0x2e'] for i in s['instructions'])
 apis.append(dict(name=name,argc=argc,oa_index=oa,**s))
thread=json.loads((W/'outputs/native-windows-nt5-kernel/thread-layouts.json').read_text())
process=json.loads((W/'outputs/native-windows-nt5-kernel/process-layouts.json').read_text())
r={'source_sha256':expected,'native_sha256':sha(exe),'native_path':str(exe),'image_base':pe.OPTIONAL_HEADER.ImageBase,
   'native_timestamp':pe.FILE_HEADER.TimeDateStamp,'image_size':pe.OPTIONAL_HEADER.SizeOfImage,
   'checkpoint':stub(pe,addresses['xwn_checkpoint425@4']-pe.OPTIONAL_HEADER.ImageBase),'record_address':addresses['xwn_record425'],
   'ntdll_sha256':mods['ntdll.dll'][2],'ntdll_base':ntdll.OPTIONAL_HEADER.ImageBase,'ntdll_timestamp':ntdll.FILE_HEADER.TimeDateStamp,
   'kernel_sha256':prior['kernel_sha256'],'apis':apis,'imports':imports,'thread_owner_offset':prior['thread_owner_offset'],
   'process_fields':process['_EPROCESS']['fields'],'thread_fields':thread['_ETHREAD']['fields'],
   'source_files':{str(p.relative_to(W)):sha(p) for p in [K/'probe.c',K/'sites003.py',W/'outputs/native-windows-nt5-kernel/thread-layouts.json',W/'outputs/native-windows-nt5-kernel/process-layouts.json']},
   'owned_module_hashes':{name:v[2] for name,v in mods.items()},'physical_access':False,'guest_launched':False}
assert json.loads((K/'modules001.json').read_text())['source_sha256']==expected
(K/'sites003.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'checkpoint':r['checkpoint'],'apis':apis,'imports':len(imports)}))
