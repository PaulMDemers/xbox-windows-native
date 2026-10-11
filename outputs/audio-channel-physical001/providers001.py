"""Read actual physical NT5 providers; validate helper hashes and native driver exports."""
import hashlib,importlib.util,json,pathlib,sys
sys.dont_write_bytecode=True
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
canonical=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,str(canonical/'work/python-packages'));import pefile
assert json.loads((canonical/'outputs/device-hardware220/state/audio-channel001-claimed.json').read_text())['owner']=='audio-channel001'
assert not (canonical/'outputs/device-hardware220/state/audio-channel001-closed.json').exists()
before=json.loads((k/'capture002.json').read_text());assert before['passed']
dest=k/'providers001.json';art=k/'artifacts/providers001';assert not dest.exists() and not art.exists();art.mkdir()
spec=importlib.util.spec_from_file_location('ftp220',repo/'outputs/fatx0098-soak3/physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
required={}
def walk(v):
    if isinstance(v,dict):
        if 'module' in v and 'sha256' in v:
            name=v['module'].lower();assert name not in required or required[name]==v['sha256'];required[name]=v['sha256']
        for a in v.values():walk(a)
    elif isinstance(v,list):
        for a in v:walk(a)
for n in ['install-review002.json','state-review001.json','hardware-runner-review001.json']:walk(json.loads((repo/'outputs/audio207'/n).read_text()))
driver=json.loads((repo/'outputs/audio207/build-review004.json').read_text())['binaries'][0]
for v in driver['imports']:
    if v['library'].lower()!='hal.dll':required[v['library'].lower()]=v['provider_sha256']
required['hal.dll']=before['files']['/E/Applications/XWNFBoot/loader/halxboxnt5.dll']['sha256']
r=dict(passed=False,physical_access=True,physical_writes=False,launch_requested=False,files={},native_exports={},hal_note='Actual active Xbox HAL bytes/export table, not the Microsoft HAL used by the earlier import-only review.')
try:
    with m.connect() as f:
        m.owner(f)
        for name,digest in required.items():
            path='/E/Applications/XWNFBoot/loader/halxboxnt5.dll' if name=='hal.dll' else '/F/winnt/system32/'+('drivers/' if name.endswith('.sys') else '')+name
            data=m.get(f,path);(art/name).write_bytes(data);actual=hashlib.sha256(data).hexdigest()
            assert m.get(f,path)==data,'Provider changed during read'
            r['files'][name]=dict(remote=path,sha256=actual,expected=digest,bytes=len(data),matched=actual==digest)
            assert actual==digest,'Provider hash mismatch: '+name
    for imports in driver['imports']:
        name=imports['library'].lower();pe=pefile.PE(str(art/name));exports={s.name.decode():s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
        missing=[n for n in imports['names'] if n not in exports or not exports[n].address]
        r['native_exports'][name]=dict(required=imports['names'],missing=missing,forwarders={n:exports[n].forwarder.decode() for n in imports['names'] if n in exports and exports[n].forwarder})
        assert not missing,'Missing actual physical driver import'
    r['passed']=True
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=r['passed'],physical_providers=len(r['files']),native_provider_tables=len(r['native_exports']))))
