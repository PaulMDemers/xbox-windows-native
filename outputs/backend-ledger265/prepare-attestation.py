"""Static leads for runtime verification; no running process is inspected here."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'attestation-inputs001.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['outputs/surface-pattern258/build-review002.json','outputs/backend-ledger265/probe-review001.json',
 'outputs/backend-ledger265/callsite-review.json','outputs/dump-map-trace/sites.json',
 'outputs/controlled-dump/layouts.json','outputs/pci-support207/inputtrace006/owner-layouts001.json',
 'outputs/native-windows-nt5-kernel/process-layouts.json','outputs/shutdown-popup-workload/site-review.json']
deps={n:sha(ws/n) for n in paths};old,probe,calls,sites,layouts,owner,proc,thread=[read(ws/n) for n in paths]
assert layouts['pdb_sha256']==owner['pdb_sha256']=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
pdb=Path(owner['pdb_path']);assert sha(pdb)==owner['pdb_sha256']
types=layouts['structures']|owner['structures']|proc
files={'ntoskrnl.exe':ws/old['providers']['ntoskrnl.exe']['path'],
 'pattern.sys':ws/'outputs/surface-pattern258/artifacts/build002/pattern.sys',
 'probe.exe':ws/'outputs/backend-ledger265/artifacts/build001/probe.exe'}
expected={'ntoskrnl.exe':sites['kernel_sha256'],'pattern.sys':old['binaries']['pattern.sys']['sha256'],'probe.exe':probe['native_sha256']}
modules={}
for name,p in files.items():
 assert sha(p)==expected[name];pe=pefile.PE(str(p));text=next(v for v in pe.sections if v.Name.rstrip(b'\0')==b'.text')
 modules[name]=dict(path=p.relative_to(ws).as_posix(),sha256=sha(p),timestamp=pe.FILE_HEADER.TimeDateStamp,
  preferred_base=pe.OPTIONAL_HEADER.ImageBase,image_size=pe.OPTIONAL_HEADER.SizeOfImage,
  text_rva=text.VirtualAddress,text_size=text.Misc_VirtualSize)
driver=files['pattern.sys'];data=driver.read_bytes();pe=pefile.PE(str(driver));start=pe.FILE_HEADER.PointerToSymbolTable
count=pe.FILE_HEADER.NumberOfSymbols;strings=start+18*count;index=0;arena=[]
while index<count:
 name,value,section,typ,storage,aux=struct.unpack_from('<8sIhHBB',data,start+index*18)
 if name[:4]==b'\0'*4:
  offset=struct.unpack('<I',name[4:])[0];end=data.index(0,strings+offset);name=data[strings+offset:end]
 else:name=name.rstrip(b'\0')
 if name==b'_Arena':
  assert section>0;arena.append(pe.sections[section-1].VirtualAddress+value)
 index+=1+aux
assert len(arena)==1
kernel=pefile.PE(str(files['ntoskrnl.exe']))
# Exact NT5 table/index/object-pointer conventions, independently reviewed by
# inputtrace006. Capture the actual instruction spans for resident verification.
semantics=[dict(rva=rva,size=n,raw=kernel.get_data(rva,n).hex()) for rva,n in
 ((0x8f87c,0x49),(0x8eaa4,0x68),(0x8eb0c,0x42),(0x4e702,0x65))]
assert kernel.get_data(0x4e704,3)==bytes.fromhex('83e2f8')
assert kernel.get_data(0x8eabd,5)==bytes.fromhex('0d00000080')
assert kernel.get_data(0x8eb35,6)==bytes.fromhex('81e7ffffff7f')
r=dict(passed=True,guest_observed=False,physical_access=False,source_sha256=sha(Path(__file__)),
 dependencies=deps,pdb_sha256=sha(pdb),modules=modules,structures=types,
 kernel_base_lead=sites['kernel_base_expected'],module_list_rva=sites['loaded_module_list_rva'],
 current_thread_address=0xffdff124,thread_owner_offset=thread['thread_owner_offset'],
 arena_rva=arena[0],checkpoint_rva=probe['checkpoint_rva'],reply_rva=probe['symbols_rva']['_Reply'] if 'symbols_rva' in probe else probe['symbols']['_Reply'],
 callsites=calls['calls'],handle_semantics=semantics,
 limits='Static addresses are leads only. Actual process/handle/object, modules, resident bytes, CR3 and four translations must match at every checkpoint; never read the dirty arena.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('260 static runtime-attestation inputs pinned; no guest observation')
