"""Cold audit intentional crash once; no normal-shutdown or dump claim."""
import contextlib,subprocess
from common import *
case=sys.argv[1];assert case in ['control002','candidate002'];out=k/case;art=out/'artifacts';dest=out/'audit.json';assert not dest.exists()
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/reset221-runs/nt5-reset221-'+case);assert (run/'cleanup.json').exists()
f=read(k/('fixture-'+case+'.json'));base=Path(f['fixture_path_linux']);disk=run/'hdd.qcow2'
assert sha(base)==f['fixture_sha256'] and sha(Path(f['parent']))==f['parent_sha256']
r=dict(physical_access=False,intentional_crash=True,ordinary_qualified=False,physical_qualified=False,dump_qualified=False,files=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
 before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
 for name,digest in f['protected'].items():
  v,path=name.split('/',1)
  if path.startswith('winnt/system32/config/') or path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:continue
  actual=m.sha(after[v].read(path));r['files'].append(dict(path=name,expected_sha256=digest,actual_sha256=actual,matched=digest==actual))
 r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['files']['F/'+STARTUP]
 for n in HIVES:
  p=art/('after-'+n);p.write_bytes(after['F'].read('winnt/system32/config/'+n))
  try:row=hive(p)
  except Exception as exc:row=dict(parsed=False,error=repr(exc))
  r['hives'].append(dict(name=n,**row))
 try:intent=after['F'].read('xwnguard221/intent.log');(art/'intent.log').write_bytes(intent);r['intent']=intent.decode('ascii');r['intent_passed']=r['intent'].startswith('INTENT E058D221 44554D50 00000221 00010000 00000001\r\n') and r['intent'].endswith('TRIGGER_ONCE\r\n')
 except KeyError:r['intent_passed']=False
 for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
  pair=[]
  for phase,rr in [('before',before),('after',after)]:
   p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
   subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL);pair.append(read(d)['records'])
  boundary=max((v['record'] for v in pair[0]),default=0);r['new_events'][label]=[v for v in pair[1] if v['record']>boundary]
scan(disk,art);a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and r['startup_unchanged'] and all(v['matched'] for v in r['files']) and all(v['parsed'] for v in r['hives'])
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
t=read(out/'trace.json');r['trace_passed']=t['passed'];r['breakpoint_teardown_passed']=not t['remaining_breakpoints'] and t.get('guest_resumed') is True and not t.get('breakpoint_cleanup_errors')
r['guard_scope_passed']=r['intent_passed'] and r['integrity_passed'] and r['trace_passed'] and r['breakpoint_teardown_passed']
r['limits']='Corrected002 ABI observer; intentional debugger-mutated crash; selected protected hashes/hive structures/full allocation only, not all file content. No normal shutdown, recovered dump, GPU context or physical promotion.'
r['crash_disk_sha256']=sha(disk);r['cleanup_sha256']=sha(run/'cleanup.json');save(dest,r)
save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,audit_sha256=sha(dest),guard_scope_passed=r['guard_scope_passed'],intentional_crash=True,ordinary_qualified=False,physical_access=False))
print(json.dumps({n:r[n] for n in ['guard_scope_passed','integrity_passed','trace_passed','normal_shutdown_count']}))
