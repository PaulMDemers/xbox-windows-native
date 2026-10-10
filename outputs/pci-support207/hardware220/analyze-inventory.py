"""Parse a complete PCI220 OS inventory. Resource metadata is not codec function proof."""
import argparse,hashlib,json
from pathlib import Path
def analyze(data):
    text=data.decode('ascii');lines=text.replace('\r\n','\n').splitlines()
    assert lines[0]=='XWN_PCI_INVENTORY220 version=1' and lines[-1]=='COMPLETE220'
    assert lines[-3:-1]==['NO_PCI_SMBUS_AC97_WRITES','NO_INSTALL_OR_DIALOG_ACTION']
    assert not any('bound_reached=' in line for line in lines)
    devices=[];device=prop=config=group=resource=None;end=None;count=None
    handle_results=[]
    for line in lines[1:-3]:
        key,value=line.split('=',1)
        if key=='device_index':
            device=dict(index=int(value),properties=[],configurations=[]);devices.append(device)
            prop=config=group=resource=None
        elif key=='device_id':device[key]=value
        elif key=='property':
            prop=dict(property=int(value));device['properties'].append(prop);resource=None
        elif key=='configuration_type':
            config=dict(type=int(value),groups=[]);device['configurations'].append(config);prop=resource=group=None
        elif key=='configuration_index':
            group=dict(index=int(value),resources=[],next_resource_results=[]);config['groups'].append(group);resource=None
        elif key=='resource_index':
            resource=dict(index=int(value));group['resources'].append(resource)
        elif key=='hex':
            raw=bytes.fromhex(value);target=prop if prop is not None else resource;assert target is not None
            target['hex']=value
            if prop is not None:
                assert len(raw)==prop['property_bytes']
                if prop['property_type'] in (1,2,7):prop['strings']=raw.decode('cp1252').rstrip('\0').split('\0')
                elif prop['property_type']==4 and len(raw)==4:prop['dword']=int.from_bytes(raw,'little')
            else:assert len(raw)==resource['resource_size']
        elif key in ('enumeration_end_error','devices'):
            if key=='enumeration_end_error':end=int(value)
            else:count=int(value)
        elif key.startswith('free_'):handle_results.append(int(value))
        elif key=='next_resource_result':group['next_resource_results'].append(int(value))
        elif key in ('first_configuration_result','next_configuration_result'):config.setdefault(key,[]).append(int(value))
        elif key.startswith('resource_'):resource[key]=int(value)
        elif key.startswith('property_'):prop[key]=int(value)
        else:device[key]=int(value)
    assert end==259 and count==len(devices) and 0<count<256 and [d['index'] for d in devices]==list(range(count))
    assert all(v==0 for v in handle_results)
    assert all(d['device_id_result']==0 and d['status_result']==0 and d['device_id'].upper().startswith('PCI\\') for d in devices)
    assert len({d['device_id'] for d in devices})==len(devices)
    unavailable=[]
    for d in devices:
        assert [p['property'] for p in d['properties']]==[0,1,2,8,4,9,10,13,21,28]
        assert all('property_error' in p or 'hex' in p for p in d['properties'])
        assert [c['type'] for c in d['configurations']]==[2,3]
        for c in d['configurations']:
            assert c['first_configuration_result'] in ([0],[14])
            assert c.get('next_configuration_result',[])==([0]*(len(c['groups'])-1)+[14] if c['groups'] else [])
            for g in c['groups']:
                assert g['next_resource_results']==[0]*len(g['resources'])+[15]
                assert [r['index'] for r in g['resources']]==list(range(len(g['resources'])))
                for r in g['resources']:
                    assert 'resource_size_result' in r and 'resource_size' in r
                    if r['resource_size_result']==0 and 0<r['resource_size']<=4096:
                        assert 'resource_data_result' in r
                        if r['resource_data_result']==0:assert 'hex' in r
                    if not (r['resource_size_result']==0 and 0<r['resource_size']<=4096 and r.get('resource_data_result')==0 and 'hex' in r):
                        unavailable.append(dict(device=d['device_id'],configuration_type=c['type'],group=g['index'],resource=r))
    assert len(handle_results)==sum(1+len(g['resources']) for d in devices for c in d['configurations'] for g in c['groups'])
    return dict(scope=__doc__,completed=True,sha256=hashlib.sha256(data).hexdigest(),device_count=count,devices=devices,
                all_resource_payloads_available=not unavailable,unavailable_resource_payloads=unavailable,
                pci_targets=[d for d in devices if any(v in d['device_id'].upper() for v in ('DEV_01B4','DEV_01C1','DEV_01B1'))],
                physical_function_qualified=False,resource_source='Windows configuration manager, not direct register/codec reads')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();r=analyze(args.input.read_bytes());args.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(completed=r['completed'],device_count=r['device_count'],targets=[d['device_id'] for d in r['pci_targets']]),indent=2))
