"""Check the actual fifteen bounded ownership observations and armed DDI sites."""
import copy,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
from desktop_observer import FUNCTIONS
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
driver=k.parent/'video-mode-reset/candidate001/artifacts/xwnown.dll';p=pefile.PE(str(driver));data=driver.read_bytes();start=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=start+count*18;size=struct.unpack_from('<I',data,strings)[0];symbols={};i=0
while i<count:
 at=start+i*18;n=data[at:at+8];v,s,typ,storage,aux=struct.unpack_from('<IhHBB',data,at+8);i+=1+aux
 if n[:4]==bytes(4):n=data[strings+struct.unpack('<I',n[4:])[0]:strings+size].split(b'\0')[0]
 else:n=n.split(b'\0')[0]
 if s>0:symbols[n.decode().lstrip('_').split('@')[0]]=p.sections[s-1].VirtualAddress+v
def verify(t):
 assert t['desktop_calls']==[] and len(t['desktop_stages'])==15 and t['intervals_complete']
 stages=t['desktop_stages'];base=stages[0]['module']['base'];expected={base+symbols[n] for n in FUNCTIONS};tables=[];pdevs=[]
 for i,s in enumerate(stages):
  round,phase=divmod(i,5);assert s['args'][:2]==[round,phase] and s['args'][3]==int(phase!=0) and not s['pending'] and not s['call_count']
  assert s['owner']==t['probe_entry']['owner'] and s['module']['base']==base
  stop=t['stop_sequence'][s['stop_index']];assert stop['owner']==s['owner'] and stop['registers']==s['registers']
  if phase:assert expected<=set(stop['armed'])
  o=s['ownership'];assert o['address']==base+symbols['XwnOwners'];raw=bytes.fromhex(o['raw']);assert len(raw)==384 and len(o['slots'])==1
  slot=o['slots'][0];idx=slot['index'];assert 0<=idx<32;owner,surface,device=struct.unpack_from('<3I',raw,idx*12);assert [owner,surface,device]==[slot['owner'],slot['surface'],slot['device']]
  assert raw[:idx*12]==bytes(idx*12) and raw[(idx+1)*12:]==bytes((31-idx)*12)
  d=slot['pdev'];assert d['address']==owner;fields=struct.unpack('<7I',bytes.fromhex(d['raw']));assert list(fields)==[d['fields'][n] for n in ['driver','hdev','primary','shadow_surface','shadow_object','shadow_bits','active']]
  assert fields[1]==device and fields[2]==surface and all(fields[3:6]) and fields[6]==1
  tables.append(raw);pdevs.append(d['raw'])
 assert len(set(tables))==len(set(pdevs))==1
 return True
t=read(k/'candidate001/trace.json');assert verify(t);rejected=[]
for name in ['missing-armed-site','changed-pdev','wrong-phase']:
 v=copy.deepcopy(t)
 if name=='missing-armed-site':
  s=v['desktop_stages'][1];pc=s['module']['base']+symbols['DrvDisableSurface'];v['stop_sequence'][s['stop_index']]['armed'].remove(pc)
 elif name=='changed-pdev':v['desktop_stages'][7]['ownership']['slots'][0]['pdev']['fields']['active']=0
 else:v['desktop_stages'][7]['args'][1]=0
 try:verify(v)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Mutation accepted')
r=dict(observation_verified=True,markers=15,intervals=3,watched_functions=list(FUNCTIONS),watched_calls=0,ownership_slots=1,ownership_and_pdev_fields_identical=True,full_driver_residency_qualified=False,surface_recreation_qualified=False,physical_qualified=False,mutations_rejected=rejected,trace_sha256=sha(k/'candidate001/trace.json'),driver_sha256=sha(driver),verifier_sha256=sha(Path(__file__)))
dest=k/'ownership-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
