"""Five captured before/after physical hives; typed bindings and unchanged device/service/dump policy."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
base=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];k=base/case
dest=k/'physical-hive-audit.json';assert not dest.exists();art=k/'artifacts/physical'
read=lambda p:json.loads(p.read_text());r=read(k/'physical.json');assert r.get('collected_utc')
result=dict(scope=__doc__,physical_result=True,physical_qualified=False,hives=[],bindings=[],policy=[])
def semantic(h):
    keys=set();values={};todo=[('',h.root())]
    while todo:
        path,n=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(n):values[(path,h.value_key(v))]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values
snapshots={}
for name in ['system','software','default','sam','security']:
    for phase in ['before','after']:
        p=art/(phase+'-'+name);data=p.read_bytes();h=hivex.Hivex(str(p));keys,values=semantic(h)
        a,b=struct.unpack_from('<II',data,4);checksum=0
        for at in range(0,508,4):checksum ^= struct.unpack_from('<I',data,at)[0]
        checksum=0xfffffffe if checksum==0xffffffff else 1 if checksum==0 else checksum
        result['hives'].append(dict(name=name,phase=phase,keys=len(keys),values=len(values),parsed=True,
            sha256=hashlib.sha256(data).hexdigest(),sequences_equal=a==b,checksum_valid=checksum==struct.unpack_from('<I',data,508)[0]))
        if name=='system':snapshots[phase]=(keys,values)
before,after=snapshots['before'][1],snapshots['after'][1]
for change in read(base/'binding-edit.json')['changes']:
    key=('\\'+change['path'],change['name']);bt,bb=before[key];at,ab=after[key]
    result['bindings'].append(dict(path=key[0],type=at,hex=ab.hex(),matched=bt==at==change['type'] and bb.hex()==change['before_hex'] and ab.hex()==change['after_hex']))
def subset(values,token):return {key:value for key,value in values.items() if token.lower() in key[0].lower()}
for token in ['\\Control\\CrashControl','\\Services\\HidServ','\\Services\\xwnfatx','\\Services\\nvnet','\\Enum\\PCI']:
    old,new=subset(before,token),subset(after,token)
    result['policy'].append(dict(subtree=token,values_before=len(old),values_after=len(new),unchanged=old==new))
result['system_semantic_delta']=dict(added_keys=sorted(snapshots['after'][0]-snapshots['before'][0]),
    removed_keys=sorted(snapshots['before'][0]-snapshots['after'][0]),
    changed_values=[dict(path=key[0],name=key[1],before=None if key not in before else [before[key][0],before[key][1].hex()],
        after=None if key not in after else [after[key][0],after[key][1].hex()]) for key in sorted(set(before)|set(after)) if before.get(key)!=after.get(key)])
result['passed']=all(v['parsed'] and v['sequences_equal'] and v['checksum_valid'] for v in result['hives']) and all(v['matched'] for v in result['bindings']) and all(v['unchanged'] for v in result['policy'])
result['limits']='Ten preserved hive snapshots, not a complete physical allocation/all-file audit. Runtime SYSTEM differences retained explicitly.'
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=result['passed'],hives=len(result['hives']),bindings=result['bindings'],policy=result['policy']),indent=2))
