"""New244 runtime on immutable239 seed; no old case or frozen input edited."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-reference-pair243'
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-243.ps1','matrix.py','trace.py','freeze.py','test-close.py','test-connection.py','test-guards003.py','schema.py','test-pair.py']
for name in names:
 p=k/name.replace('Invoke-243','Invoke-244');assert not p.exists()
 s=(old/name).read_text(encoding='utf-8').replace('gpu-reference-pair243','gpu-lifecycle244').replace('phase243','phase244').replace('Invoke-243','Invoke-244')
 if name=='freeze.py':s=s.replace("k.parent/'gpu-reference-pair242/emulator-frozen.json'","k.parent/'gpu-reference-pair243/emulator-frozen.json'").replace('artifacts/build004','artifacts/build003')
 if name=='Run.ps1':
  s=s.replace('artifacts/build004/xemu-inventory242.exe','artifacts/build003/xemu-lifecycle244.exe').replace('build004.json','build003.json')
 if name=='Invoke-243.ps1':
  s=s.replace('inventory242-scratch','lifecycle244-scratch')
  anchor="        if ($UsbMouse)";assert s.count(anchor)==1
  s=s.replace(anchor,"        $vmArguments += @('-trace','enable=xwn_mem_callback244','-trace','enable=nv2a_lifecycle244')\n"+anchor)
 if name=='trace.py':
  s=s.replace("  preservation_experiment()","  response=cmd('qom-set '+r['nv2a_qom_path']+' xwn-lifecycle244-mark true');assert 'Error' not in response\n  preservation_experiment()")
  anchor=" if phase=='freeldr':take_snapshot";assert s.count(anchor)==1
  s=s.replace(anchor," # Existing CPU-exclusive queue may run while stopped. No wait under actor locks.\n time.sleep(.2)\n response=cmd('qom-set '+r['nv2a_qom_path']+' xwn-lifecycle244-mark true');assert 'Error' not in response\n for event in ['xwn_mem_callback244','nv2a_lifecycle244']:\n  response=cmd('trace-event '+event+' off');assert 'Error' not in response\n r['lifecycle_window_closed']=True;save()\n"+anchor)
 if name=='audit-emulator.py':
  s=s.replace("r['publication_limit']='242 finite before/after inventory during actual halted preservation; CPU callback queues and GL bindings unobserved, no reference retirement/native ownership/physical qualification.'","r['publication_limit']='244 lifecycle logs separately audited after host closure; no new cleanup, reference retirement or native ownership permission.'")
 p.write_text(s,encoding='utf-8')
for name in ['fixture-preserve001.json','fixture-seed001.json','inventory001.json','inventory.c']:
 shutil.copyfile(old/name,k/name)
for name in ['inputs','ram-source']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
shutil.copytree(old/'source',k/'source')
(k/'preserve001/artifacts').mkdir(parents=True)
for name in ['fixture-preserve001.json','fixture-seed001.json']:
 p=k/name;d=json.loads(p.read_text());d['new_unique_runtime']='nt5-phase244-preserve001';d['compiled_emulator_from']='outputs/gpu-lifecycle244/build003.json';d.pop('compiled_emulator_reused_from',None);p.write_text(json.dumps(d,indent=2)+'\n')
print('New244 host kit staged, immutable seed unchanged, no guest')
