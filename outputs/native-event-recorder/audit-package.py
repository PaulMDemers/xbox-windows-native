"""Inspect installed GPU registration and SetupAPI evidence after the host-recorder paired idle/restart test."""
import contextlib,importlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent;ws=root.parents[1]
case=sys.argv[1];assert case in ['001','002'];k=root/case
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'));from coldio import ColdIO
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
run=ws/('work/runs/nt5-native-event-recorder-'+case);assert (run/'cleanup.json').exists()
fixture=json.loads((root/('fixture-'+case+'.json')).read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture['fixture_name']
assert m.filehash(base)==fixture['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
out=k/'artifacts';out.mkdir(exist_ok=True)
r=dict(scope=__doc__,physical_access=False,case=case)
with contextlib.ExitStack() as stack:
    bio=stack.enter_context(ColdIO(base));aio=stack.enter_context(ColdIO(run/'hdd.qcow2'))
    before={'F':m.Writer(bio,m.fatx.open_partition(bio,base,'F'))}
    after={'F':m.Writer(aio,m.fatx.open_partition(aio,run/'hdd.qcow2','F'))}
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
    r['device0']=values(cs+'\\Services\\XboxVnt5\\Device0')
    r['pnp_binding_present']=bool(driver) and r['device'].get('Service','').lower()=='xboxvnt5' and r['driver_key'].get('InfSection','').lower()=='xbox.install' and r['install_flags_cleared']
    inf=r['driver_key'].get('InfPath')
    if inf:
        infdata=after['F'].read('winnt/inf/'+inf)
        (out/'installed.inf').write_bytes(infdata)
        r['installed_inf_exact']=infdata==(root.parent/'shutdown-device-install/xwnvideo.inf').read_bytes()
    else:r['installed_inf_exact']=False
    raw_before=before['F'].read('winnt/setupapi.log');raw_after=after['F'].read('winnt/setupapi.log')
    (out/'after-setupapi.log').write_bytes(raw_after)
    assert raw_after.startswith(raw_before),'SetupAPI prefix changed'
    r['new_setupapi_lines']=raw_after[len(raw_before):].decode('cp1252').splitlines()

    r['existing_display_registered']=any(v.get('InstalledDisplayDrivers')=='framebuf' for v in [r['device0'],r['driver_key']])
    r['display_binary_unchanged']=after['F'].read('winnt/system32/framebuf.dll')==before['F'].read('winnt/system32/framebuf.dll')
    r['miniport_unchanged']=after['F'].read('winnt/system32/drivers/xboxvnt5.sys')==before['F'].read('winnt/system32/drivers/xboxvnt5.sys')
workload=json.loads((k/'audit.json').read_text())
r['installation_checks_passed']=all([r['pnp_binding_present'],r['installed_inf_exact'],r['existing_display_registered'],r['display_binary_unchanged'],r['miniport_unchanged']])
r['combined_checks_passed']=r['installation_checks_passed'] and workload['diagnostic_checks_passed'] and workload['ordinary_run_valid']
r['hardware_qualified']=False
r['limits']='Cold installation evidence from a host-recorder experiment only; recording is enabled only in case002. This does not qualify an ordinary boot, fix the shutdown popup or qualify physical deployment.'
(k/'package-audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['installation_checks_passed','combined_checks_passed','device','service','driver_key']},indent=2))
