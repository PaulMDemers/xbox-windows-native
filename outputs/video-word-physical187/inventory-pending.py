"""Offline appended SetupAPI/device evidence; identifies logged installer leads, not live pending owner."""
import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='control001';base=k/case;art=base/'artifacts/physical'
dest=base/'pending-inventory.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
before=(art/'before-setupapi.log').read_bytes();after=(art/'after-setupapi.log').read_bytes()
assert after.startswith(before),'No append-only SetupAPI delta'
appended=after[len(before):];text=appended.decode('cp1252')
blocks=[v for v in re.split(r'(?=^\[\d{4}/)',text,flags=re.M) if v.startswith('[')]
def node(h,path):
    n=h.root()
    for part in path.split('\\'):
        children=[c for c in h.node_children(n) if h.node_name(c).casefold()==part.casefold()]
        assert len(children)<=1
        if not children:return None
        n=children[0]
    return n
def values(h,path):
    n=node(h,path)
    if n is None:return None
    result={}
    for v in h.node_values(n):
        typ,data=h.value_value(v)
        result[h.value_key(v)]=dict(type=typ,hex=data.hex(),decoded=int.from_bytes(data,'little') if typ==4 else data.decode('utf-16le').rstrip('\0') if typ in [1,2,7] else None)
    return result
systems={phase:hivex.Hivex(str(art/(phase+'-system'))) for phase in ['before','after']}
current=values(systems['after'],'Select')['Current']['decoded'];cs='ControlSet%03d'%current
devices=[]
for block in blocks:
    found=re.search(r'DevInstall ([^\r\n]+)',block)
    if not found:continue
    id=found[1];old=values(systems['before'],cs+'\\Enum\\'+id);new=values(systems['after'],cs+'\\Enum\\'+id)
    devices.append(dict(id=id,setupapi_block=block,metadata_before=old,metadata_after=new,metadata_unchanged=old==new,
        no_compatible_driver_logged='0xe0000228' in block.lower()))
result=dict(scope=__doc__,physical_capture=True,physical_access=False,source_sha256=sha(Path(__file__).read_bytes()),
    before_setupapi_sha256=sha(before),after_setupapi_sha256=sha(after),append_only=True,appended_bytes=len(appended),
    system_sha256={phase:sha((art/(phase+'-system')).read_bytes()) for phase in systems},
    appended_blocks=blocks,logged_client_installers=devices,
    actual_guard_status=258,actual_live_pending_device_owner_captured=False,
    limits='Two installer starts with no-compatible-driver result are leads. No live process/wizard ownership was captured. No disable/null-driver policy or service/event suppression applied.')
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(appended_bytes=len(appended),logged_devices=[dict(id=v['id'],unchanged=v['metadata_unchanged'],values=v['metadata_after']) for v in devices]),indent=2))
