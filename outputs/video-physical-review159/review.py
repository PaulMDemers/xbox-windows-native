"""Cold physical-hive display binding inventory; no edits, deployment or boot."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent;dest=k/'binding-review.json';assert not dest.exists();capture=json.loads((k/'capture.json').read_text());assert capture['passed']
art=k/'artifacts';r=dict(scope=__doc__,passed=False,physical_hives=True,physical_writes=False,launch_attempted=False,hives={},bindings=[])
def node(h,path):
    n=h.root()
    for p in path.split('\\'):
        n=h.node_get_child(n,p)
        if not n:return 0
    return n
def values(h,n):
    result={}
    if not n:return result
    for v in h.node_values(n):
        typ,data=h.value_value(v);name=h.value_key(v)
        result[name]=dict(type=typ,hex=data.hex(),decoded=int.from_bytes(data,'little') if typ==4 else data.decode('utf-16le').rstrip('\0') if typ in [1,2,7] else None)
    return result
for name in ['system','software']:
    p=art/('F/winnt/system32/config/'+name);data=p.read_bytes();row=next(v for v in capture['files'] if v['path'].endswith('/config/'+name));assert hashlib.sha256(data).hexdigest()==row['sha256']
    h=hivex.Hivex(str(p));seen=set();todo=[h.root()];count=0
    while todo:
        n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
        for v in h.node_values(n):h.value_key(v);h.value_value(v);count+=1
        todo.extend(h.node_children(n))
    a,b=struct.unpack_from('<II',data,4);checksum=0
    for at in range(0,508,4):checksum^=struct.unpack_from('<I',data,at)[0]
    if checksum==0xffffffff:checksum=0xfffffffe
    elif checksum==0:checksum=1
    assert a==b and checksum==struct.unpack_from('<I',data,508)[0]
    r['hives'][name]=dict(sha256=row['sha256'],keys=len(seen),values=count,sequences_equal=True,checksum_valid=True)
    if name!='system':continue
    selection=values(h,node(h,'Select'));r['select']=selection
    cs='ControlSet%03d'%selection['Current']['decoded'];assert selection['Default']['decoded']==selection['Current']['decoded']
    pci=node(h,cs+r'\Enum\PCI');gpu=[]
    for dev in h.node_children(pci):
        if not h.node_name(dev).startswith('VEN_10DE&DEV_02A0'):continue
        for inst in h.node_children(dev):gpu.append(dict(path=cs+'\\Enum\\PCI\\'+h.node_name(dev)+'\\'+h.node_name(inst),values=values(h,inst)))
    assert len(gpu)==1;g=gpu[0]['values'];assert g['Service']['decoded'].lower()=='xboxvnt5' and g['ConfigFlags']['decoded']==0
    r['gpu']=gpu[0];driver=g['Driver']['decoded'];r['driver_key']=values(h,node(h,cs+'\\Control\\Class\\'+driver))
    paths=[cs+'\\Control\\Class\\'+driver+r'\Settings',cs+r'\Services\XboxVnt5\Device0']
    for path in paths:
        v=values(h,node(h,path));assert 'InstalledDisplayDrivers' in v
        value=v['InstalledDisplayDrivers'];assert value['decoded'].lower()=='framebuf' and value['type'] in [1,7]
        r['bindings'].append(dict(path=path,name='InstalledDisplayDrivers',before=value,planned_token='xwnown',preserve_registry_type=True))
    r['service']=values(h,node(h,cs+r'\Services\XboxVnt5'))
    r['crash_control']=values(h,node(h,cs+r'\Control\CrashControl'))
    r['hid_service']=values(h,node(h,cs+r'\Services\HidServ'))
    r['video_geometry_configuration']=values(h,node(h,cs+r'\Services\XboxVnt5\Device0'))
r.update(passed=True,geometry_runtime_qualified=False,limits='Registry geometry/settings are configuration evidence, not runtime scanout. No policy changes or synthesized device installation. Binding proposal is not applied.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Fresh physical hives structurally valid; two typed framebuf bindings identified, proposal only')
