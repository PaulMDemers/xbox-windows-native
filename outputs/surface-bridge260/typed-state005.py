"""Typed before/after device and policy state from preserved emulator SYSTEM only; no repair."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
case=sys.argv[1];assert case in ['emu005'];out=k/case;dest=out/'device-state.json';assert not dest.exists()
p={phase:{'system':dict(path=str((out/'artifacts'/(phase+'-system')).relative_to(ws)),sha256=sha((out/'artifacts'/(phase+'-system')).read_bytes()))} for phase in ['before','after']}
def snapshot(row):
    path=ws/row['path'];data=path.read_bytes();assert sha(data)==row['sha256']
    h=hivex.Hivex(str(path));keys=set();values={};todo=[('',h.root())]
    while todo:
        path,node=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(node):values[(path,h.value_key(v))]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(node))
    a,b=struct.unpack_from('<II',data,4);checksum=0
    for at in range(0,508,4):checksum ^= struct.unpack_from('<I',data,at)[0]
    checksum=0xfffffffe if checksum==0xffffffff else 1 if checksum==0 else checksum
    return keys,values,dict(sha256=sha(data),keys=len(keys),values=len(values),sequences_equal=a==b,checksum_valid=checksum==struct.unpack_from('<I',data,508)[0])
snap={phase:snapshot(p[phase]['system']) for phase in ['before','after']}
def render(value):
    if value is None:return None
    typ,data=value;r=dict(type=typ,hex=data.hex())
    if typ in [1,2,7] and not len(data)%2:
        try:r['strings']=data.decode('utf-16le').rstrip('\0').split('\0')
        except UnicodeError:r['decode_error']=True
    if typ==4 and len(data)==4:r['dword']=struct.unpack('<I',data)[0]
    return r
def subset(values,token):return {key:value for key,value in values.items() if token.lower() in key[0].lower()}
def pci(values):
    nodes={}
    for (path,name),value in values.items():
        parts=path.split('\\')
        if len(parts)==6 and parts[2:4]==['Enum','PCI']:
            nodes.setdefault(path,{})[name]=render(value)
    return nodes
before,after=[snap[v][1] for v in ['before','after']]
r=dict(scope=__doc__,physical_observation=False,emulator_observation=True,physical_qualified=False,snapshots={phase:v[2] for phase,v in snap.items()},devices={phase:pci(v[1]) for phase,v in snap.items()},policy=[])
for token in ['\\Control\\CrashControl','\\Services\\HidServ','\\Services\\xwnfatx','\\Services\\nvnet','\\Services\\xboxv','\\Services\\framebuf','\\Control\\Video']:
    a,b=subset(before,token),subset(after,token)
    r['policy'].append(dict(subtree=token,values_before=len(a),values_after=len(b),unchanged=a==b))
r['actual_component_services']=[]
for (path,name),value in before.items():
    decoded=render(value)
    if name.lower()=='imagepath' and '\\Services\\' in path and any(text.lower().endswith(('xwnfatx.sys','nvnetnt5.sys','xboxvnt5.sys','hidserv.exe')) for text in decoded.get('strings',[])):
        a={key:v for key,v in before.items() if key[0]==path or key[0].startswith(path+'\\')}
        b={key:v for key,v in after.items() if key[0]==path or key[0].startswith(path+'\\')}
        row=dict(subtree=path,image_path=decoded,values_before=len(a),values_after=len(b),unchanged=a==b)
        r['actual_component_services'].append(row)
interesting=lambda key:('\\Enum\\PCI\\' in key[0] or '\\Enum\\USB\\' in key[0]) or any(token.lower() in key[0].lower() for token in ['\\Control\\Video','\\Services\\xboxv','\\Services\\framebuf'])
r['device_binding_delta']=[dict(path=key[0],name=key[1],before=render(before.get(key)),after=render(after.get(key))) for key in sorted(set(before)|set(after)) if interesting(key) and before.get(key)!=after.get(key)]
r['hive_headers_valid']=all(v[2]['sequences_equal'] and v[2]['checksum_valid'] for v in snap.values())
r['selected_policy_unchanged']=all(v['unchanged'] for v in r['policy']+r['actual_component_services'])
r['new_device_disable_flags']=[dict(path=key[0],before=render(before.get(key)),after=render(after.get(key))) for key in sorted(set(before)|set(after)) if '\\Enum\\' in key[0] and key[1].lower()=='configflags' and render(after.get(key)) and render(after.get(key)).get('dword',0)&1 and not (render(before.get(key)) or {}).get('dword',0)&1]
r['no_new_device_disabling']=not r['new_device_disable_flags']
def service_values(values):
    return {path:{name.lower():render(value) for (p,name),value in values.items() if p==path}
            for path,name in values if path.lower().endswith('\\services\\xwnpattern258')}
r['arena_service_before']=service_values(before);r['arena_service_after']=service_values(after)
r['arena_service_valid']=not r['arena_service_before'] and bool(r['arena_service_after']) and all(
    v.get('start',{}).get('dword')==3 and v.get('type',{}).get('dword')==1 and
    v.get('imagepath',{}).get('strings')==['\\??\\C:\\xwnpat258\\pattern.sys']
    for v in r['arena_service_after'].values())
r['limits']='Typed persistent metadata after targeted guest Cancel actions; not live ownership, functional hardware support or full-file qualification. Natural PnP changes retained and never overwritten.'
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(hive_headers_valid=r['hive_headers_valid'],selected_policy_unchanged=r['selected_policy_unchanged'],device_binding_delta=len(r['device_binding_delta']))))
