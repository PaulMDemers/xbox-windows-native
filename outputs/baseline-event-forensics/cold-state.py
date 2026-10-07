"""Read owned closed emulator registry/files; no image modification or console access."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-map-rendezvous'))
from common import ColdIO,readers,sha
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
out=k/'cold-state.json';assert not out.exists()
case=k.parent/'fatx-map-rendezvous/flush001';closed=json.loads((case/'closure.json').read_text())
disk=ws/'work/runs/nt5-fatx-map-rendezvous-flush001/hdd.qcow2'
assert (disk.parent/'cleanup.json').exists() and sha(disk)==closed['private_disk_sha256']
art=k/'artifacts';art.mkdir(exist_ok=True)
with ColdIO(disk) as io:
    volumes=readers(io,disk);f=volumes['F'];data=f.read('winnt/system32/config/system')
    assert hashlib.sha256(data).hexdigest()==json.loads((case/'after-configuration.json').read_text())['system_sha256']
    hp=art/'system';hp.write_bytes(data);h=hivex.Hivex(str(hp))
    def node(path):
        n=h.root()
        for part in path.split('\\'):
            n=h.node_get_child(n,part)
            if not n:return 0
        return n
    def values(path):
        n=node(path)
        if not n:return None
        result={}
        for v in h.node_values(n):
            t,b=h.value_value(v)
            value=int.from_bytes(b,'little') if t==4 else b.decode('utf-16le').rstrip('\0') if t in [1,2,7] else b.hex()
            result[h.value_key(v)]=dict(type=t,value=value)
        return result
    select=values('Select');cs='ControlSet%03d'%select['Current']['value']
    paths=['Services\\HidServ','Services\\HidServ\\Parameters','Services\\Ftdisk',
           'Services\\EventLog\\System\\Service Control Manager','Services\\EventLog\\System\\Ftdisk',
           'Control\\Session Manager\\Memory Management','Control\\CrashControl']
    records={p:values(cs+'\\'+p) for p in paths}
    paths=['winnt/system32/hidserv.exe','winnt/system32/hidserv.dll','winnt/system32/drivers/ftdisk.sys',
           'winnt/system32/iologmsg.dll','winnt/system32/netevent.dll','winnt/system32/services.exe',
           'winnt/system32/kernel32.dll','pagefile.sys','winnt/system32/drivers/xwnfatx.sys']
    files=[]
    for path in paths:
        row=dict(path=path,present=False)
        try:
            blob=f.read(path);row.update(present=True,size=len(blob),sha256=hashlib.sha256(blob).hexdigest())
            if path!='pagefile.sys':
                target=art/path.replace('/','_');target.write_bytes(blob);row['private_copy']=target.name
        except KeyError:pass
        files.append(row)
r=dict(scope=__doc__,physical_access=False,disk=str(disk),disk_sha256=closed['private_disk_sha256'],system_sha256=hashlib.sha256(data).hexdigest(),select=select,control_set=cs,registry=records,files=files,limits='Closed emulator state only. File absence and configured paths are evidence, not a diagnosis of every loader/service failure. No pagefile contents or unrelated registry values retained.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
