"""Verify source, actual loaded bootvid code/global and closed cold audit."""
import hashlib,json,struct,sys
from pathlib import Path
from walk import read_virtual,physical
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace002'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');c=read(out/'closure.json');s=read(k/'alias-scan.json');pre=read(out/'preflight.json')
assert s['passed'] and t['status']=='desktop_snapshot_captured' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert a['strict_qualification_passed'] and not a['ordinary_qualified'] and a['debugger']
assert sha(Path(c['private_disk']))==c['private_disk_sha256']
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h and sha(k/n)==h
assert sha(k/'scan.py')==s['source_sha256'] and sha(k/'walk.py')==s['walker_sha256'] and sha(out/'trace.json')==s['trace_sha256']
raw=Path(t['private_memory']);assert sha(raw)==s['snapshot_sha256']==t['private_memory_sha256'];data=raw.read_bytes();cr3=t['control_registers']['CR3']
sites=read(k/'sites.json')
for pin in t['runtime_pins']:
 mod=sites['modules'][pin['module']];assert sha(Path(mod['path']))==mod['sha256'];p=pefile.PE(mod['path']);b=bytearray(p.get_data(pin['rva'],len(bytes.fromhex(pin['raw']))));assert b.hex()==pin['raw']
 for off in pin['relocations']:struct.pack_into('<I',b,off,(struct.unpack_from('<I',b,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 assert b.hex()==pin['resident'] and read_virtual(data,cr3,pin['address'],len(b))==b
b=out/'artifacts/before-xboxbvid.dll';p=pefile.PE(str(b));d=b.read_bytes();expected='2196f646653c4c944d73fee4944ee3d056c82cf01903e4f435e67d63c03ed4b7';assert sha(b)==expected
assert all(read(out/(phase+'-bootvid.json'))['sha256']==expected for phase in ['before','after'])
module=next(v for v in t['module_list'] if v['name']=='bootvid.dll');base=module['base'];assert module['size']==p.OPTIONAL_HEADER.SizeOfImage
assert read_virtual(data,cr3,base,2)==b'MZ';nt=struct.unpack('<I',read_virtual(data,cr3,base+60,4))[0]
assert struct.unpack('<I',read_virtual(data,cr3,base+nt+8,4))[0]==p.FILE_HEADER.TimeDateStamp
sec=next(x for x in p.sections if x.Name.rstrip(b'\0')==b'.text');start=sec.VirtualAddress;code=bytearray(p.get_data(start,sec.Misc_VirtualSize))
for block in p.DIRECTORY_ENTRY_BASERELOC:
 for e in block.entries:
  if e.type==3 and start<=e.rva<start+len(code):
   off=e.rva-start;assert off+4<=len(code);struct.pack_into('<I',code,off,(struct.unpack_from('<I',code,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
assert read_virtual(data,cr3,base+start,len(code))==code
sym=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=sym+18*count;globals={};i=0
while i<count:
 row=d[sym+18*i:sym+18*(i+1)];z,off=struct.unpack_from('<II',row);name=d[strings+off:].split(b'\0')[0] if z==0 else row[:8].split(b'\0')[0]
 if name in [b'_FrameBufferStart',b'_BackBuffer']:
  val,section=struct.unpack_from('<Ih',row,8);assert section>0;rva=p.sections[section-1].VirtualAddress+val;address=base+rva;value=struct.unpack('<I',read_virtual(data,cr3,address,4))[0]
  globals[name.decode()]=dict(symbol_rva=rva,address=address,value=value,physical=physical(data,cr3,value))
 i+=1+row[17]
assert len(globals)==2 and globals['_FrameBufferStart']['physical']==0x03c00000
bootva=globals['_FrameBufferStart']['value'];roots=[]
for directory in s['directories']:
 matches=[v for v in directory['ranges'] if v['virtual']==bootva and v['physical']==0x03c00000]
 assert len(matches)==1 and matches[0]['length']==0x400000 and matches[0]['flags'][2:4]==[True,True]
 roots.append(directory['root'])
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']];assert before['clusters']==after['clusters'] and before['whole_file']==after['whole_file']
assert all(read(out/(phase+'-configuration.json'))['expected_configuration'] for phase in ['before','after'])
result=dict(passed=True,physical_access=False,ordinary_qualified=False,bootvid=dict(sha256=expected,base=base,text_rva=start,text_bytes=len(code),relocated_text_sha256=hashlib.sha256(code).hexdigest(),globals=globals,mapping_found_in_roots=roots),alias_scan_sha256=sha(k/'alias-scan.json'),audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),source_sha256=sha(Path(__file__)),limits='Current linked active roots and current root, present translations only. Code identity/global proves retained bootvid mapping at this point. No current MSR/TLB, unlinked process or future lifetime proof.')
dest=k/'verification.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
