"""Preserve saturated observation as a failure, with strictly partial findings."""
import collections,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];o=k/'emu001'
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=read(o/'host-state.json');a=read(o/'audit.json');t=read(o/'trace.json')
assert host['closed'] and host['status']=='cold_audited' and all(host[n]==0 for n in ['runner_exit_code','tracer_exit_code','audit_exit_code'])
assert t['passed'] and t['closed'] and t['guest_resumed'] and t['remaining_breakpoints']==0 and t['physical_mode_restored']
assert a['ledger_diagnostic_passed'] and a['integrity_passed'] and a['orderly_host_exit_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return']
assert [(e['source'],e['event_id']) for e in a['warnings_errors']]==[('Ftdisk',49)] and not a['new_events']['application']
assert read(o/'watch-seal.json')['acknowledged']
spec=importlib.util.spec_from_file_location('base',k/'analyze-base.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
terminal=base.numbers((o/'watch-terminal.txt').read_text());assert terminal['reuse269_error']==3
spec=importlib.util.spec_from_file_location('watch',k/'analyze-watch.py');watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
folder=Path(read(o/'watch-location.json')['path']);events=[]
for seq,p in enumerate(sorted(folder.glob('event-*.txt'))):
    row={key:int(v) for key,v in re.findall(r'(\w+)=(\d+)',p.read_text())};assert row['seq']==seq;events.append(row)
assert len(events)==129 and events[-1]['kind']==9 and events[-1]['code']==1
assert collections.Counter(r['kind'] for r in events)=={1:1,2:1,3:126,9:1}
blobs={p.name:watch.decode(p.read_bytes()) for p in folder.glob('unit-*.bin')}
assert set(blobs)=={f'unit-{u}-stage-0.bin' for u in range(4)}|{'unit-0-stage-1.bin'}
before,before_bytes=blobs['unit-0-stage-0.bin'];after,after_bytes=blobs['unit-0-stage-1.bin']
rows=base.load(o,t,'ledger');unit0=next(r for r in rows if r[0]==3 and r[1]==0);binding=next(r for r in rows if r[0]==4 and r[1]==unit0[2])
assert before[5]==after[5]==unit0[2] and before[6]==after[6]==binding[3]
assert before[4]==after[4]==1 and before[21]==after[21]==terminal['worker']
bind=next(r for r in events if r['kind']==2);assert bind['unit']==0 and bind['identity']==before[5] and bind['code']==2
assert not any(r['kind']==4 for r in events[:bind['seq']])
equal=[x==y for x,y in zip(before_bytes,after_bytes)];assert equal==[True,False,True,False]
assert before[9]!=after[9]
failure=o/'watch-analysis-failure.json';assert not failure.exists()
p=subprocess.run([sys.executable,'-B',str(k/'analyze-watch.py')],capture_output=True,timeout=30)
assert p.returncode!=0 and not (o/'watch-analysis.json').exists()
failure.write_text(json.dumps({'passed':False,'exit_code':p.returncode,'output':(p.stdout+p.stderr).decode(errors='replace'),'expected_rejection':'Terminal observer overflow error3; never waive complete coverage'},indent=2)+'\n')
frozen=read(k/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
sp=importlib.util.spec_from_file_location('deps',k/'runtime-dependencies.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert m.inventory()==read(k/'host-dependencies.json')['files']
assert read(o/'actual-controls.json')['passed'] and read(o/'ledger-analysis.json')['unknown_actor_work']==0
alloc=read(o/'allocation.json');assert alloc['allocation_consistent'] and not alloc['orphan_cluster_count'] and not alloc['errors']
result={'closed':True,'never_relaunch_or_recollect':True,'reuse_qualification_passed':False,'complete_observation_passed':False,
    'failure':'129th event is explicit overflow marker after126 counted decrements and one real bind; terminal error3',
    'four_unit_unchanged_reuse_proved':False,'other_three_later_reuse':'Unknown after saturation; no later snapshot captured',
    'partial_unit0':{'actual_original_identity_bound':True,'cache_key_equal':equal[0],'source_equal':equal[1],'palette_equal':equal[2],'rgba_equal':equal[3],
        'draw_time_before':before[9],'draw_time_after':after[9],
        'changed_source_bytes':sum(x!=y for x,y in zip(before_bytes[1],after_bytes[1])),
        'changed_rgba_bytes':sum(x!=y for x,y in zip(before_bytes[3],after_bytes[3])),
        'not_a_preservation_failure':'Original ordinary rendered texture is updated; no release installed',
        'lifetime_scope':'Original generation until first bind; no claims after dropped events'},
    'ledger_diagnostic_passed':True,'strict_qualification_passed':False,'strict_event_failure':'Inherited Ftdisk49',
    'actual_native_attestations':len(t['checkpoints']),'exact_cpu_bytes':32768,'cpu_reads':2,'cpu_writes':0,
    'normal_guest_restart':True,'orderly_host_exit':True,'observer_sealed':True,
    'directories':alloc['directories'],'files':alloc['files'],'directory_clusters':alloc['directory_clusters'],'orphans':0,'allocation_errors':0,
    'hives':len(a['hives']),'protected_hashes':len(a['files']),'frozen_inputs':len(frozen),'host_dependencies':len(m.inventory()),
    'actual_graph_negatives':len(read(o/'actual-controls.json')['rejected_mutations']),'synthetic_watch_negatives':19,'gate_races':4096,
    'renderer_sha256':read(k/'renderer-build005.json')['executable_sha256'],
    'physical_access':False,'release_installed':False,'native_gpu_grant':False,'ordinary_qualified':False,'speedup_proved':False,
    'private_capture':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in folder.iterdir() if p.is_file()},
    'evidence_sha256':{p.relative_to(k).as_posix():sha(p) for p in [o/'trace.json',o/'audit.json',o/'watch-terminal.txt',o/'watch-seal.json',failure,o/'ledger-analysis.json',o/'actual-controls.json']}}
dest=k/'final-review.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:v for n,v in result.items() if n not in ['private_capture','evidence_sha256']},indent=2))
