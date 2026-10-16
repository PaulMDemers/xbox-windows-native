"""Read-only selected boot configuration comparison; never edits a hive."""
import configparser
import hashlib
import json
import struct
import sys
from pathlib import Path

K=Path(__file__).resolve().parent
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex


def values(h,path,keys):
    n=h.root()
    for part in path.split('\\'):
        n=h.node_get_child(n,part)
        if not n:return {key:None for key in keys}
    found={h.value_key(v).lower():h.value_value(v) for v in h.node_values(n)}
    result={}
    for key in keys:
        v=found.get(key.lower())
        if v is None:result[key]=None;continue
        t,b=v
        if t==4 and len(b)==4:decoded=struct.unpack('<I',b)[0]
        elif t in [1,2,7]:decoded=b.decode('utf-16le').rstrip('\0').split('\0') if t==7 else b.decode('utf-16le').rstrip('\0')
        else:decoded=b.hex()
        result[key]=dict(type=t,value=decoded)
    return result


snapshots={}
for phase in ['demo','fresh']:
    root=Path('/mnt/e/xwn415')/phase
    hive=root/'winnt/system32/config/system'
    before=hashlib.sha256(hive.read_bytes()).hexdigest()
    h=hivex.Hivex(str(hive))
    select=values(h,'Select',['Current','Default','LastKnownGood','Failed'])
    current=select['Current']['value'];cs=f'ControlSet{current:03d}'
    r=dict(select=select,active_control_set=cs,services={})
    for service in ['XwnFatx','XboxVnt5','nvnetnt5','xwnaci207','PciIde','atapi','openhci','usbhub','HidUsb','kbdhid','mouhid','kbdclass','mouclass','HidServ','VgaSave']:
        r['services'][service]=values(h,cs+'\\Services\\'+service,['Start','Type','Group','ImagePath','ErrorControl'])
    r['video']=values(h,cs+'\\Services\\XboxVnt5\\Device0',[
        'InstalledDisplayDrivers','VgaCompatible','DefaultSettings.XResolution','DefaultSettings.YResolution',
        'DefaultSettings.BitsPerPel','DefaultSettings.VRefresh'])
    r['crash_control']=values(h,cs+'\\Control\\CrashControl',['CrashDumpEnabled','AutoReboot','LogEvent'])
    r['pagefile']=values(h,cs+'\\Control\\Session Manager\\Memory Management',['PagingFiles'])
    r['C_mount']=values(h,'MountedDevices',['\\DosDevices\\C:'])
    r['critical_devices']={}
    for device in ['pci#ven_10de&dev_01bc','pci#ven_10de&dev_02a0','pci#ven_10de&dev_01c2','usb#root_hub','usb#class_03','hid_device_system_keyboard','hid_device_system_mouse']:
        r['critical_devices'][device]=values(h,cs+'\\Control\\CriticalDeviceDatabase\\'+device,['Service','ClassGUID'])
    del h
    assert hashlib.sha256(hive.read_bytes()).hexdigest()==before
    r['hive_sha256']=before
    snapshots[phase]=r
differences=[]
def walk(a,b,path=''):
    for key in a.keys()|b.keys():
        va,vb=a.get(key),b.get(key);p=path+'/'+key
        if isinstance(va,dict) and isinstance(vb,dict):walk(va,vb,p)
        elif va!=vb:differences.append(dict(path=p,demo=va,fresh=vb))
walk(snapshots['demo'],snapshots['fresh'])
r=dict(readonly=True,physical_writes=False,scope='Selected active-control-set values, not full PnP or registry equivalence',
       snapshots=snapshots,differences=differences)
with (K/'registry001.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(differences,indent=2))
