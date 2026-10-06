"""Cold audit of actual NT5 display installation or subsequent ordinary graphics boot."""
import importlib,json,subprocess,sys,struct
from pathlib import Path
root=Path(__file__).resolve().parent;ws=root.parents[1]
case=sys.argv[1];assert case in ['001','002','003','004','005'];k=root/case;k.mkdir(exist_ok=True)
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
run=ws/('work/runs/nt5-video-nt5-display-package-'+case);assert (run/'cleanup.json').exists()
fixture=json.loads((root/('fixture-'+case+'.json')).read_text())
base=ws/('outputs/native-windows-fatx-forensics/artifacts/video-nt5-display-package-'+case+'.qcow2')
assert m.filehash(base)==fixture['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
def readers(disk):
    io=m.SliceIO(disk)
    return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
before=readers(base);after=readers(run/'hdd.qcow2')
r=dict(scope=__doc__,case=case,physical_access=False,payloads=[],baseline_checks={})
for row in fixture['payloads']:
    if row['path']=='winnt/system32/xwn-video-trace.bin':continue
    actual=m.sha(after['F'].read(row['path']))
    r['payloads'].append(dict(path=row['path'],sha256=actual,matched=actual==row['sha256']))
for letter,path in [('F','winnt/system32/drivers/xwnfatx.sys'),('E','Applications/XWNFBoot/loader/halxboxnt5.dll'),
                    ('E','Applications/XWNFBoot/default.xbe'),('E','Applications/XWNFBoot/freeldr.sys')]:
    r['baseline_checks'][letter+'/'+path]=before[letter].read(path)==after[letter].read(path)
out=k/'artifacts';out.mkdir(exist_ok=True)
if case=='004':
    trace=after['F'].read('winnt/system32/xwn-video-trace.bin');(out/'video-trace.bin').write_bytes(trace)
    count=int.from_bytes(trace[16:20],'little');assert len(trace)==4096 and count<=254
    r['cold_trace_records']=[[hex(v) for v in struct.unpack_from('<4I',trace,32+i*16)] for i in range(count)]
if case=='001':
    try:log=after['F'].read('xwninf01/install.log')
    except KeyError:log=b''
    (out/'install.log').write_bytes(log);r['installer_log_present']=bool(log)
    r['installer_log']=log.decode('ascii');r['installation_api_succeeded']='UPDATE_SUCCESS\r\n' in r['installer_log'] and r['installer_log'].endswith('NORMAL_RESTART_REQUEST\r\n')
else:r['installation_api_succeeded']=None
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
launch=json.loads((k/'launch.json').read_text())
r['one_dashboard_return']=len(launch['cycles'])==1 and all(v.get('dashboard_return') for v in launch['cycles'])
system=out/'after-system';system.write_bytes(after['F'].read('winnt/system32/config/system'))
h=hivex.Hivex(str(system))
def node(path):
    n=h.root()
    for part in path.split('\\'):
        n=h.node_get_child(n,part)
        if not n:return 0
    return n
def values(path):
    n=node(path)
    if not n:return {}
    result={}
    for v in h.node_values(n):
        t,data=h.value_value(v)
        result[h.value_key(v)]=int.from_bytes(data,'little') if t==4 else (data.decode('utf-16le').rstrip('\0') if t in [1,2,7] else data.hex())
    return result
current=values('Select')['Current'];cs='ControlSet%03d'%current
device=cs+r'\Enum\PCI\VEN_10DE&DEV_02A0&SUBSYS_00000000&REV_A1\3&477a1ca&0&00F0'
r['device']=values(device);driver=r['device'].get('Driver','')
r['install_flags_cleared']=r['device'].get('ConfigFlags')==0
r['driver_key']=values(cs+'\\Control\\Class\\'+driver) if driver else {}
r['service']=values(cs+'\\Services\\XboxVnt5')
if case=='005':r['system_start_retained']=r['service'].get('Start')==1
r['device0']=values(cs+'\\Services\\XboxVnt5\\Device0')
if case in ['003','004','005']:
    try:display=after['F'].read('winnt/system32/xwnfb.dll')
    except KeyError:display=b''
    r['installed_owned_display_sha256']=m.sha(display)
    r['installed_owned_display_exact']=display==before['F'].read('xwninf01/xwnfb.dll')
    r['owned_display_registered']=any(v.get('InstalledDisplayDrivers')=='xwnfb' for v in [r['device0'],r['driver_key']])
r['pnp_binding_present']=bool(driver) and r['device'].get('Service','').lower()=='xboxvnt5' and r['driver_key'].get('InfSection','').lower()=='xbox.install' and r['install_flags_cleared']
inf=r['driver_key'].get('InfPath')
if inf:
    infdata=after['F'].read('winnt/inf/'+inf)
    (out/'installed.inf').write_bytes(infdata)
    r['installed_inf_exact']=infdata==before['F'].read('xwninf01/xboxvnt5.inf')
else:r['installed_inf_exact']=False
raw_before=before['F'].read('winnt/setupapi.log');raw_after=after['F'].read('winnt/setupapi.log')
(out/'after-setupapi.log').write_bytes(raw_after)
assert raw_after.startswith(raw_before),'SetupAPI prefix changed'
r['new_setupapi_lines']=raw_after[len(raw_before):].decode('cp1252').splitlines()
r['graphics_check_required']=case!='001'
if case!='001':
    workload='xwnlag02/' if case in ['004','005'] else 'xwnlag01/'
    try:log=after['F'].read(workload+'gdi-baseline.txt').decode('ascii')
    except KeyError:log=''
    try:attempt=after['F'].read(workload+'attempt.log').decode('ascii')
    except KeyError:attempt=''
    r['graphics_log']=log;r['graphics_attempt']=attempt
    r['graphics_passed']=log.endswith('PASS 0 0 0\r\n') and 'FAIL' not in log and all(f'COPY_stage_pass {i} 1 0\r\n' in log for i in range(4)) and sum(v.startswith('TIMING_kind_count_ms ') for v in log.splitlines())==5 and attempt=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
r['passed']=all([all(v['matched'] for v in r['payloads']),all(r['baseline_checks'].values()),r['one_dashboard_return'],r['normal_shutdown_count']==1,
 not r['unexpected_errors'],not r['new_popup_records'],not events['application'],r['installation_api_succeeded'] if case=='001' else True,r['pnp_binding_present'],r['installed_inf_exact'],r.get('graphics_passed',case=='001')])
if case in ['003','004','005']:r['passed'] &= r['installed_owned_display_exact'] and r['owned_display_registered']
if case=='005':
    r['passed'] &= r['system_start_retained']
    r['package_qualified']=False
    r['diagnostic_only']='An offline Start=1 intervention is not a corrected installer or demand-start qualification.'
r['limits']='Ordinary owned synthetic-resource xemu only, diagnostic audio flags inherited. Not hardware, full allocation, performance, or arbitrary PnP lifetime qualification.'
(k/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','installation_api_succeeded','pnp_binding_present','installed_inf_exact','normal_shutdown_count','unexpected_errors','new_popup_records']},indent=2))
