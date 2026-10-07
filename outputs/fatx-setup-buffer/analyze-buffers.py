"""Correlate SetupAPI append requests and reported write/flush results with cold bytes."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='001';out=k/case;dest=out/'buffer-analysis.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
t=read(out/'trace.json');s=read(k/'sites.json');f=read(k/('fixture-'+case+'.json'))
assert t['source_sha256']==sha((k/'trace.py').read_bytes()) and t['sites_sha256']==sha((k/'sites.json').read_bytes())
# A zero-hit trace disconnected during owned runner cleanup; retain that miss.
assert (t.get('guest_resumed') and not t['armed_breakpoints_remaining']) or (not t['records'] and not t['hit_counts'] and t['status']=='capture_incomplete')
run=ws/('work/runs/nt5-fatx-setup-buffer-'+case);assert (run/'cleanup.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'));from coldio import ColdIO
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512);base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert m.filehash(base)==f['fixture_sha256']
modules=[]
for disk in [base,run/'hdd.qcow2']:
 with ColdIO(disk) as io:data=m.Writer(io,m.fatx.open_partition(io,disk,'F')).read('winnt/system32/setupapi.dll')
 modules.append(dict(disk=disk.name,sha256=sha(data),matched=sha(data)==s['setupapi_sha256']))
assert all(v['matched'] for v in modules)
al=read(out/'alignment.json');cold=(out/'artifacts/after-setupapi.log').read_bytes();assert sha(cold)==al['after_sha256'];target=al['desired_offset'];expected=cold[target:target+al['expected_warning_bytes']]
rows=[]
for row in t['records']:
 if not row.get('buffer_file'):continue
 data=(out/'artifacts'/row['buffer_file']).read_bytes();assert sha(data)==row['source_sha256'] and len(data)==row['length']
 offset=row['file_end'];matches=offset!=0xffffffff and cold[offset:offset+len(data)]==data
 rows.append(dict(index=row['index'],pid=row['pid'],image=row['image'],file_end=offset,length=len(data),source_sha256=sha(data),warning_occurrences=row.get('warning_occurrences',0),write_bool=row.get('write_bool'),bytes_written=row.get('bytes_written'),flush_called=row.get('flush_called',False),flush_bool=row.get('flush_bool'),same_flush_handle=row.get('flush_handle')==row['handle'],no_overlapped=row.get('overlapped')=='0x0',source_matches_cold_at_seek_offset=matches,source_is_exact_warning=data==expected,source_first111_exact=data[:111]==expected[:111]))
warnings=[v for v in rows if v['warning_occurrences']];targets=[v for v in warnings if v['file_end']==target]
for v in warnings:v['reported_complete_write_and_flush']=bool(v['write_bool'] and v['bytes_written']==v['length'] and v['flush_called'] and v['flush_bool'] and v['same_flush_handle'] and v['no_overlapped'])
a=read(out/'audit.json');v=read(out/'allocation.json');p=read(out/'package-audit.json')
coverage=bool(t['status']=='three_warning_occurrences_flushed' and len(targets)==1 and targets[0]['source_is_exact_warning'] and targets[0]['source_matches_cold_at_seek_offset'] and targets[0]['reported_complete_write_and_flush'])
r=dict(scope=__doc__,case=case,debugger_observation=True,physical_qualified=False,ordinary_qualified=False,trace_status=t['status'],breakpoints_removed_before_disconnect=not bool(t['armed_breakpoints_remaining']),guest_resumed_by_tracer=t.get('guest_resumed',False),owned_runner_cleanup_present=True,setupapi_checks=modules,captured_requests_verified=len(rows),requests=rows,warning_requests=warnings,target_request=targets,target_source_and_cold_coverage=coverage,cold_checks_passed=all([a['diagnostic_checks_passed'],p['installation_checks_passed'],v['allocation_consistent'],not v['errors'],not v['orphan_cluster_count'],al['actual_alignment_verified'],al['prefix_preserved'],al['target_warning_intact']]),trace_sha256=sha((out/'trace.json').read_bytes()),evidence_sha256={name:sha((out/name).read_bytes()) for name in ['audit.json','allocation.json','package-audit.json','alignment.json','collection.json','launch.json']},limits='Debugger timing differs. File end is observed SetFilePointer(FILE_END) return, not yet independently read from a filesystem IRP. Reported WriteFile/Flush success plus exact cold bytes verifies this diagnostic request only; it does not observe cache/DMA buffers or explain the physical111-byte anomaly.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({key:r[key] for key in ['trace_status','captured_requests_verified','warning_requests','target_source_and_cold_coverage','cold_checks_passed']},indent=2))
