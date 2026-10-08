"""Offline verification of actual captured bytes/pairing, never ordinary qualification."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
t=read(out/'trace.json');sites=read(k/'sites.json');audit=read(out/'audit.json')
assert not (out/'trace-verification.json').exists()
assert t['source_sha256']==sha(k/'trace.py') and t['sites_sha256']==sha(k/'sites.json')
pin_checks=[]
for row in t['pins']:
 name=row['module']['name'];meta=sites['binaries'][name];p=ws/meta['path']
 assert sha(p)==meta['sha256']==row['source_sha256'];pe=pefile.PE(str(p))
 base=row['address']-row['rva'];raw=bytes.fromhex(row['raw']);assert raw==pe.get_data(row['rva'],len(raw))
 import struct
 relocated=bytearray(raw)
 rel=[e.rva-row['rva'] for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]) for e in block.entries if e.type==3 and row['rva']<=e.rva<row['rva']+len(raw)]
 assert rel==row['relocations']
 for off in rel:struct.pack_into('<I',relocated,off,(struct.unpack_from('<I',relocated,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 assert bytes(relocated).hex()==row['resident'] and row['module']['base']==base
 pin_checks.append(dict(module=name,rva=row['rva'],matched=True))
entries={v['index']:v for v in t['events'] if v['function']=='CreateProcessInternalW'}
returns=[v for v in t['events'] if v['function']=='CreateProcessInternalW_return'];pairs=[]
for v in returns:
 e=entries[v['entry_index']];c=v['call'];assert v['owner']['thread']==e['owner']['thread']==c['thread']
 assert v['registers']['ESP']==e['registers']['ESP']+48 and c['stack']==e['registers']['ESP']
 assert c['return_address']==e['caller']==v['registers']['EIP'] and c['result']==v['return_eax']
 assert c['parent_pid']==e['owner']['pid'] and c['returned']
 pairs.append(dict(entry=e['index'],returned=v['index'],parent=e['owner'],command_line=e.get('command_line'),application=e.get('application'),caller=e['caller'],caller_pin=e.get('caller_resident_pin'),result=v['return_eax'],process_information=v.get('process_information')))
assert len({v['entry'] for v in pairs})==len(pairs)
suspects=[v for v in pairs if 'rundll32' in ((v.get('command_line') or '')+' '+(v.get('application') or '')).lower()]
harderrors=[v for v in t['events'] if v['function']=='_NtRaiseHardError@24']
shutdown=[v for v in t['events'] if v['function']=='_NtShutdownSystem@4']
popups=[v for v in audit['new_events']['system'] if v['source']=='Application Popup']
teardown=not t.get('teardown_error') and t.get('breakpoints_after_teardown')==[] and t.get('guest_resumed') is True
r=dict(debugger=True,ordinary_qualified=False,physical_qualified=False,performance_qualified=False,
 trace_status=t['status'],trace_error=t.get('error'),resident_pins=pin_checks,creation_entries=len(entries),creation_pairs=pairs,
 rundll32_pairs=suspects,harderrors=harderrors,shutdown=shutdown,popups=popups,pending_returns=t['pending_returns'],
 unreadable_hits=t['unreadable_hits'],teardown_passed=teardown,
 diagnostic_capture_complete=teardown and not t.get('error') and len(pairs)>0 and len(shutdown)==1,
 workload_passed=audit['workload_passed'],integrity_passed=audit['integrity_passed'],strict_events_passed=audit['strict_events_passed'],
 limits='Read-only debugger scheduling differs from ordinary boot. No popup reproduction does not resolve prior ordinary failure. Child command is captured at creation in parent context; child PID is actual returned PROCESS_INFORMATION, not a later child-context read.')
(out/'trace-verification.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['trace_status','creation_entries','diagnostic_capture_complete','teardown_passed','workload_passed','integrity_passed','strict_events_passed']},indent=2))
