"""Cold structural hive and actual incoming audio binding audit, no registry writes."""
import hashlib,json,pathlib,struct,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=pathlib.Path(__file__).resolve().parent;record=json.loads((k/'capture001.json').read_text())
assert record['passed'] and not record['physical_writes']
art=k/'artifacts/before001';dest=k/'before-audit001.json';assert not dest.exists()
def lookup(remote):
    found=[p for p in record['files'] if p.lower()==remote.lower()];assert found
    p=art/found[0].lstrip('/');assert hashlib.sha256(p.read_bytes()).hexdigest()==record['files'][found[0]]['sha256'];return p
def audit(name):
    p=lookup('/F/winnt/system32/config/'+name);data=p.read_bytes();h=hivex.Hivex(str(p))
    todo=[('',h.root())];seen=set();values={}
    while todo:
        path,n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
        for v in h.node_values(n):values[(path,h.value_key(v))]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    a,b=struct.unpack_from('<II',data,4);c=0
    for at in range(0,508,4):c ^= struct.unpack_from('<I',data,at)[0]
    c=0xfffffffe if c==0xffffffff else 1 if c==0 else c
    assert a==b and c==struct.unpack_from('<I',data,508)[0],name
    return dict(sha256=hashlib.sha256(data).hexdigest(),keys=len(seen),values=len(values),sequences_equal=True,checksum_valid=True),values
results={};system=None
for name in ['system','software','default','sam','security']:
    results[name],values=audit(name)
    if name=='system':system=values
def render(v):
    typ,data=v
    if typ in [1,2,7]:return data.decode('utf-16le').rstrip('\0').split('\0')
    if typ==4 and len(data)==4:return struct.unpack('<I',data)[0]
    return dict(type=typ,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def values(path):return {n.lower():render(v) for (p,n),v in system.items() if p.lower()==path.lower()}
current=values('\\Select')['current'];prefix='\\ControlSet%03d'%current
devices={}
for (path,name),v in system.items():
    if path.lower().startswith(prefix.lower()+'\\enum\\pci\\') and len(path.split('\\'))==6 and any(s in path.lower() for s in ['ven_10de&dev_01b1','ven_10de&dev_01b0']):devices.setdefault(path,{})[name.lower()]=render(v)
audio=[(p,v) for p,v in devices.items() if 'ven_10de&dev_01b1' in p.lower()];assert len(audio)==1
path,device=audio[0]
r=dict(passed=True,physical_snapshot=True,hives=results,current_control_set=current,devices=devices,aci_instance=path,aci_device=device,aci_service=None,aci_class=None,offline_registry_edits=False)
if device.get('service'):r['aci_service']=values(prefix+'\\Services\\'+device['service'][0])
if device.get('driver'):r['aci_class']=values(prefix+'\\Control\\Class\\'+device['driver'][0])
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','current_control_set','aci_device','aci_service','aci_class']},indent=2))
