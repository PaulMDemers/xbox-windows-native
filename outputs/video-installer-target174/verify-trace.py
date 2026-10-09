"""Verify captured code/return pairs; retain absent/failed child outcomes honestly."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
t=read(out/'trace.json');review=read(k/'sites.json');a=read(out/'audit.json')
dest=out/'trace-verification.json';assert not dest.exists()
assert t['source_sha256']==sha(k/'trace.py') and t['sites_sha256']==sha(k/'sites.json')
pins=[]
for row in t['pins']:
    name=row['module']['name'];meta=review['binaries'][name];file=ws/meta['path']
    assert sha(file)==meta['sha256']==row['source_sha256'];pe=pefile.PE(str(file))
    raw=bytes.fromhex(row['raw']);assert raw==pe.get_data(row['rva'],len(raw))
    base=row['address']-row['rva'];assert row['module']['base']==base
    rel=[e.rva-row['rva'] for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]) for e in block.entries if e.type==3 and row['rva']<=e.rva<row['rva']+len(raw)]
    assert rel==row['relocations'];data=bytearray(raw)
    for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    assert data.hex()==row['resident']
    if row['module'].get('identity'):
        assert row['header']['readable'] and row['header']['timestamp']==pe.FILE_HEADER.TimeDateStamp and row['header']['image_size']==pe.OPTIONAL_HEADER.SizeOfImage
    pins.append(dict(name=name,rva=row['rva'],matched=True,identity=row['module'].get('identity','actual loader/kernel')))
entries={v['index']:v for v in t['events'] if v.get('kind') in ['create_inner','create_outer']}
returns=[v for v in t['events'] if v['function'].endswith('_return')];pairs=[]
for v in returns:
    e=entries[v['entry_index']];c=v['call']
    assert e['owner']['thread']==v['owner']['thread']==c['thread']
    assert c['stack_delta']==48 and v['registers']['ESP']==e['registers']['ESP']+48
    assert c['stack']==e['registers']['ESP'] and c['return_address']==e['caller']==v['registers']['EIP']
    assert c['function']==e['function'] and v['function']==e['function']+'_return'
    assert c['result']==v['return_eax'] and c['returned']
    pairs.append(dict(entry=e['index'],returned=v['index'],function=e['function'],thread=e['owner']['thread'],parent=e['owner'],
        command_line=e.get('command_line'),application=e.get('application'),caller_identity=e.get('caller_identity'),
        result=v['return_eax'],last_error=v.get('last_error'),process_information=v.get('process_information')))
assert len({p['entry'] for p in pairs})==len(pairs)
installer=[p for p in pairs if 'rundll32' in ((p.get('command_line') or '')+' '+(p.get('application') or '')).lower()]
outer=[p for p in installer if p['function']=='CreateProcessAsUserW']
linked=[]
for p in outer:
    inner=[q for q in installer if q['function']=='CreateProcessInternalW' and q['thread']==p['thread'] and p['entry']<q['entry']<q['returned']<p['returned']]
    pi=p.get('process_information');pid=pi[2] if pi else None
    events=[e for e in t['events'] if e['index']>p['entry'] and pid is not None and e['owner']['pid']==pid and e.get('kind') in ['loader_entry','harderror','terminate']]
    linked.append(dict(outer=p,inner=inner,returned_child_pid=pid,child_events=events,
        correlation_limits='PID/order and current-process command only; PID reuse or unreadable command prevents a definitive lifecycle attribution. Loader entry is not completed initialization.'))
teardown=t.get('breakpoints_after_teardown')==[] and t.get('guest_resumed') is True and not t.get('teardown_error')
shutdown=[e for e in t['events'] if e.get('kind')=='shutdown']
harderrors=[e for e in t['events'] if e.get('kind')=='harderror']
popups=[e for e in a['new_events']['system'] if e['source']=='Application Popup']
r=dict(debugger=True,ordinary_qualified=False,physical_qualified=False,performance_qualified=False,trace_status=t['status'],trace_error=t.get('error'),
    resident_pins=pins,creation_entries=len(entries),creation_pairs=pairs,installer_pairs=installer,outer_installer_lifecycles=linked,
    shutdown=shutdown,harderrors=harderrors,popups=popups,pending_returns=t['pending_returns'],unreadable_hits=t['unreadable_hits'],teardown_passed=teardown,
    diagnostic_capture_complete=teardown and not t.get('error') and t['status']=='dashboard_observed' and bool(outer) and len(shutdown)==1,
    workload_passed=a['workload_passed'],integrity_passed=a['integrity_passed'],strict_events_passed=a['strict_events_passed'],
    limits='Debugger scheduling is not ordinary validation. Outer TRUE, loader entry and cold log absence separately do not prove full child startup or fix an intermittent popup. Failed BOOL makes LastError meaningful; TRUE does not.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({key:r[key] for key in ['trace_status','creation_entries','diagnostic_capture_complete','teardown_passed','workload_passed','integrity_passed','strict_events_passed']}))
