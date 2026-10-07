"""Verify actual paired routes/pins and closed cold audit; no guest operations."""
import hashlib,json,struct,sys,collections
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace003'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
r=read(out/'trace.json');s=read(k/'sites.json');a=read(out/'audit.json');c=read(out/'closure.json');pre=read(out/'preflight.json')
assert r['status']=='four_routes_captured' and r['guest_resumed'] and not r['armed_breakpoints_remaining'] and r['pending_calls']==0
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
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
assert before['clusters']==after['clusters'] and before['whole_file']==after['whole_file']
assert all(read(out/(phase+'-configuration.json'))['expected_configuration'] for phase in ['before','after'])
result=dict(passed=True,ordinary_qualified=False,physical_access=False,events=len(r['events']),paired_calls=len(r['calls']),resident_pins=len(r['runtime_pins']),samples=rows,source_sha256=sha(Path(__file__)),trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),limits='Debugger route evidence, not time attribution. Software-pointer involvement inferred from small surfaces at pointer rectangle; separate matched cursor-position test required. Private row-copy branch selection was not captured.')
p=k/'trace-verification.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:result[key] for key in ['passed','events','paired_calls','resident_pins']},indent=2))
