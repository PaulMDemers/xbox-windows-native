"""Independent recorded-return/pin/TEB checks; retain failed workload qualification."""
import copy,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def validate(t):
 assert t['status']=='probe_exit_observed' and t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not t.get('resume_error')
 assert not t['probe_exit']['pending_api'] and not t['probe_exit']['pending_driver']
 assert t['probe_exit']['registers']==t['stop_sequence'][-1]['registers']
 paths={Path(n).name:Path(n) for n in t['dependencies'] if Path(n).suffix.lower() in ['.exe','.dll','.sys']}
 pes={n:pefile.PE(str(p)) for n,p in paths.items()}
 for pin in t['pins']:
  p=pes[pin['module']];raw=bytes.fromhex(pin['raw']);assert p.get_data(pin['rva'],len(raw))==raw and sha(paths[pin['module']])==pin['sha256']
  rel=[e.rva-pin['rva'] for b in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and pin['rva']<=e.rva<pin['rva']+len(raw)];assert rel==pin['relocations'];expected=bytearray(raw)
  for off in rel:struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
  assert bytes(expected)==bytes.fromhex(pin['resident'])
 def teb(row):
  b=bytes.fromhex(row['raw_first64']);assert len(b)==64 and struct.unpack_from('<I',b,0x18)[0]==row['base'] and struct.unpack_from('<I',b,0x34)[0]==row['last_error']
 teb(t['probe_exit']['teb']);rows=t['api_calls'];assert rows
 ub=next(m['base'] for m in t['loaded_modules'] if m['name']=='user32.dll');exports={s.name.decode():s.address for s in pes['user32.dll'].DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 results=[]
 for i,row in enumerate(rows):
  assert row['index']==i and row['name'] in ['OpenDesktopA','CloseDesktop'];argc=4 if row['name']=='OpenDesktopA' else 1;assert row['argc']==argc
  entry=row['entry_registers'];ret=row['return'];assert entry['EIP']==ub+exports[row['name']]
  assert row['owner']==ret['owner']==t['probe_entry']['owner'] and ret['registers']['EIP']==row['args'][0] and ret['registers']['ESP']==entry['ESP']+4+4*argc
  assert row['entry_stop']<ret['stop']<len(t['stop_sequence'])-1
  assert t['stop_sequence'][row['entry_stop']]['registers']==entry and t['stop_sequence'][ret['stop']]['registers']==ret['registers']
  assert any(p['module']=='user32.dll' and p['rva']==exports[row['name']] for p in t['pins'])
  teb(row['teb_before']);teb(ret['teb']);assert row['teb_before']['base']==ret['teb']['base']
  results.append(dict(name=row['name'],stage_count=row['stage_count'],arguments=row['args'][1:],desktop_name=row.get('desktop_name'),result=ret['registers']['EAX'],last_error=ret['teb']['last_error']))
 assert any(r['name']=='OpenDesktopA' and r['stage_count']==0 and r['result']==0 and r['last_error']==2 for r in results)
 post=[r for r in results if r['name']=='OpenDesktopA' and r['stage_count'] in [5,10,15] and r['desktop_name']=='XwnDesktop126_'+str(r['stage_count']//5-1)];assert post,'No post-close observation'
 return results,post
dest=k/'api-verification.json';assert not dest.exists();t=read(out/'trace.json');results,post=validate(t)
for n,h in t['dependencies'].items():assert sha(Path(n))==h
for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
cl=read(out/'closure.json');assert sha(Path(cl['private_disk']))==cl['private_disk_sha256']
a=read(out/'audit.json');cold=read(k/'verification.json');launch=read(out/'launch.json');assert launch['observer_closed'] and launch['observer_teardown_ok']
assert a['integrity_passed'] and a['strict_events_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return'] and cold['pagefile_unchanged']
if t['helper_succeeded']:assert t['probe_exit']['status']==0 and cold['cold_diagnostic_workload_passed']
else:assert t['probe_exit']['status']!=0 and not cold['cold_diagnostic_workload_passed']
rejected=[]
for name in ['teb','return-stack','pin','teardown']:
 m=copy.deepcopy(t)
 if name=='teb':m['api_calls'][0]['return']['teb']['last_error']^=1
 elif name=='return-stack':m['api_calls'][0]['return']['registers']['ESP']+=4
 elif name=='pin':m['pins'][0]['resident']='00'+m['pins'][0]['resident'][2:]
 else:m['guest_resumed']=False
 try:validate(m)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Mutation accepted: '+name)
r=dict(observation_verified=True,full_workload_qualified=cold['cold_diagnostic_workload_passed'],ordinary_qualified=False,physical_qualified=False,surface_recreation_qualified=False,probe_exit_status=t['probe_exit']['status'],markers=len(t['desktop_stages']),watched_driver_calls=[r['name'] for r in t['desktop_calls']],api_calls=results,post_close_opens=post,teardown_verified=True,pins=len(t['pins']),mutations_rejected=rejected,trace_sha256=sha(out/'trace.json'),cold_verification_sha256=sha(k/'verification.json'),verifier_sha256=sha(Path(__file__)),limits='Successful API observation is separate from workload qualification; no immediate desktop destruction or driver fault inferred.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
