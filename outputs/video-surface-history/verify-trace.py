"""Recompute upload operands/page walks/paired copies from preserved trace bytes."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def validate(r,s):
 assert r['status']=='three_uploads_captured' and r['guest_resumed'] and r['pending'] is None and not r['armed_breakpoints_remaining']
 assert not any(n in r for n in ['error','resume_error'])
 assert len(r['samples'])==3 and len(r['events'])==24
 base=next(m['base'] for m in r['loaded_modules'] if m['name']=='xwnown.dll')
 addresses={n:base+rv for n,rv in s['sites'].items()}
 summaries=[]
 for index, sample in enumerate(r['samples']):
  assert sample['sample']==index and sample['complete'] and sample['returned'] and sample['copy_returned']
  rect=[[0,0,192,96],[128,0,320,96],[0,160,192,256]][index];assert sample['rect']==rect
  before,after=sample['pdev'],sample['pdev_after']
  for d in [before,after]:
   raw=bytes.fromhex(d['raw']);assert len(raw)==136 and d['ScreenDelta']==4096
   for n,offset in s['pdev_offsets'].items():assert d[n]==struct.unpack_from('<Q' if n=='ShadowBytes' else '<I',raw,offset)[0]
  assert before['address']==after['address']
  assert after['ShadowUploads']==before['ShadowUploads']+1 and after['ShadowBytes']==before['ShadowBytes']+73728
  assert all(before[n]==after[n] for n in ['ShadowBits','ScreenPtr','ScreenDelta'])
  cr=sample['context']['registers'];assert cr['CR0']&0x80000000 and not cr['CR4']&0x20
  assert sample['context']['recursive_pde']&1 and sample['context']['recursive_pde']&0xfffff000==cr['CR3']&0xfffff000
  l,t,right,bottom=rect;dst,src,n=sample['copy_arguments']
  assert [dst,src,n]==[before['ScreenPtr']+t*4096+l*4,before['ShadowBits']+t*4096+l*4,768]
  a,b=sample['rep_before'],sample['rep_after']
  assert a['EIP']==addresses['rep_movsd'] and a['ESI']==src and a['EDI']==dst and a['ECX']==192 and not a['EFLAGS']&0x400
  assert b['EIP']==addresses['after_rep'] and b['ESI']==src+n and b['EDI']==dst+n and b['ECX']==0 and a['ESP']==b['ESP']
  assert sample['source_before']==sample['destination_after'] and len(bytes.fromhex(sample['source_before']))==n
  events=r['events'][index*8:(index+1)*8]
  assert [e['kind'] for e in events]==['marker','upload_entry','copy_call','rep_movsd','after_rep','copy_return','upload_return','marker']
  assert [events[0]['phase'],events[-1]['phase']]==[0,1]
  for e in events:assert e['sample']==index and e['owner']['thread']==sample['thread'] and e['owner']['process']==sample['process']
  for j,label in [(1,'upload_entry'),(2,'copy_call'),(3,'rep_movsd'),(4,'after_rep'),(5,'copy_return')]:assert events[j]['address']==addresses[label]
  assert events[1]['registers']['EAX']==before['address'] and events[1]['registers']['ESP']==sample['entry_stack']
  assert events[2]['registers']['ESP']==sample['copy_stack'] and events[2]['registers']['EDI']==before['address']
  assert events[5]['registers']['ESP']==sample['copy_stack'] and events[5]['registers']['EAX']==dst
  assert events[6]['address']==sample['return_address'] and events[6]['registers']['ESP']==sample['entry_stack']+4
  sides={}
  for side,key in [('source','ShadowBits'),('destination','ScreenPtr')]:
   memory=sample[side];assert memory['base']==before[key] and len(memory['rows'])==96
   tables={r['address']:bytes.fromhex(r['raw']) for r in memory['tables']};assert all(len(data)==4096 for data in tables.values())
   physical=[];flags=set()
   for y,row in zip(range(t,bottom),memory['rows']):
    assert row['y']==y and len(row['points'])==2
    for end,p in enumerate(row['points']):
     va=before[key]+y*4096+(l*4 if end==0 else right*4-1)
     assert p['virtual']==va and p['pde_address']==0xc0300000+(va>>22)*4 and p['pde']&1
     if p['large']:
      bits=p['pde'];assert bits&128;pa=(bits&0xffc00000)+(va&0x3fffff);pat=bool(bits&4096)
     else:
      assert not p['pde']&128 and p['pte_address']==0xc0000000+(va>>12)*4
      addr=p['pte_address'];bits=struct.unpack_from('<I',tables[addr&~4095],addr&4095)[0]
      assert bits==p['pte'] and bits&1;pa=(bits&0xfffff000)+(va&4095);pat=bool(bits&128)
     assert p['physical']==pa and p['pwt']==bool(bits&8) and p['pcd']==bool(bits&16) and p['pat']==pat
     flags.add((p['pwt'],p['pcd'],p['pat'],p['large']))
     if end==0:physical.append(pa)
   sides[side]=dict(base=before[key],first_virtual=memory['rows'][0]['points'][0]['virtual'],first_physical=physical[0],last_physical=physical[-1],unique_physical_pages=len({v>>12 for v in physical}),cache_flags=[list(f) for f in sorted(flags)])
  summaries.append(dict(sample=index,rect=rect,copy_bytes=n,rows=96,cr3=cr['CR3'],source=sides['source'],destination=sides['destination'],virtual_base_delta=before['ScreenPtr']-before['ShadowBits'],algorithm='local memmove forward rep movsd',first_row_equal=True))
 return summaries

if __name__=='__main__':
 r=read(out/'trace.json');s=read(k/'sites.json');rows=validate(r,s)
 for name,digest in r['dependencies'].items():assert sha(Path(name))==digest,name
 for name,digest in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/name)==digest,name
 sys.path.insert(0,str(ws/'work/python-packages'));import pefile
 review=read(k/'pe-review.json');old=read(k.parent/'video-shared-trace2/sites.json')
 paths={'probe.exe':k/'artifacts/probe.exe','xwnown.dll':Path(s['driver_path']),'ntoskrnl.exe':Path(old['modules']['ntoskrnl.exe']['path'])}
 assert sha(paths['probe.exe'])==review['probe_sha256'] and sha(paths['xwnown.dll'])==review['display_sha256']==s['driver_sha256']
 pes={name:pefile.PE(str(p)) for name,p in paths.items()}
 for pin in r['pins']:
  p=pes[pin['module']];raw=bytes.fromhex(pin['raw']);assert p.get_data(pin['rva'],len(raw))==raw and sha(paths[pin['module']])==pin['sha256']
  reloc=[e.rva-pin['rva'] for b in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and pin['rva']<=e.rva<pin['rva']+len(raw)]
  assert reloc==pin['relocations'];data=bytearray(raw)
  for off in reloc:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
  assert data.hex()==pin['resident']
 v=read(out/'verification.json');a=read(out/'audit.json');assert v['passed'] and not v['ordinary_qualified'] and not v['timing_qualified'] and a['debugger']
 result=dict(passed=True,ordinary_qualified=False,physical_qualified=False,samples=rows,events=len(r['events']),resident_pins=len(r['pins']),all_breakpoints_removed=True,diagnostic_cold_passed=True,
  pins={n:sha(out/n) for n in ['trace.json','verification.json','closure.json','audit.json','preflight.json']},source_sha256=sha(Path(__file__)),limits='First-row execution plus all-row mappings; not all-row instruction coverage, effective cache type, TLB-miss evidence or timing qualification.')
 dest=k/'trace-verification.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))
