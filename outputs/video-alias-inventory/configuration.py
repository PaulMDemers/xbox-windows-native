"""Record cold inherited emulator-only PnP configuration without altering it."""
import sys
from common import *
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case,phase=sys.argv[1:];assert case in ['trace001'] and phase in ['before','after']
out=k/case;dest=out/(phase+'-configuration.json');assert not dest.exists()
f=read(k/('fixture-'+case+'.json'))
disk=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'] if phase=='before' else ws/('work/runs/nt5-valias-'+case+'/hdd.qcow2')
if phase=='before':assert sha(disk)==f['fixture_sha256']
else:assert (disk.parent/'cleanup.json').exists()
art=out/'artifacts';art.mkdir(exist_ok=True)
with ColdIO(disk) as io:
    rr=readers(io,disk);data=rr['F'].read('winnt/system32/config/system');hpath=art/(phase+'-configuration-system');hpath.write_bytes(data);h=hivex.Hivex(str(hpath))
    def node(path):
        n=h.root()
        for part in path.split('\\'):
            n=h.node_get_child(n,part)
            if not n:return 0
        return n
    def values(n):
        result={}
        for v in h.node_values(n):
            t,b=h.value_value(v);result[h.value_key(v)]=int.from_bytes(b,'little') if t==4 else b.decode('utf-16le').rstrip('\0') if t in [1,2,7] else b.hex()
        return result
    cs='ControlSet%03d'%values(node('Select'))['Current'];devices=[]
    for device in h.node_children(node(cs+r'\Enum\PCI')):
        for inst in h.node_children(device):
            devices.append(dict(id=h.node_name(device)+'\\'+h.node_name(inst),values=values(inst)))
    null=next(d for d in devices if d['id'].startswith('VEN_1B36&DEV_0005&'))['values']
    gpu=next(d for d in devices if d['id'].startswith('VEN_10DE&DEV_02A0&'))['values']
    key=values(node(cs+'\\Control\\Class\\'+null['Driver']))
    inf=rr['F'].read('winnt/inf/'+key['InfPath'])
    null_exact=inf==(k.parent/'shutdown-null-placeholder/xwntest.inf').read_bytes()
    failed={d['id']:d['values'].get('ConfigFlags',0) for d in devices if d['values'].get('ConfigFlags',0)&64}
    r=dict(phase=phase,case=case,physical_access=False,system_sha256=m.sha(data),devices=devices,null_driver_key=key,null_inf_sha256=m.sha(inf),null_inf_exact=null_exact,inherited_failedinstall=failed,gpu_bound=gpu.get('ConfigFlags')==0 and gpu.get('Service','').lower()=='xboxvnt5',null_bound=null_exact and null.get('ConfigFlags')==0 and not null.get('Service') and key.get('InfSection','').lower()=='xemu.null',note='Historical registry inventory, not live bus enumeration. Existing01B0/01B4 failed-install policy and synthetic null package are emulator limitations, not physical support or new edits.')
    r['expected_configuration']=r['gpu_bound'] and r['null_bound'] and len(failed)==2 and all(any(tag in name for tag in ['DEV_01B0&','DEV_01B4&']) and flags==64 for name,flags in failed.items())
save(dest,r);print('Expected inherited emulator configuration:',r['expected_configuration'])
assert r['expected_configuration']
