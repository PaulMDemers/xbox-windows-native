"""Verify actual paired routes/pins and closed cold audit; no guest operations."""
import hashlib,json,struct,sys,collections
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
r=read(out/'trace.json');s=read(k/'sites.json');a=read(out/'audit.json');c=read(out/'closure.json');pre=read(out/'preflight.json')
assert r['status']=='four_routes_captured' and r['guest_resumed'] and not r['armed_breakpoints_remaining'] and r['pending_calls']==0 and r['row_watch'] is None
assert not any(v in r for v in ['error','failed_read','resume_error'])
assert a['strict_qualification_passed'] and a['debugger'] and not a['ordinary_qualified']
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
assert sha(Path(c['private_disk']))==c['private_disk_sha256']
assert sha(out/'source/trace.py')==r['source_sha256'] and sha(k/'sites.json')==r['sites_sha256']
pes={name:pefile.PE(mod['path']) for name,mod in s['modules'].items()}
for name,mod in s['modules'].items():assert sha(Path(mod['path']))==mod['sha256']
headers={v['base']:v for v in r['module_header_identities']}
for pin in r['runtime_pins']:
 p=pes[pin['module']];raw=bytes.fromhex(pin['raw']);assert p.get_data(pin['rva'],len(raw))==raw
 assert pin['address']==pin['base']+pin['rva'] and pin['source_sha256']==s['modules'][pin['module']]['sha256']
 data=bytearray(raw)
 for off in pin['relocations']:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 assert bytes(data).hex()==pin['resident'];header=headers[pin['header_identity_base']]
 assert header['module']==pin['module'] and header['timestamp']==p.FILE_HEADER.TimeDateStamp and header['mz']=='4d5a'
stack=[];entered=[];returned=[]
for event in r['events']:
 if event['kind']=='entry':
  call=r['calls'][event['call_index']];assert call['thread']==event['thread'];stack.append(call['index']);entered.append(call['index'])
 elif event['kind']=='return':
  call=r['calls'][event['call_index']];assert stack.pop()==call['index'] and call['returned'] and call['return_address']==event['registers']['EIP'];returned.append(call['index'])
 elif event['kind']=='algorithm':assert stack and stack[-1]==event['call_index'] and r['calls'][event['call_index']]['algorithm']['label']==event['label']
 else:assert event['kind']=='marker' and not stack
assert not stack and sorted(entered)==sorted(returned)==list(range(len(r['calls'])))
assert [(v['size'],v['kind']) for v in r['samples']]==[(0,1),(0,3),(2,1),(2,3)]
rows=[]
for sample in r['samples']:
 assert sample['complete'] and sample['phase']==2
 calls=[v for v in r['calls'] if v['sample']==sample['index']]
 for name,phase in [('BitBlt',0),('NtGdiBitBlt',0),('GdiFlush',1),('NtGdiFlush',1)]:
  selected=[v for v in calls if v['name']==name];assert len(selected)==1 and selected[0]['phase']==phase
  if name!='NtGdiFlush':assert selected[0]['result']==1
 eng=[v for v in calls if v['name']=='EngCopyBits'];assert eng and all(v['phase']==0 and v['result']==1 for v in eng)
 targets=[v for v in calls if v['name']=='copy_inner_0x26e60'];assert targets and all(v['target']==0xa0117125 for v in targets)
 rows.append(dict(size=sample['size'],kind=sample['kind'],call_counts=dict(collections.Counter(v['name'] for v in calls)),copy_target_rva=0x117125,small_surfaces=[dict(call=v['index'],field=f,width=v[f]['width'],height=v[f]['height'],stride=v[f]['stride']) for v in eng for f in ['destination','source'] if v[f]['width']<64]))
row_calls=[v for v in r['calls'] if v['name']=='row_first_copy']
outer_calls=[v for v in r['calls'] if v['name'].startswith('copy_inner_') and v['target']==0xa0117125]
assert len(row_calls)==len(outer_calls)>0 and sorted(v['parent_copy_index'] for v in row_calls)==sorted(v['index'] for v in outer_calls)
for sample in r['samples']:
 ctx=sample['page_context'];cr=ctx['control_registers'];assert cr['CR0']&0x80000000 and not cr['CR4']&0x20
 assert ctx['recursive_pde']&1 and ctx['recursive_pde']&0xfffff000==cr['CR3']&0xfffff000
