"""Explicit PC-to-Xbox SYSTEM provisioning on a PRIVATE COPY, never an old hive."""
import hashlib, json, shutil, struct, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
P=Path('/mnt/c/xwn405/provision002'); SOURCE=Path('/mnt/c/xwn405/extract004/files')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
sys.path.insert(0,str(W/'outputs/native-windows-nt5-kernel'))
import hivex
from nt5_hive_indexes import normalize
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def snapshot(h):
    result={}; todo=[('',h.root())]
    while todo:
        path,n=todo.pop()
        for v in h.node_values(n):
            typ,b=h.value_value(v);result[path+'|'+h.value_key(v)]=[typ,b.hex()]
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return result
def node(h,path):
    n=h.root()
    for part in path.split('\\'):
        child=h.node_get_child(n,part)
        if not child:child=h.node_add_child(n,part)
        n=child
    return n
assert not P.exists() and json.loads((K/'extraction005.json').read_text())['status']=='extracted'
P.mkdir(parents=True)
files={p.relative_to(SOURCE).as_posix().lower():p for p in SOURCE.rglob('*') if p.is_file()}
r=dict(source='Fresh closed404 customized SP4 installation; no old Xbox hive/user payload',hives={},physical_access=False)
for name in ['system','software']:
    original=files['winnt/system32/config/'+name];target=P/name;shutil.copyfile(original,target)
    h=hivex.Hivex(str(target),write=True);before=snapshot(h);requested={}
    def value(path,key,typ,v):
        b=struct.pack('<I',v) if typ==4 else v if typ==3 else (('\0'.join(v)+'\0\0') if typ==7 else v+'\0').encode('utf-16le')
        h.node_set_value(node(h,path),dict(key=key,t=typ,value=b));requested[('\\'+path+'|'+key).lower()]=[typ,b.hex()]
    if name=='system':
        sets=[h.node_name(c) for c in h.node_children(h.root()) if h.node_name(c).startswith('ControlSet')]
        assert sets and all(len(cs)==13 and cs[10:].isdigit() for cs in sets)
        for cs in sets:
            def service(s,start,group,image,kind=1,error=1):
                p=cs+'\\Services\\'+s
                for key,val in [('Type',kind),('Start',start),('ErrorControl',error)]:value(p,key,4,val)
                value(p,'ImagePath',2,image);value(p,'Group',1,group)
            value(cs+'\\Services\\PciIde','Start',4,0)
            service('XwnFatx',0,'Boot File System','system32\\drivers\\xwnfatx.sys',2)
            service('XboxVnt5',1,'Video','system32\\drivers\\xboxvnt5.sys')
            p=cs+'\\Services\\XboxVnt5\\Device0'
            value(p,'InstalledDisplayDrivers',7,['xwnown']);value(p,'VgaCompatible',4,0)
            value(p,'Device Description',1,'Xbox firmware framebuffer')
            for k,v in [('XResolution',1280),('YResolution',720),('BitsPerPel',32),('VRefresh',60)]:value(p,'DefaultSettings.'+k,4,v)
            value(cs+'\\Services\\VgaSave','Start',4,4)
            bindings=[('pci#ven_10de&dev_01bc','pciide','{4D36E96A-E325-11CE-BFC1-08002BE10318}'),
              ('pci#ven_10de&dev_02a0','XboxVnt5','{4D36E968-E325-11CE-BFC1-08002BE10318}'),
              ('pci#ven_10de&dev_01c2','openhci','{36FC9E60-C465-11CF-8056-444553540000}'),
              ('usb#root_hub','usbhub','{36FC9E60-C465-11CF-8056-444553540000}'),
              ('usb#class_09','usbhub','{36FC9E60-C465-11CF-8056-444553540000}'),
              ('usb#class_03','HidUsb','{745A17A0-74D3-11D0-B6FE-00A0C90F57DA}'),
              ('hid_device_system_keyboard','kbdhid','{4D36E96B-E325-11CE-BFC1-08002BE10318}'),
              ('hid_device_system_mouse','mouhid','{4D36E96F-E325-11CE-BFC1-08002BE10318}')]
            for device,s,guid in bindings:
                p=cs+'\\Control\\CriticalDeviceDatabase\\'+device
                value(p,'Service',1,s);value(p,'ClassGUID',1,guid)
            for s,start,group,error in [('openhci',3,'Base',1),('usbhub',3,'Base',1),('HidUsb',2,'extended base',0),('kbdhid',1,'Keyboard Port',0),('mouhid',3,'Pointer Port',0)]:
                service(s,start,group,'system32\\drivers\\'+s.lower()+'.sys',error=error)
            for guid,filt in [('{4D36E96B-E325-11CE-BFC1-08002BE10318}','kbdclass'),('{4D36E96F-E325-11CE-BFC1-08002BE10318}','mouclass')]:
                value(cs+'\\Control\\Class\\'+guid,'UpperFilters',7,[filt])
            value(cs+'\\Services\\kbdhid\\Parameters','WorkNicely',4,0)
            for k in ['UseOnlyMice','TreatAbsoluteAsRelative','TreatAbsolutePointerAsAbsolute']:value(cs+'\\Services\\mouhid\\Parameters',k,4,0)
        # Replace only the original PC C volume identity and its exact aliases.
        mounted=node(h,'MountedDevices');old=None
        for v in h.node_values(mounted):
            if h.value_key(v)=='\\DosDevices\\C:':old=h.value_value(v)[1]
        assert old and len(old)==12
        for key,typ,b in [(h.value_key(v),*h.value_value(v)) for v in h.node_values(mounted)]:
            if b==old:value('MountedDevices',key,3,struct.pack('<IQ',0xaa55,5633024*512))
        # CD/PC drive mappings do not name the protected dashboard C partition.
        r['control_sets']=sets
    else:
        path='Microsoft\\Windows\\CurrentVersion'; n=node(h,path)
        old=h.value_string(h.node_get_value(n,'DevicePath'))
        value(path,'DevicePath',2,old+';C:\\XWN405\\Audio;C:\\XWN405\\Network;C:\\XWN405\\Video')
    h.commit(str(target));del h
    data,conversions=normalize(target.read_bytes());target.write_bytes(data)
    h=hivex.Hivex(str(target));after=snapshot(h);del h
    # No change outside explicitly requested values, including opaque DRM data.
    assert set(before)<=set(after)
    for key,val in after.items():
        if key.lower() in requested:assert val==requested[key.lower()],key
        else:assert before.get(key)==val,key
    changes={k:dict(before=before.get(k),after=v) for k,v in after.items() if before.get(k)!=v}
    r['hives'][name]=dict(original_sha256=sha(original),result_sha256=sha(target),changes=changes,normalization=conversions,
                          untouched_values_exact=True)
r['status']='provisioned-offline-not-boot-qualified'
(K/'provision002.json').write_text(json.dumps(r,indent=2)+'\n')
print('Explicit fresh hive changes', {k:len(v['changes']) for k,v in r['hives'].items()})
