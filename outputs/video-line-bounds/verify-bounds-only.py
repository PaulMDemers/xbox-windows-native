"""Verify completed line intervals only; preserve failed ExitProcess header capture."""
import copy,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
from protocol import LINES, points
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
driver=k.parent/'video-mode-reset/candidate001/artifacts/xwnown.dll';p=pefile.PE(str(driver));data=driver.read_bytes();start=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=start+count*18;size=struct.unpack_from('<I',data,strings)[0];symbols={};i=0
while i<count:
 at=start+i*18;n=data[at:at+8];v,s,typ,storage,aux=struct.unpack_from('<IhHBB',data,at+8);i+=1+aux
 if n[:4]==bytes(4):n=data[strings+struct.unpack('<I',n[4:])[0]:strings+size].split(b'\0')[0]
 else:n=n.split(b'\0')[0]
 if s>0:symbols[n.decode().lstrip('_').split('@')[0]]=p.sections[s-1].VirtualAddress+v

def verify(t):
 assert t['status']=='capture_incomplete' and t['error']=="AssertionError('E14')"
 assert "pin('kernel32.dll',exit_rva)" in t['exception_traceback']
 assert t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not t.get('resume_error')
 stages=t['line_stages'];calls=t['line_calls'];assert len(stages)==36 and len(calls)<=64
 base=stages[0]['module']['base'];entry=base+symbols['XwnLineTo'];tables=[];pdevs=[]
 for i,s in enumerate(stages):
  index,phase=divmod(i,2);assert s['args']==[index,phase] and not s['pending']
  assert s['owner']==t['probe_entry']['owner'] and s['module']['base']==base
  stop=t['stop_sequence'][s['stop_index']];assert stop['owner']==s['owner'] and stop['registers']==s['registers']
  if phase:assert entry in stop['armed']
  o=s['ownership'];assert o['address']==base+symbols['XwnOwners'];raw=bytes.fromhex(o['raw']);assert len(raw)==384 and len(o['slots'])==1
  slot=o['slots'][0];idx=slot['index'];assert 0<=idx<32
  owner,surface,device=struct.unpack_from('<3I',raw,idx*12);assert [owner,surface,device]==[slot['owner'],slot['surface'],slot['device']]
  assert raw[:idx*12]==bytes(idx*12) and raw[(idx+1)*12:]==bytes((31-idx)*12)
  d=slot['pdev'];assert d['address']==owner;fields=struct.unpack('<7I',bytes.fromhex(d['raw']))
  assert list(fields)==[d['fields'][n] for n in ['driver','hdev','primary','shadow_surface','shadow_object','shadow_bits','active']]
  assert fields[1]==device and fields[2]==surface and all(fields[3:6]) and fields[6]==1
  tables.append(raw);pdevs.append(d['raw'])
 assert len(set(tables))==len(set(pdevs))==1
 paths={Path(n).name:Path(n) for n in t['dependencies'] if n.lower().endswith(('.dll','.exe','.sys'))}
 pinset=set()
 for pin in t['pins']:
  path=paths[pin['module']];assert sha(path)==pin['sha256'];pe=pefile.PE(str(path))
  raw=bytes.fromhex(pin['raw']);assert 32<=len(raw)<=64 and pe.get_data(pin['rva'],len(raw))==raw
  rel=[e.rva-pin['rva'] for b in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and pin['rva']<=e.rva<pin['rva']+len(raw)]
  assert rel==pin['relocations'];expected=bytearray(raw)
  for off in rel:struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+pin['base']-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
  assert bytes.fromhex(pin['resident'])==expected
  pinset.add((pin['module'],pin['base']+pin['rva']))
 result=[]
 for row in calls:
  index=row['sample'];assert 0<=index<18 and row['owner']==t['probe_entry']['owner']
  args=row['args'];assert args==list(struct.unpack('<10I',bytes.fromhex(row['raw_stack'])))
  assert row['entry_registers']['EIP']==entry and ('xwnown.dll',entry) in pinset
  assert [v if v<0x80000000 else v-0x100000000 for v in args[4:8]]==list(LINES[index][:4])
  before,after=stages[index*2:index*2+2];assert before['stop_index']<row['entry_stop_index']<row['return']['stop_index']<after['stop_index']
  stop=t['stop_sequence'][row['entry_stop_index']];assert stop['registers']==row['entry_registers'] and stop['owner']==row['owner'] and entry in stop['armed']
  ret=row['return'];assert ret['owner']==row['owner'] and ret['registers']['EIP']==args[0] and ret['registers']['ESP']==row['entry_registers']['ESP']+40 and ret['registers']['EAX']==1
  stop=t['stop_sequence'][ret['stop_index']];assert stop['registers']==ret['registers'] and stop['owner']==ret['owner'] and args[0] in stop['armed']
  assert (row['return_module']['name'],args[0]) in pinset
  assert args[8] and row['bounds']==list(struct.unpack('<4i',bytes.fromhex(row['bounds_raw'])))
  left,top,right,bottom=row['bounds'];assert left<right and top<bottom
  clip=bytes.fromhex(row['clip_raw']) if row['clip_raw'] is not None else None
  assert (args[2]==0)==(clip is None)
  if clip is None:cl,ct,cr,cb=0,0,1024,576
  else:
   assert len(clip)==24;cl,ct,cr,cb=struct.unpack_from('<4i',clip,4)
  surf=bytes.fromhex(row['surface_raw']);assert len(surf)==52
  dhsurf,hsurf,dhpdev,hdev=struct.unpack_from('<4I',surf);slot=before['ownership']['slots'][0]
  assert dhsurf==dhpdev==slot['owner'] and hsurf==slot['surface'] and hdev==slot['device']
  assert struct.unpack_from('<2i',surf,16)==(1024,576) and struct.unpack_from('<H',surf,48)[0]==1
  assert all(left<=x<right and top<=y<bottom and cl<=x<cr and ct<=y<cb for x,y in points(index))
  result.append(dict(sample=index,bounds=row['bounds'],clip_bounds=[cl,ct,cr,cb],complexity=clip[20] if clip else None,pixels=len(points(index))))
 for index in range(18):
  before,after=stages[index*2:index*2+2]
  count=sum(v['sample']==index for v in calls);assert after['call_count']-before['call_count']==count
  assert count==1,(index,count)
 return result

