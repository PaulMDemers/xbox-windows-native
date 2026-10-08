"""Recheck actual markers, armed sites, resident pins, call pairs and cold result."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';sys.path.insert(0,str(ws/'work/python-packages'));import pefile
from desktop_observer import FUNCTIONS
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify(t):
 assert t['status']=='desktop_intervals_complete' and t['intervals_complete'] and t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not t.get('resume_error')
 for n,h in t['dependencies'].items():assert sha(Path(n))==h
 paths={Path(n).name:Path(n) for n in t['dependencies'] if Path(n).suffix.lower() in ['.exe','.dll','.sys']}
 pes={n:pefile.PE(str(p)) for n,p in paths.items()}
 for pin in t['pins']:
  p=pes[pin['module']];assert sha(paths[pin['module']])==pin['sha256'];raw=bytes.fromhex(pin['raw']);assert p.get_data(pin['rva'],len(raw))==raw
  expected=bytearray(raw);rel=[e.rva-pin['rva'] for b in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and pin['rva']<=e.rva<pin['rva']+len(raw)];assert rel==pin['relocations']
  for off in rel:struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
  assert bytes(expected)==bytes.fromhex(pin['resident'])
 # Decode our actual COFF table independently of the live observer.
 p=pes['xwnown.dll'];data=paths['xwnown.dll'].read_bytes();offset=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=offset+count*18;length=struct.unpack_from('<I',data,strings)[0];symbols={};i=0
 while i<count:
  at=offset+i*18;name=data[at:at+8];v,section,typ,storage,aux=struct.unpack_from('<IhHBB',data,at+8);i+=1+aux
  if name[:4]==bytes(4):name=data[strings+struct.unpack('<I',name[4:])[0]:strings+length].split(b'\0')[0]
  else:name=name.split(b'\0')[0]
  if section>0:symbols[name.decode().lstrip('_').split('@')[0]]=p.sections[section-1].VirtualAddress+v
 stages=t['desktop_stages'];calls=t['desktop_calls'];assert len(stages)==15 and len(calls)<=64
 probeowner=t['probe_entry']['owner'];base=stages[0]['module']['base'];sites={base+symbols[n] for n in FUNCTIONS};identities=[]
 for i,stage in enumerate(stages):
  round,phase=divmod(i,5);args=stage['args'];assert args[:2]==[round,phase] and args[3]==int(phase!=0) and (bool(args[2])==bool(phase)) and stage['owner']==probeowner and not stage['pending'] and stage['module']['base']==base
  stop=t['stop_sequence'][stage['stop_index']];assert stop['registers']==stage['registers'] and stop['owner']==probeowner
  if phase:assert sites<=set(stop['armed'])
  o=stage['ownership'];assert o['address']==base+symbols['XwnOwners'];raw=bytes.fromhex(o['raw']);assert len(raw)==384;slots=[]
  for index in range(32):
   owner,surface,device=struct.unpack_from('<3I',raw,index*12)
   if owner or surface or device:
    slot=next(v for v in o['slots'] if v['index']==index);assert [owner,surface,device]==[slot['owner'],slot['surface'],slot['device']]
    pdev=slot['pdev'];values=list(struct.unpack('<7I',bytes.fromhex(pdev['raw'])));assert pdev['address']==owner and values==list(pdev['fields'].values()) and values[1]==device and values[2]==surface and values[6]==1
    slots.append(slot)
  assert slots==o['slots'] and slots;identities.append(o['raw'])
 for i,call in enumerate(calls):
  assert call['index']==i and call['name'] in FUNCTIONS and call['module']['base']==base
  entry=call['entry_registers'];ret=call['return'];assert entry['EIP']==base+symbols[call['name']] and ret['owner']['thread']==call['owner']['thread'] and ret['registers']['EIP']==call['args'][0]
  argc,stdcall=FUNCTIONS[call['name']];assert ret['registers']['ESP']==entry['ESP']+4+4*argc*int(stdcall)
  assert any(stages[n]['stop_index']<call['entry_stop_index']<ret['stop_index']<stages[n+4]['stop_index'] for n in [0,5,10])
  assert any(v['module']=='xwnown.dll' and v['rva']==symbols[call['name']] for v in t['pins'])
 return dict(markers=15,pins=len(t['pins']),calls=[v['name'] for v in calls],ownership_identical=len(set(identities))==1,slot_counts=[len(s['ownership']['slots']) for s in stages])
dest=k/'lifecycle-verification.json';assert not dest.exists();trace=read(out/'trace.json');facts=verify(trace);cold=read(k/'verification.json');assert cold['cold_diagnostic_workload_passed']
r=dict(passed=True,ordinary_qualified=False,physical_qualified=False,surface_recreation_qualified=False,**facts,trace_sha256=sha(out/'trace.json'),cold_verification_sha256=sha(k/'verification.json'),verifier_sha256=sha(Path(__file__)),limits='Actual bounded desktop intervals only; absent callbacks do not qualify destruction/recreation or full driver residency.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
