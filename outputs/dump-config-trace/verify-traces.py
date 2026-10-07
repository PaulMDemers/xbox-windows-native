"""Replay resident-byte pins and paired diagnostic observations without rerunning guests."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
kernel=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe');kp=pefile.PE(str(kernel));fp=pefile.PE(str(k.parent/'fatx-directory-order/artifacts/xwnfatx.sys'))
results=[]
for case in ['serial001','serial002','serial003','serial004','serial005']:
 out=k/case;t=read(out/'trace.json');pre=read(out/'preflight.json');a=read(out/'audit.json')
 assert sha(out/'source/trace.py')==t['source_sha256']
 sitefile=next(n for n,d in pre['sources'].items() if d==t['sites_sha256']);sites=read(out/'source'/sitefile);assert sha(kernel)==sites['kernel_sha256']
 storage=read(out/'storage-binaries.json');assert storage['passed'] and len(storage['files'])==6
 for v in storage['files']:
  assert sha(out/'artifacts'/('before-'+v['name']))==v['sha256']==v['after_sha256']==sha(out/'artifacts'/('after-'+v['name']))
 assert t['guest_resumed'] and not t['armed_breakpoints_remaining'] and t['pending_calls']==0
 assert a['debugger'] and not a['ordinary_qualified'] and not a['strict_qualification_passed'] and not a['strict_events_passed']
 assert a['workload_and_persistence_passed'] and a['integrity_passed']
 assert [(e['source'],e['event_id']) for e in a['warnings_errors']]==[('Ftdisk',49)]
 for name,d in pre['sources'].items():assert sha(out/'source'/name)==d
 if case=='serial001':
  assert t['status']=='capture_incomplete' and t['error']=="AssertionError('No paired final return')" and not t['events']
  results.append(dict(case=case,diagnostic_passed=False,preserved_failure=t['error']));continue
 assert t['status']=='failure_path_captured' and not t['calls']
 events={e['kind']:e for e in t['events']};assert len(events)==len(t['events']) and len({e['thread'] for e in t['events'] if not e['kind'].startswith('fatx_pnp_')})==1
 cfg=events['configure_entry']['configure'];assert events['configure_handle_return']['status_or_pointer']=='0x0'
 assert events['dump_stack_return']['status_or_pointer']==events['caller_error']['status_or_pointer']=='0xc00000bb'
 assert int(events['caller_error']['registers']['EBP'],16)==cfg['frame'] and int(events['caller_error']['registers']['ESP'],16)==cfg['entry_stack']-32
 ss={e['name']:e for e in sites['sites']}
 for e in t['events']:
  pe=kp;base=sites['kernel_base_expected'];s=ss.get(e['kind'])
  if s is None:
   assert case=='serial005';f=read(out/'source/fatx-sites.json');assert sha(k.parent/'fatx-directory-order/artifacts/xwnfatx.sys')==f['driver_sha256']
   s=next(z for z in f['sites'] if z['name']==e['kind']);pe=fp;base=int(events['stack_usage_call']['driver']['base'],16)
  raw=pe.get_data(s['rva'],len(bytes.fromhex(s['raw'])));assert raw.hex()==s['raw'];data=bytearray(raw)
  relocs=[x.rva-s['rva'] for block in pe.DIRECTORY_ENTRY_BASERELOC for x in block.entries if x.type==3 and s['rva']<=x.rva<s['rva']+len(data)]
  assert relocs==s['relocations']
  for off in relocs:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
  assert e['resident_bytes']==data.hex() and int(e['registers']['EIP'],16)==base+s['rva']
 if case in ['serial003','serial004','serial005']:
  assert events['stack_build_call']['arguments'][0]=='0x41020' and events['stack_driver_effective']['effective_status']=='0x0'
  assert events['stack_final_return']['status']=='0xc00000bb'
 if case in ['serial004','serial005']:
  assert events['stack_load_miniport_return']['status_or_pointer']=='0x0'
  sl=bytes.fromhex(events['stack_usage_call']['usage_stack_location']);assert sl[:2]==bytes([0x1b,0x16]) and sl[4]==1 and int.from_bytes(sl[8:12],'little')==3
  assert events['stack_usage_return']['status_or_pointer']=='0xc00000bb'
 if case=='serial005':
  assert events['fatx_pnp_entry']['stack_location'][:4]=='1b16'
  assert events['fatx_pnp_return']['status']=='0x103'
  assert events['fatx_pnp_forward']['lower_driver']['name']=='\\Driver\\Ftdisk'
  assert events['fatx_pnp_entry']['paired_usage_event']==events['stack_usage_call']['index']
 results.append(dict(case=case,diagnostic_passed=True,hits=len(events),resident_pins_replayed=True,strict_qualification_passed=False))
p=k/'trace-verification.json';result=dict(scope=__doc__,results=results)
if p.exists():assert read(p)==result
else:p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(results,indent=2))