t=read(k/'candidate001/trace.json');dest=k/'bounds-evidence.json';assert not dest.exists()
record=dict(bounds_evidence_verified=False,full_diagnostic_qualified=False,ordinary_qualified=False,physical_qualified=False,trace_sha256=sha(k/'candidate001/trace.json'),verifier_sha256=sha(Path(__file__)))
try:
 rows=verify(t);rejected=[]
 for name in ['bounds','raw-stack','return-esp','resident-pin','teardown','armed-site']:
  v=copy.deepcopy(t)
  if name=='bounds':v['line_calls'][0]['bounds'][2]=0
  elif name=='raw-stack':v['line_calls'][0]['args'][4]+=1
  elif name=='return-esp':v['line_calls'][0]['return']['registers']['ESP']+=4
  elif name=='resident-pin':v['pins'][0]['resident']='00'*len(bytes.fromhex(v['pins'][0]['resident']))
  elif name=='teardown':v['armed_breakpoints_remaining']=[1]
  else:v['stop_sequence'][v['line_stages'][1]['stop_index']]['armed'].remove(v['line_stages'][1]['module']['base']+symbols['XwnLineTo'])
  try:verify(v)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Mutation accepted: '+name)
 record.update(bounds_evidence_verified=True,rows=rows,markers=36,calls=len(rows),resident_pins=len(t['pins']),mutations_rejected=rejected,ownership_unchanged=True,teardown_verified=True)
except Exception as exc:record['error']=repr(exc)
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2))
