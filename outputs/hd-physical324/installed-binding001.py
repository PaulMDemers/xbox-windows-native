"""Read actual persisted PnP/service/class values after genuine installation."""
import hashlib,json,pathlib,struct,sys
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=pathlib.Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['physical001']
out=k/case;dest=out/'installed-binding.json';assert not dest.exists()
h=hivex.Hivex(str(k/'artifacts'/case/'F/winnt/system32/config/system'))
def node(path):
    n=h.root()
    for part in path.split('\\'):
        matches=[c for c in h.node_children(n) if h.node_name(c).lower()==part.lower()]
        assert len(matches)==1,('Missing/duplicate node',path,part)
        n=matches[0]
    return n
def values(path):
    result={}
    for v in h.node_values(node(path)):
        typ,data=h.value_value(v);name=h.value_key(v).lower()
        if typ in [1,2,7]:result[name]=data.decode('utf-16le').rstrip('\0').split('\0')
        elif typ==4:
            assert len(data)==4;result[name]=struct.unpack('<I',data)[0]
        else:result[name]=dict(type=typ,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    return result
r=dict(passed=False,physical_qualified=False,offline_registry_edits=False)
try:
    current=values('Select')['current'];assert isinstance(current,int) and 1<=current<=999
    prefix='ControlSet%03d'%current
    state=json.loads((out/'device-state.json').read_text())
    hardware='pci\\ven_10de&dev_01b1&subsys_00000000&rev_b1'
    matches=[p for p,v in state['devices']['after'].items() if p.lower().startswith('\\'+prefix.lower()+'\\enum\\pci\\') and hardware in [s.lower() for s in v.get('HardwareID',{}).get('strings',[])]]
    assert len(matches)==1,('Target count',matches)
    target=matches[0].lstrip('\\');dev=values(target)
    service=values(prefix+'\\Services\\xwnaci207')
    assert len(dev['driver'])==1
    driver=values(prefix+'\\Control\\Class\\'+dev['driver'][0])
    r.update(current_control_set=current,instance=target,device=dev,service=service,driver_class=driver)
    assert dev['service']==['xwnaci207'] and not dev.get('configflags',0)&1
    assert service['start']==3 and service['type']==1 and service['errorcontrol']==1
    assert len(service['imagepath'])==1 and service['imagepath'][0].lower().endswith('\\xwnaci207.sys')
    assert len(driver['infsection'])==1 and driver['infsection'][0].lower() in ['audio','audio.nt']
    assert len(driver['infpath'])==1 and driver['infpath'][0].lower().endswith('.inf')
    # No unrelated PCI/USB service rebinding is allowed as part of this package.
    bad=[v for v in state['device_binding_delta'] if v['name'].lower()=='service' and 'ven_10de&dev_01b1' not in v['path'].lower()]
    assert not bad,('Unrelated service changes',bad)
    r['passed']=True
except Exception as exc:r['error']=repr(exc)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','error'] if n in r}))
