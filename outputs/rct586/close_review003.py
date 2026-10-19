"""MIT. Close two-phase PC save/load control from cold records and observed images."""
import datetime,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn586/pc001')
sys.path.insert(0,str(W/'work/python-packages'));from Registry import Registry
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'final002.json';assert not out.exists()
states=[json.loads((K/f'ntfs-phase{n}.json').read_text()) for n in (1,2)]
colds=[json.loads((K/f'ntfs-cold{n}-002.json').read_text()) for n in (0,1,2)]
manifests=[json.loads((P/f'cold{n}-002/manifest.json').read_text()) for n in (0,1,2)]
assert all(s['closed'] for s in states) and all(c['complete'] for c in colds)
assert sha(P/'disk.qcow2')==states[-1]['disk_sha256']==colds[-1]['disk_sha256']
def subtree(path):
 hive=Registry.Registry(str(path))
 try:key=hive.open('Fish Technology Group')
 except Registry.RegistryKeyNotFoundException:return None
 def node(k):return dict(values=sorted((v.name(),v.value_type(),repr(v.value())) for v in k.values()),children={x.name():node(x) for x in k.subkeys()})
 return node(key)
trees=[subtree(P/f'cold{n}-002/files/WINNT/system32/config/software') for n in (0,1,2)]
checks={};phases=[]
for n,(state,cold) in enumerate(zip(states,colds[1:]),1):
 log=(P/f'collection00{n}/runner.txt').read_text();fields={}
 for line in log.splitlines():
  if '=' in line:
   key,value=line.split('=',1);fields.setdefault(key,[]).append(value)
 one=dict(normal_vm_exit=state['exit_code']==0 and not any(state.get(x) for x in ['host_quit','host_terminate','host_kill','deadline','space_stop']),
   normal_shutdown=cold['normal_shutdown_delta']==1,source_unchanged=state['source_unchanged'] and cold['source_unchanged'],
   media_unchanged=state['iso_unchanged'],disk_audit_unchanged=cold['audit_unchanged'],
   hives_clean=all(h['header_valid'] and h['clean'] and h['independent_raw_values_agree'] for h in cold['hives']),
   registry_restored=trees[n]==trees[n-1],runner_registry_restored=fields.get('registry_restored')==['1'],
   game_exit=fields.get('game_exit')==['0'],no_forced_game_termination='forced_terminate' not in fields,
   desktop_restored=fields.get('desktop_restored')==['1'],restart_requested=fields.get('restart_requested')==['1'])
 phases.append(dict(phase=n,checks=one,new_system_events=cold.get('new_system_events'),
  runner_sha256=sha(P/f'collection00{n}/runner.txt'),manual_sequence_field=fields.get('input_sequence_submitted')))
 checks[f'phase{n}']=all(one.values())
name='xwn586-kit/game/saved games/xwn586.sv4';a,b=manifests[1][name],manifests[2][name]
checks['new_save_created']=name not in manifests[0] and a['bytes']==290242
checks['save_unchanged_after_load']=a==b and sha(P/'cold2-002/files'/b['path'])==a['sha256']
assets=json.loads((K/'asset-integrity001.json').read_text())
mutable={'game/Data/CSS0.DAT','game/Data/Game.cfg'}
checks['all_500_immutable_assets_unchanged']=len(assets)==502 and all(all(m['xwn586-kit/'+name.lower()]['sha256']==row['sha256'] for name,row in assets.items() if name not in mutable) for m in manifests[1:])
checks['documented_mutable_files_retained']=all(all('xwn586-kit/'+name.lower() in m for name in mutable) for m in manifests[1:])
media=json.loads((K/'phase2-source/media001.json').read_text())
checks['phase2_helper_exact']=manifests[2]['xwn586-kit/load586.exe']['sha256']==media['exe_sha256']
visual=json.loads((K/'load-visual001.json').read_text());checks['observed_load_restores_scene']=visual['passed']
checks['phase1_save_receipt']=json.loads((K/'save-readback001.json').read_text())['passed']
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=all(checks.values()),checks=checks,
 phases=phases,save=a,disk_sha256=states[-1]['disk_sha256'],physical_access=False,
 limits='One paused windowed PC save/restart/load control. No Xbox FATX save/reload, all-game-state, FPS, GPU or sound qualification. Typed hive decoder limitations remain in cold receipts.',
 failures_preserved=['preparation001-failure.json','launch-preflight001-failure.json','phase2-launch-text-failure001.json','phase1-observations001.json','final001.json','asset-postrun-differences001.json'],
 next='Watched Xbox save/restart/load with a fresh attempt, or fresh pristine fixed-scene rendering API observation; never reuse this closed runtime.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(checks));assert r['passed']
