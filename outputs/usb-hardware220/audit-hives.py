"""Read-only full hive walks and typed SYSTEM deltas from captured physical USB220 bytes."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
K=Path(__file__).resolve().parent
phase=sys.argv[1];assert phase in ['before','after']
dest=K/(phase+'-hive-audit.json');assert not dest.exists()
r=json.loads((K/'physical001.json').read_text())
result=dict(phase=phase,physical_evidence=True,hives=[],passed=False)
sha=lambda b:hashlib.sha256(b).hexdigest()

def walk(path):
    h=hivex.Hivex(str(path));todo=[('',h.root())];keys=set();values={}
    while todo:
        path,n=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(n):values[(path,h.value_key(v))]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values

for name in ['system','software','default','sam','security']:
    row=r[phase][name];p=K/row['file'];b=p.read_bytes();assert sha(b)==row['sha256']
    keys,values=walk(p);a,c=struct.unpack_from('<II',b,4);check=0
    for at in range(0,508,4):check ^= struct.unpack_from('<I',b,at)[0]
    check=0xfffffffe if check==0xffffffff else 1 if check==0 else check
    result['hives'].append(dict(name=name,keys=len(keys),values=len(values),sha256=sha(b),
        parsed=True,sequences_equal=a==c,checksum_valid=check==struct.unpack_from('<I',b,508)[0]))
    if name=='system':
        result['select']={key[1]:dict(type=t,hex=data.hex()) for key,(t,data) in values.items() if key[0].lower()=='\\select'}
        result['usb_service_and_enum']=[dict(path=key[0],name=key[1],type=t,hex=data.hex()) for key,(t,data) in sorted(values.items())
            if '\\enum\\usb' in key[0].lower() or any('\\services\\'+s in key[0].lower() for s in ['openhci','usbhub','usbd','hidusb','hidclass','hidparse','kbdhid','mouhid'])]
        if phase=='after':
            oldkeys,old=walk(K/r['before']['system']['file'])
            result['system_delta']=dict(added_keys=sorted(keys-oldkeys),removed_keys=sorted(oldkeys-keys),
                changed_values=[dict(path=key[0],name=key[1],before=None if key not in old else [old[key][0],old[key][1].hex()],
                    after=None if key not in values else [values[key][0],values[key][1].hex()])
                    for key in sorted(set(old)|set(values)) if old.get(key)!=values.get(key)])
result['passed']=all(v['parsed'] and v['sequences_equal'] and v['checksum_valid'] for v in result['hives'])
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(phase=phase,passed=result['passed'],hives=len(result['hives']))))
