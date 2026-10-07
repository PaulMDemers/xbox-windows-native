"""Correlate observed cache/IRP buffers with exact cold log ranges, no physical claim."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='001';out=k/case
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
dest=out/'buffer-analysis.json';assert not dest.exists()
t=read(out/'trace.json');sites=read(k/'sites.json');f=read(k/('fixture-'+case+'.json'))
assert sha((k/'trace.py').read_bytes())==t['source_sha256'] and sha((k/'sites.json').read_bytes())==t['sites_sha256']
assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
run=ws/('work/runs/nt5-fatx-cache-buffer-'+case);assert (run/'cleanup.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'));from coldio import ColdIO
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert m.filehash(base)==f['fixture_sha256']
modules=[]
for disk in [base,run/'hdd.qcow2']:
 with ColdIO(disk) as io:data=m.Writer(io,m.fatx.open_partition(io,disk,'F')).read('winnt/system32/drivers/xwnfatx.sys')
 modules.append(dict(disk=disk.name,sha256=sha(data),matched=sha(data)==sites['driver_sha256']))
assert all(v['matched'] for v in modules)
al=read(out/'alignment.json');cold=(out/'artifacts/after-setupapi.log').read_bytes();assert sha(cold)==al['after_sha256']
target=al['desired_offset'];end=target+al['expected_warning_bytes'];returns={v['entry_index']:v for v in t['events'] if 'entry_index' in v}
rows=[]
for e in t['events']:
 if not e.get('buffer_file'):continue
 data=(out/'artifacts'/e['buffer_file']).read_bytes();assert sha(data)==e['buffer_sha256'] and len(data)==e['length']
 offset=e['byteoffset'];explicit=offset>=0;lo=max(target,offset);hi=min(end,offset+len(data))
 overlap=explicit and lo<hi
 ret=returns.get(e['index']);success=bool(ret and ((e['kind']=='cache_call' and ret.get('returned_boolean')) or (e['kind']=='write_entry' and ret.get('status')==0)))
 row=dict(index=e['index'],kind=e['kind'],path=e['path'],pid=e['pid'],image=e['image'],offset=offset,length=len(data),source_sha256=sha(data),paging_io=bool(e.get('flags',0)&2),explicit_offset=explicit,return_event=ret,
          reported_success=success,source_matches_cold_full_range=explicit and cold[offset:offset+len(data)]==data,
          target_overlap_bytes=hi-lo if overlap else 0,target_overlap_start=lo if overlap else None,
          target_overlap_matches=bool(overlap and data[lo-offset:hi-offset]==cold[lo:hi]),
          target_full_span_observed=explicit and offset<=target and offset+len(data)>=end,
          first111_observed=explicit and offset<=target and offset+len(data)>=target+111)
 rows.append(row)
cache=[v for v in rows if v['kind']=='cache_call' and v['target_full_span_observed']]
paging=[v for v in rows if v['kind']=='write_entry' and v['paging_io'] and v['target_overlap_bytes']]
coverage=bool(cache and all(v['target_overlap_matches'] and v['reported_success'] for v in cache))
matched_pages=set()
for v in paging:
 if v['target_overlap_matches'] and v['reported_success']:
  matched_pages.update(range(v['target_overlap_start'],v['target_overlap_start']+v['target_overlap_bytes']))
a=read(out/'audit.json');v=read(out/'allocation.json');p=read(out/'package-audit.json')
r=dict(scope=__doc__,case=case,debugger_observation=True,physical_qualified=False,ordinary_qualified=False,trace_status=t['status'],driver_checks=modules,captured_buffers_verified=len(rows),requests=rows,
       target_cache_source_coverage=coverage,target_paging_source_coverage=all(i in matched_pages for i in range(target,end)),target_paging_matching_bytes=len(matched_pages),
       cache_target_requests=cache,paging_target_requests=paging,pending_write_count=t['pending_write_count'],pending_cache_count=t['pending_cache_count'],
       buffer_read_errors=[v for v in t['events'] if v.get('buffer_error') or v.get('buffer_unobserved')],
       cold_checks_passed=all([a['diagnostic_checks_passed'],p['installation_checks_passed'],v['allocation_consistent'],not v['errors'],not v['orphan_cluster_count'],al['actual_alignment_verified'],al['prefix_preserved'],al['target_warning_intact']]),
       trace_sha256=sha((out/'trace.json').read_bytes()),evidence_sha256={name:sha((out/name).read_bytes()) for name in ['audit.json','allocation.json','package-audit.json','alignment.json','collection.json','launch.json']},
       limits='Debugger timing differs. Cache source is captured immediately before CcCopyWrite, AL observed after. Paging source is an existing MDL system mapping observed at VfatWrite entry; it is not a DMA submission capture. VfatWrite success is before dispatch completion. Pending statuses are not successes. Full physical cause and original caller buffer remain unproven.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({key:r[key] for key in ['trace_status','captured_buffers_verified','target_cache_source_coverage','target_paging_source_coverage','target_paging_matching_bytes','cold_checks_passed']},indent=2))
