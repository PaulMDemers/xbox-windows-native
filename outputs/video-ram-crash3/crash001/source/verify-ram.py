"""Independent retained RAM ownership/text audit at real dump return."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'video-shared-trace2'));from walk import read_virtual
from residency import inspect_display
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');info=read(k/'modules.json')['xwnown.dll'];symbols=info['symbols']
assert read(k/'render-verification.json')['passed'] and read(k/'payload-verification.json')['passed']
assert not a['warnings_errors'] and not a['new_events']['application'] and a['event_history_preserved']
assert a['normal_shutdown_count']==0
before=t['ram_before'];after=t['ram_after'];base=before['base'];assert after['base']==base
assert before['lock'] and len(before['slots'])==1 and before['slots'][0]['pdev7'][6]==1
assert before==after,'Unexpected ownership transition requires investigation, not a waived gate'
assert not [e for e in t['events'] if e['kind']=='ram_callback_entry'],'Unexpected display callback requires interpretation'
raw=Path(t['private_memory']);assert sha(raw)==t['private_memory_sha256'];ram=raw.read_bytes();cr3=t['control_registers']['CR3']
rv=lambda at,n:read_virtual(ram,cr3,at,n)
assert rv(base+symbols['XwnOwners'],384).hex()==after['table_raw']
assert struct.unpack('<I',rv(base+symbols['XwnOwnerLock'],4))[0]==after['lock']
for row in after['slots']:
 assert list(struct.unpack('<7I',rv(row['owner'],28)))==row['pdev7']
 assert row['pdev7'][1:3]==[row['device'],row['surface']]
 assert all(row['pdev7'][i] for i in [0,1,2,3,4,5])
p=Path(info['path']);assert sha(p)==info['sha256'];pe=pefile.PE(str(p));sec=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
before_memory=t['before_memory'];bp=Path(before_memory['path']);assert sha(bp)==before_memory['sha256']
before_res=inspect_display(bp.read_bytes(),before_memory['control_registers']['CR3'],base,pe,symbols)
after_res=inspect_display(ram,cr3,base,pe,symbols)
assert before_res==t['ram_residency_before'] and after_res==t['ram_residency_after']
assert before_res==after_res
pins=[t['runtime_pins'][i] for i in t['ram_live_function_pins']]
assert [int(v['rva'],16) for v in pins]==[symbols[n] for n in ['XwnUpload','DrvAssertMode']]
assert all(v['module']=='xwnown.dll' for v in pins)
dis=t['kernel_discovery'];assert len(dis['gates'])==2 and all(v['base']==dis['kernel_base']==t['kernel_base'] for v in dis['gates'])
beforecfg,aftercfg=[read(out/(phase+'-configuration.json')) for phase in ['before','after']]
assert beforecfg['expected_configuration'] and aftercfg['expected_configuration']
assert beforecfg['devices']==aftercfg['devices']
r=dict(passed=True,strict_diagnostic_passed=True,physical_qualified=False,ordinary_qualified=False,recovery_qualified=False,physical_access=False,
 display_sha256=info['sha256'],display_text_bytes=sec.Misc_VirtualSize,mapped_display_text_bytes=after_res['mapped_bytes'],unmapped_display_text_bytes=after_res['unmapped_bytes'],owner_slots=len(after['slots']),ownership_retained=True,
 watched_ram_callbacks_observed=0,bootvid_functions=read(k/'render-verification.json')['observed_render_functions'],
 whole_display_text_residency_qualified=False,mapped_display_text_before_after_exact=True,event_deltas_clean=True,normal_shutdown_count=0,
 evidence={n:sha(k/n) for n in ['verification.json','payload-verification.json','render-verification.json','crash001/trace.json','crash001/audit.json','crash001/closure.json']},
 limits='One debugger-observed desktop-to-crash handoff; unmapped display code explicitly excluded from residency claim; active RAM registration retained. No claim of display teardown, arbitrary timing, physical support or recovery of this disk.')
dest=k/'ram-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
