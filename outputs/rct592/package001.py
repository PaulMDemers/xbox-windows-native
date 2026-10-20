"""Freeze unchanged PC-qualified helper for one explicitly requested watched rerun."""
import ast,datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists() and not (K/'console-space001.json').exists()
assert read(K/'ready001.json')['watched_retry_requested']
old=K.parent/'rct591';final=read(old/'final001.json');assert final['closed'] and not final['phase1_save_passed'] and not final['runner_output_present'] and not final['new_save_present']
assert all(final['cleanup_checks'].values())
q=read(old/'package001.json');st=read(old/'stage001.json');col=read(old/'collection001.json')
assert st['completed'] and col['completed'] and col['hook_removed']
for p,h in q['pins'].items():assert sha(p)==h,p
for n,r in q['files'].items():assert Path(r['path']).stat().st_size==r['bytes'] and sha(r['path'])==r['sha256']
existing={n:dict(bytes=r['bytes'],sha256=r['sha256']) for n,r in st['staged'].items()}
for n,r in col['files'].items():
 if n in existing:assert r['sha256']==existing[n]['sha256'] and r['bytes']==existing[n]['bytes'],n
used='/E/xwn586-kit/startup-used591.cmd';r=col['files'][used];assert sha(r['path'])==r['sha256'];existing[used]=dict(bytes=r['bytes'],sha256=r['sha256'])
expected={n[len('/E/xwn586-kit/game/'):]:r for n,r in existing.items() if n.startswith('/E/xwn586-kit/game/')}
assert len(expected)==502 and set(col['game_rows'])=={'/E/xwn586-kit/game/'+n for n in expected}
assert not col.get('result_directory')
test=read(K/'controller-host001.json');assert test['passed'] and test['source_sha256']==sha(K/'controller001.py')
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
space=read(old/'console-space001.json');remaining=space['projected_remaining_bytes']-64*1024**2;assert remaining>=128*1024**2
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=importlib.util.spec_from_file_location('package592controller',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
(K/'console-space001.json').write_text(json.dumps(dict(admitted=True,fresh_free_space_measurement=False,source='Prior591 conservative allowance plus64MiB for592; existing game/helper retained',previous_remaining=space['projected_remaining_bytes'],new_allowance=64*1024**2,projected_remaining_bytes=remaining,minimum_spare_bytes=128*1024**2),indent=2)+'\n')
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(q['pins'])
for n in ['package001.json','stage001.json','collection001.json','final001.json']:
 p=old/n;pins[str(p.resolve())]=sha(p)
for module in list(sys.modules.values()):
 n=getattr(module,'__file__',None)
 if n:
  p=Path(n).resolve()
  if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_attempt=592,prior_closed_attempt=591,pc_probe=586,phase=1,allowed_launches=1,watched_retry_explicitly_requested=True,cold_start_confirmed=False,files=q['files'],existing_payload=existing,reuse_expected=expected,runtime_module_pins=q['runtime_module_pins'],pins=pins,phase2_loader=q['phase2_loader'],source_binary_unchanged=True,prior_runtime_reopened=False,physical_access=False,host_space=dict(free_bytes=free,projected_new_bytes=128*1024**2,minimum_free_bytes=20*1024**3),limits='Fresh watched physical attempt; existing result namespace must be absent. No new PC/graphics qualification.')
out.write_text(json.dumps(r,indent=2)+'\n');print('Frozen592 with',len(existing),'verified existing payload files')
