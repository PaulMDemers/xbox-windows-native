"""Unique observation runtime; unchanged native payload and never-executed seed."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'backend-actors267'
for n in ['common.py','atomic_json.py','kernel-discovery.py','close-host.py','typed-state.py','runtime-dependencies.py','attest.py','attestation-inputs001.json','analyze-base.py','analyze-extra.py','analyze-ledger.py']:
    assert not (k/n).exists();shutil.copyfile(p/n,k/n)
for n in ['run.py','Run.ps1','Invoke.ps1','audit.py','trace.py']:
    t=(p/n).read_text().replace('backend-actors267','unit-reuse269').replace('/actors267/','/reuse269/').replace('nt5-actors267','nt5-reuse269').replace('windows-native-actors267','windows-native-reuse269')
    if n=='Run.ps1':
        b=json.loads((k/'renderer-build005.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
        t=t.replace('actors267-build001/xemu-actors267.exe','reuse269-build005/xemu-reuse269.exe').replace('75494d6eecfc579d2d7bc77fadb89584d78ed191436ee23d06237fa518b98e38',b['executable_sha256'])
        anchor="$env:PYTHONUTF8='1'"
        t=t.replace(anchor,anchor+'''
$watch=Get-Content (Join-Path $out watch-location.json) -Raw | ConvertFrom-Json
if(-not (Test-Path $watch.path) -or (Get-ChildItem -LiteralPath $watch.path).Count){throw '269 requires unique empty capture directory'}
$env:XWN_REUSE269_DIR=$watch.path
''')
    if n=='run.py':
        anchor="    (run/'capture-complete.signal').touch(exist_ok=False);break"
        assert t.count(anchor)==1
        t=t.replace(anchor,"""    sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
    from monitor_capture import command,acquire_monitor_lock
    lock=acquire_monitor_lock(4594)
    try:
     command(4594,'stop')
     seal_deadline=time.monotonic()+5;seals=[]
     while True:
      response=command(4594,'qom-set -j '+trace['nv2a_path']+' xwn-ledger265 '+json.dumps('seal269'))
      seals.append(response)
      if 'Error' not in response:break
      assert time.monotonic()<seal_deadline,'Observer seal did not acknowledge'
      time.sleep(.02)
     (out/'watch-seal.json').write_text(json.dumps({'acknowledged':True,'responses':seals,'cpu_stopped':True},indent=2)+'\\n')
     terminal=command(4594,'qom-get '+trace['nv2a_path']+' xwn-ledger265-report')
     (out/'watch-terminal.txt').write_bytes(terminal.encode('utf-8'))
    finally:lock.close()
    (run/'capture-complete.signal').touch(exist_ok=False);break""")
    assert not (k/n).exists();(k/n).write_text(t)
out=k/'emu001';out.mkdir(exist_ok=False);shutil.copytree(p/'emu001/before',out/'before');(out/'artifacts').mkdir()
for n in ['system','software','default','sam','security']:shutil.copyfile(p/'emu001/artifacts'/('before-'+n),out/'artifacts'/('before-'+n))
f=json.loads((p/'emu001/fixture.json').read_text());f.update(new_unique_runtime='nt5-reuse269-emu001',compiled_emulator_from='E:/Codex-archive/xbox-windows-native/reuse269-build005',emulator_source_changed_only=json.loads((k/'renderer-build005.json').read_text())['changed_sources'],fixture_reuse='Never-executed265 standalone preparation.269 makes a fresh private runtime; no completed/interrupted run parent.')
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
watch=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/reuse269/watch-emu001');watch.mkdir(parents=True,exist_ok=False)
(out/'watch-location.json').write_text(json.dumps({'path':str(watch),'private_contents':True,'guest_writes':False},indent=2)+'\n')
print('269 unique runtime inputs and empty private capture directory prepared; no launch')
