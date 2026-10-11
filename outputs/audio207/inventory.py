"""Read-only pinned physical IDs and actual owned NT5 fixture audio providers."""
import hashlib,importlib,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path[:0]=[str(repo/'outputs/video-text-oracle206'),str(repo/'outputs/fatx-mapped-eof')]
from common import ColdIO,readers,hive
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
sha=lambda b:hashlib.sha256(b).hexdigest()
f=json.loads((repo/'outputs/setup-wizard-automation201/fixture-observe002.json').read_text());base=pathlib.Path(f['fixture_path_linux'])
assert sha(base.read_bytes())==f['fixture_sha256']
out=k/'artifacts/inventory001';out.mkdir(parents=True,exist_ok=False)
r={'fixture':str(base),'fixture_sha256':f['fixture_sha256'],'physical_access':False,'providers':{},'services':{}}
with ColdIO(base) as io:
    rr=readers(io,base)
    for name in ['portcls.sys','ks.sys','sysaudio.sys','kmixer.sys','wdmaud.sys','ac97xnt5.sys']:
        data=rr['F'].read('winnt/system32/drivers/'+name);(out/name).write_bytes(data);r['providers'][name]=sha(data)
    for name in ['ntoskrnl.exe','hal.dll','kernel32.dll','user32.dll','advapi32.dll','winmm.dll','setupapi.dll']:
        data=rr['F'].read('winnt/system32/'+name);(out/name).write_bytes(data);r['providers'][name]=sha(data)
    data=rr['F'].read('winnt/system32/config/system');(out/'system').write_bytes(data)
    r['system']=hive(out/'system')
h=hivex.Hivex(str(out/'system'))
for control in ['ControlSet001','ControlSet002']:
    for service in ['ac97xnt5','sysaudio','kmixer','wdmaud']:
        n=h.root()
        for part in [control,'Services',service]:
            n=h.node_get_child(n,part)
            if not n:break
        if not n:continue
        r['services'][control+'/'+service]={h.value_key(v):{'type':h.value_value(v)[0],'hex':h.value_value(v)[1].hex()} for v in h.node_values(n)}
physical=repo/'outputs/device-durability189/physical-device-state.json';p=json.loads(physical.read_text())
r['physical_evidence_sha256']=sha(physical.read_bytes())
def walk(obj,path=''):
    if isinstance(obj,dict):
        for key,value in obj.items():
            if '\\Enum\\PCI\\' in key and any('DEV_'+id in key for id in ['01B0','01B1']):
                yield {'snapshot':path,'instance':key,'values':value}
            else:yield from walk(value,path+'/'+key)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from walk(v,path+'/'+str(i))
r['physical_audio_ids']=list(walk(p))
(k/'inventory001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['providers','services']},indent=2))
