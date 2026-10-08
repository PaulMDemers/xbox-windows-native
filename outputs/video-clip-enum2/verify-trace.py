"""Verify paired real clip enumerations, counted final buffers and cold identities."""
import copy,hashlib,json,struct,sys
from pathlib import Path
from protocol import points
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(t):
 assert t['status']=='probe_exit_observed' and t['helper_succeeded'] and t['intervals_complete']
 assert t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not t.get('resume_error')
 assert t['probe_exit']['status']==0 and t['probe_exit']['pending_driver']==0
 stages=t['clip_stages'];calls=t['clip_calls'];assert len(stages)==36 and len(calls)<=512
 for index,s in enumerate(stages):
  assert s['args']==list(divmod(index,2)) and not s['pending'] and s['owner']==t['probe_entry']['owner']
  stop=t['stop_sequence'][s['stop_index']];assert stop['owner']==s['owner'] and stop['registers']==s['registers']
  if index%2:assert set(map(int,s['entries']))<=set(stop['armed'])
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
  argc=row['argc'];args=row['args'];assert args==list(struct.unpack('<'+'I'*(argc+1),bytes.fromhex(row['raw_stack'])))
  entry=row['entry_registers']['EIP'];assert (row['code_module'],entry) in pinset
  assert stages[2*index]['entries'][str(entry)]==[row['name'],argc,row['code_module'],row['code_base']]
  before,after=stages[index*2:index*2+2];ret=row['return']
  assert before['stop_index']<row['entry_stop_index']<ret['stop_index']<after['stop_index']
  assert ret['owner']==row['owner'] and ret['registers']['EIP']==args[0] and ret['registers']['ESP']==row['entry_registers']['ESP']+4*(argc+1)
  assert (row['return_module']['name'],args[0]) in pinset
  for part,at in [(row['entry_registers'],row['entry_stop_index']),(ret['registers'],ret['stop_index'])]:
   stop=t['stop_sequence'][at];assert stop['registers']==part and stop['owner']==row['owner'] and part['EIP'] in stop['armed']
  clip=bytes.fromhex(row['clip_raw']) if row['clip_raw'] else None
  assert row['clip_address']==(args[4] if row['name']=='XwnBitBlt' else args[1])
  if clip:assert len(clip)==24
  if row['name']=='XwnBitBlt':
   assert argc==11 and ret['registers']['EAX']==1 and clip and clip[20]==3
   surf=bytes.fromhex(row['surface_raw']);assert len(surf)==52
   o=row['ownership'];assert len(o['slots'])==1;slot=o['slots'][0]
   dhsurf,hsurf,dhpdev,hdev=struct.unpack_from('<4I',surf)
   assert dhsurf==dhpdev==slot['owner'] and hsurf==slot['surface'] and hdev==slot['device']
   assert struct.unpack_from('<2i',surf,16)==(1024,576) and struct.unpack_from('<H',surf,48)[0]==1
   assert o['raw']==before['ownership']['raw']==after['ownership']['raw']
  elif row['name']=='CLIPOBJ_cEnumStart':
   assert argc==5 and clip and args[2] in [0,1] and args[3]==0 and args[4] in [0,1,2,3,4]
  else:
   assert row['name']=='CLIPOBJ_bEnum' and argc==3 and clip and ret['registers']['EAX'] in [0,1]
   raw=bytes.fromhex(row['enum_raw']);count=struct.unpack_from('<I',raw)[0]
   assert len(raw)==4+16*count and count<=(args[2]-4)//16
   assert row['rectangles']==[list(struct.unpack_from('<4i',raw,4+i*16)) for i in range(count)]
   assert all(l<r and top<bottom for l,top,r,bottom in row['rectangles'])
 for index in range(18):
  rows=[v for v in calls if v['sample']==index];drivers=[v for v in rows if v['name']=='XwnBitBlt']
  assert len(drivers)==(0 if index%6==3 else 2 if index%6==5 else 1),(index,'driver coverage',len(drivers))
  sequences=[]
  for driver in drivers:
   begin=len(sequences)
   nested=[v for v in rows if driver['entry_stop_index']<v['entry_stop_index']<v['return']['stop_index']<driver['return']['stop_index']]
   assert nested and all(v['clip_address']==driver['clip_address'] for v in nested)
   seq=None
   for v in nested:
    if v['name']=='CLIPOBJ_cEnumStart':
     assert seq is None or seq['complete']
     seq=dict(start=v['args'],start_return=v['return']['registers']['EAX'],rectangles=[],batches=[],complete=False);sequences.append(seq)
    else:
     assert seq is not None and not seq['complete']
     seq['rectangles']+=v['rectangles'];seq['batches'].append(dict(count=len(v['rectangles']),more=v['return']['registers']['EAX'],buffer_bytes=v['args'][2]))
     seq['complete']=v['return']['registers']['EAX']==0
   assert seq is not None and seq['complete']
   assert len(sequences)-begin==2
   a,b=sequences[begin:];assert a['start'][2:]==[0,0,4,0] and b['start'][2:]==[0,0,4,4096]
   assert a['rectangles']==b['rectangles'] and b['start_return']==len(b['rectangles'])
  for seq in sequences:
   visible={(x,y) for l,top,r,bottom in seq['rectangles'] for y in range(max(0,top),min(256,bottom)) for x in range(max(0,l),min(384,r))}
   assert visible==points(index),(index,'enumerated coverage')
  result.append(dict(sample=index,driver_calls=len(drivers),sequences=sequences,visible_pixels=len(points(index))))
 assert any(len(v['batches'])>1 for row in result for v in row['sequences']),'No multi-batch evidence'
 return result

t=read(k/'candidate001/trace.json');dest=k/'trace-verification.json';assert not dest.exists()
r=dict(observation_verified=False,ordinary_qualified=False,physical_qualified=False,trace_sha256=sha(k/'candidate001/trace.json'),verifier_sha256=sha(Path(__file__)))
try:
 rows=verify(t);rejected=[]
 for name in ['raw_stack','return_esp','buffer_count','rectangle','resident_pin','teardown','armed_site']:
  v=copy.deepcopy(t);call=v['clip_calls'][0];enum=next(x for x in v['clip_calls'] if x['name']=='CLIPOBJ_bEnum' and x['rectangles'])
  if name=='raw_stack':call['args'][1]^=4
  elif name=='return_esp':call['return']['registers']['ESP']+=4
  elif name=='buffer_count':enum['enum_raw']='ffffffff'+enum['enum_raw'][8:]
  elif name=='rectangle':enum['rectangles'][0][2]+=1
  elif name=='resident_pin':v['pins'][0]['resident']='00'*len(bytes.fromhex(v['pins'][0]['resident']))
  elif name=='teardown':v['armed_breakpoints_remaining']=[1]
  else:v['stop_sequence'][call['entry_stop_index']]['armed'].remove(call['entry_registers']['EIP'])
  try:verify(v)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Accepted mutation '+name)
 r.update(observation_verified=True,rows=rows,mutations_rejected=rejected,markers=len(t['clip_stages']),calls=len(t['clip_calls']),pins=len(t['pins']))
except Exception as exc:r['error']=repr(exc)
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:v for n,v in r.items() if n!='rows'},indent=2))
