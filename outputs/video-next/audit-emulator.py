"""Cold GDI probe result audit, after the owned emulator has closed."""
import importlib,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
run=m.ws/'work/runs/nt5-gdi-baseline-001';assert (run/'cleanup.json').exists()
disk=run/'hdd.qcow2';f=m.SliceIO(disk);m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
w=m.Writer(f,m.fatx.open_partition(f,disk,'F'));out=k/'artifacts/emulator-001';out.mkdir(exist_ok=True)
result=dict(scope='Emulator correctness and cold result persistence, not physical performance or full filesystem audit',run=run.name)
for name in ['gdi-baseline.txt','attempt.log']:
    data=w.read('xwnpaint/'+name);(out/name).write_bytes(data);result[name]=data.decode('ascii')
log=result['gdi-baseline.txt']
result['copy_right_down_passed']='COPY_RIGHT_DOWN 1 0 0\r\n' in log
result['copy_left_up_passed']='COPY_LEFT_UP 1 0 0\r\n' in log
result['probe_passed']=log.endswith('PASS 0 0 0\r\n') and 'FAIL' not in log
result['runner_normal_restart_requested']='NORMAL_RESTART_REQUEST' in result['attempt.log']
result['timings_emulated_only']=[]
for line in log.splitlines():
    if line.startswith('TIMING_kind_count_ms '):
        kind,count,ms=map(int,line.split()[1:]);assert count>0
        result['timings_emulated_only'].append(dict(kind=kind,operations=count,milliseconds=ms))
assert [x['kind'] for x in result['timings_emulated_only']]==list(range(5))
for row in json.loads((k/'fixture.json').read_text())['payloads']:
    assert m.sha(w.read(row['path']))==row['sha256']
result['drivers']={}
for name,key in [('xwnfatx.sys','filesystem_sha256'),('xboxvnt5.sys','miniport_sha256')]:
    expected=json.loads((m.k/'fixture.json').read_text())[key]
    actual=m.sha(w.read('winnt/system32/drivers/'+name));assert actual==expected
    result['drivers'][name]=actual
for name in ['sysevent.evt','appevent.evt']:(out/name).write_bytes(w.read('winnt/system32/config/'+name))
result.update(passed=result['probe_passed'] and result['copy_right_down_passed'] and result['copy_left_up_passed'],
              physical_access=False,event_review_pending=True)
(k/'emulator-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
