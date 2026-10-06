"""Cold strict audit for a one-device installer configuration experiment; no debugger or hardware access."""
import importlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent;ws=root.parents[1]
case=sys.argv[1];assert case in ['audio003','control003','pair004'];k=root/case
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
run=ws/('work/runs/nt5-video-installer-'+case);assert (run/'cleanup.json').exists()
fixture=json.loads((k/'fixture.json').read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts/gdi-baseline-003.qcow2'
assert m.filehash(base)==fixture['source_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
def readers(disk):
    io=m.SliceIO(disk)
    return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
before=readers(base);after=readers(run/'hdd.qcow2')
r=dict(scope=__doc__,physical_access=False,cycles=[],payloads=[],baseline_checks={})
for row in fixture['payloads']:
    if row['path']=='winnt/system32/xwn-video-trace.bin':continue
    actual=m.sha(after['F'].read(row['path']))
    r['payloads'].append(dict(path=row['path'],sha256=actual,matched=actual==row['sha256']))
for letter,path in [('F','winnt/system32/drivers/xwnfatx.sys'),('E','Applications/XWNFBoot/loader/halxboxnt5.dll'),
                    ('E','Applications/XWNFBoot/default.xbe'),('E','Applications/XWNFBoot/freeldr.sys')]:
    r['baseline_checks'][letter+'/'+path]=before[letter].read(path)==after[letter].read(path)
out=k/'artifacts';out.mkdir(exist_ok=True)
for index in [1]:
    logs={}
    for name in ['attempt.log','gdi-baseline.txt']:
        data=after['F'].read(f'xwnlag0{index}/'+name)
        (out/f'cycle{index}-{name}').write_bytes(data);logs[name]=data.decode('ascii')
    log=logs['gdi-baseline.txt'];runner=logs['attempt.log']
    ok=log.endswith('PASS 0 0 0\r\n') and 'FAIL' not in log and all(f'COPY_stage_pass {i} 1 0\r\n' in log for i in range(4))
    ok=ok and sum(v.startswith('TIMING_kind_count_ms ') for v in log.splitlines())==5
    restart=runner=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
    r['cycles'].append(dict(index=index,logs=logs,pixel_and_timing_workload_passed=ok,normal_restart_requested=restart))
events={};known=[]
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    for prefix,reader in [('before',before),('after',after)]:
        f=out/(prefix+'-'+name);f.write_bytes(reader['F'].read('winnt/system32/config/'+name))
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(f),'--output',str(k/(prefix+'-'+label+'-events.json'))],check=True,stdout=subprocess.DEVNULL)
    a=json.loads((k/('before-'+label+'-events.json')).read_text())['records'];b=json.loads((k/('after-'+label+'-events.json')).read_text())['records']
    by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a)
    known.extend(a);boundary=max((v['record'] for v in a),default=0)
    events[label]=[v for v in b if v['record']>boundary]
def recurring(v):
    return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
r['new_events']=events
r['unexpected_errors']=[v for group in events.values() for v in group if v['type'] in (1,2) and not recurring(v)]
r['new_popup_records']=[v for v in events['system'] if v['source']=='Application Popup']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in events['system'])
trace=after['F'].read('winnt/system32/xwn-video-trace.bin')
(out/'after-video-trace.bin').write_bytes(trace)
r['trace_valid']=len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n' and 1<=int.from_bytes(trace[16:20],'little')<=254 and int.from_bytes(trace[32:36],'little')==1
r['trace_sha256']=m.sha(trace)
launch=json.loads((k/'launch.json').read_text())
r['one_dashboard_return']=len(launch['cycles'])==1 and all(v.get('dashboard_return') for v in launch['cycles'])
subprocess.run([sys.executable,str(root/'decode-mapping.py'),str(out/'after-video-trace.bin'),'--output',str(k/'emulator-mapping.json')],check=True,stdout=subprocess.DEVNULL)
mapping=json.loads((k/'emulator-mapping.json').read_text())['mapping_observations']
r['direct_ram_uc_verified']=bool(mapping) and all(g['physical']==g['ram_offset'] and g['length']==0x400000 and all(g['pages'][str(i)].get('physical')==g['ram_offset']+(0 if i==0 else 0x3ff000) and g['pages'][str(i)].get('effective_type')=='UC' for i in [0,1]) for g in mapping)
r['passed']=all([all(v['matched'] for v in r['payloads']),all(r['baseline_checks'].values()),r['trace_valid'],
 r['direct_ram_uc_verified'],r['one_dashboard_return'],r['normal_shutdown_count']==1,not r['unexpected_errors'],not r['new_popup_records'],not events['application'],
 all(v['pixel_and_timing_workload_passed'] and v['normal_restart_requested'] for v in r['cycles'])])
r['limits']='One ordinary0097 display replacement boot with0096 miniport in owned synthetic-resource xemu; not hardware qualification, performance evidence, a full allocation audit, or PnP stop/remove qualification.'

sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
system=out/'after-system';system.write_bytes(after['F'].read('winnt/system32/config/system'))
h=hivex.Hivex(str(system));n=h.root()
for part in fixture['registry_edit']['path'].split('\\'):
    n=h.node_get_child(n,part);assert n
matches=[v for v in h.node_values(n) if h.value_key(v)=='ConfigFlags'];flags=h.value_dword(matches[0]) if matches else None
r['device_config_flags_after']=flags
r['expected_device_state_retained']=flags==fixture['registry_edit']['after']
r['additional_device_states']=[]
for edit in fixture['registry_edit'].get('additional_changes',[]):
    n=h.root()
    for part in edit['path'].split('\\'):
        n=h.node_get_child(n,part);assert n
    matches=[v for v in h.node_values(n) if h.value_key(v)=='ConfigFlags']
    actual=h.value_dword(matches[0]) if matches else None
    r['additional_device_states'].append(dict(path=edit['path'],actual=actual,matched=actual==edit['after']))
    r['expected_device_state_retained'] &= actual==edit['after']
raw_before=before['F'].read('winnt/setupapi.log');raw_after=after['F'].read('winnt/setupapi.log')
(out/'after-setupapi.log').write_bytes(raw_after)
assert raw_after.startswith(raw_before), 'SetupAPI prefix changed; do not infer new boundaries'
r['new_setupapi_lines']=raw_after[len(raw_before):].decode('cp1252').splitlines()
r['new_interactive_install_commands']=[v for v in r['new_setupapi_lines'] if 'rundll32.exe newdev.dll,DevInstall' in v]
r['passed']=r['passed'] and r['expected_device_state_retained']
r['limits']='Ordinary instrumented GDI boot in owned synthetic-resource xemu with a controlled device-install configuration; not a driver fix, hardware qualification, performance measurement, or full allocation/PnP audit.'

(k/'audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','trace_valid','one_dashboard_return','normal_shutdown_count','unexpected_errors']},indent=2))