for call in row_calls:
 parent=r['calls'][call['parent_copy_index']];eng=r['calls'][call['eng_copy_index']];desc=struct.unpack('<14I',bytes.fromhex(call['descriptor_raw']));dst,src,n=call['arguments']
 assert call['descriptor_raw']==parent['row_descriptor']['descriptor_raw'] and call['descriptor_address']==parent['row_descriptor']['descriptor_address']
 assert 0<desc[4]<=1024 and 0<desc[5]<=576 and n==desc[4]*4
 adjust=4-n if desc[3]&0x80000000 else 0
 assert src==(desc[1]+desc[9]*4+adjust)&0xffffffff and dst==(desc[2]+desc[11]*4+adjust)&0xffffffff
 assert call['target']==(0xa013afc8 if desc[13] else 0xa000c4fa)
 assert call['recursive_pde']&0xfffff000==r['samples'][call['sample']]['page_context']['control_registers']['CR3']&0xfffff000
 alg=call['algorithm'];label=alg['label']
 if 'kernel_memmove' in label:
  target=alg['target'];pin=r['runtime_pins'][alg['target_pin']];assert pin['module']=='ntoskrnl.exe' and target==pin['base']+s['modules']['ntoskrnl.exe']['exports']['memmove']
 if label=='fallback_kernel_memmove':assert src<dst<src+n
 if label=='mmx_8byte':assert call['mmx_control_value']!=0 and src%8==0 and n>=8
 if label=='scalar_8byte':assert call['mmx_control_value']==0 and src%8==0 and n>=8
 for side,address in [('source',src),('destination',dst)]:
  memory=call[side];surf=eng[side];assert memory['address']==address and memory['byte_length']==n and memory['surface_address']==surf['address']
  assert memory['surface_row_matches']
  for match in memory['surface_row_matches']:
   y=match['y'];x=match['x_bytes'];assert 0<=y<surf['height'] and 0<=x<=surf['width']*4-n and address==surf['pvScan0']+y*surf['stride']+x
  expected=sorted(set([address,address+n-1]+list(range((address+4096)&~4095,address+n,4096))))
  assert [v['virtual_address'] for v in memory['pages']]==expected
  for page in memory['pages']:
   va=page['virtual_address'];assert page['pde_address']==0xc0300000+(va>>22)*4 and page['pde']&1
   bits=page['pde'] if page['large_page'] else page['pte'];assert bits&1
   if page['large_page']:assert page['pde']&128;physical=(bits&0xffc00000)+(va&0x3fffff);pat=bool(bits&4096)
   else:assert not page['pde']&128 and page['pte_address']==0xc0000000+(va>>12)*4;physical=(bits&0xfffff000)+(va&4095);pat=bool(bits&128)
   assert physical==page['physical_address'] and page['pwt']==bool(bits&8) and page['pcd']==bool(bits&16) and page['pat']==pat
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
assert before['clusters']==after['clusters'] and before['whole_file']==after['whole_file']
assert all(read(out/(phase+'-configuration.json'))['expected_configuration'] for phase in ['before','after'])
result=dict(passed=True,ordinary_qualified=False,physical_access=False,events=len(r['events']),paired_calls=len(r['calls']),resident_pins=len(r['runtime_pins']),samples=rows,first_row_calls=len(row_calls),algorithms=dict(collections.Counter(v['algorithm']['label'] for v in row_calls)),row_summaries=[dict(sample=v['sample'],parent_copy=v['parent_copy_index'],arguments=v['arguments'],descriptor_flag=struct.unpack('<14I',bytes.fromhex(v['descriptor_raw']))[13],algorithm=v['algorithm']['label'],source=v['source'],destination=v['destination'],mmx_control=v['mmx_control_value']) for v in row_calls],source_sha256=sha(Path(__file__)),trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),limits='Debugger first-row branch/access evidence, not timing or every-row coverage. Raw paging cache bits are not a full effective memory-type/PAT/MTRR audit. No physical or driver qualification.')
p=k/'trace-verification.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:result[key] for key in ['passed','events','paired_calls','resident_pins','first_row_calls','algorithms']},indent=2))
