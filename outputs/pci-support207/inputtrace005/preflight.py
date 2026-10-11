"""Pin a read-only debugger plan against actual NT5 images and historical PDB layouts."""
import ast,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[2]
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
providers={'ntoskrnl.exe':(k.parent/'artifacts/providers001/ntoskrnl.exe','84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'),
 'kbdclass.sys':(k.parent/'rebalance002/artifacts/providers001/kbdclass.sys','477d54c98c12e53ab0b43ede5cf3e8699f35efe256af3f1e825ed9439abaeb14'),
 'mouclass.sys':(k.parent/'rebalance002/artifacts/providers001/mouclass.sys','9c7917f95e1ddc615a4bd3781a65dcec94b65f729a7d882c15040d9ca92ec404')}
rows={}
for name,(p,digest) in providers.items():
    assert sha(p)==digest
    pe=pefile.PE(str(p));rows[name]=dict(path=str(p),sha256=digest,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage,preferred_base=pe.OPTIONAL_HEADER.ImageBase)
pub=read(repo/'outputs/native-windows-nt5-kernel/kernel-publics.json')
layouts=read(repo/'outputs/video-transfer-observed/layouts.json')
assert pub['pdb_sha256']==layouts['pdb_sha256']=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
L=layouts['structures'];L.update(read(repo/'outputs/native-windows-fatx-runtime/fatx-native-layouts.json'))
assert L['_FILE_OBJECT']['fields']['ReadAccess']['offset']==0x26
pe=pefile.PE(str(providers['ntoskrnl.exe'][0]));exports={v.name.decode():v.address for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
sites={'open_enter':0xa0078,'open_after_zw':0xa00b2,'open_end':0xa00ee,'share_enter':0x9f030,'share_failure':0x9f0f5,'share_end':0x9f137,'call_driver':0x1ddf4}
assert exports['IoGetDeviceObjectPointer']==sites['open_enter']==pub['symbols']['_IoGetDeviceObjectPointer@16']['rva']
assert exports['IoCheckShareAccess']==sites['share_enter'] and exports['IofCallDriver']==sites['call_driver']
assert pe.get_data(sites['share_failure'],5)==bytes.fromhex('b8430000c0')
assert pe.get_data(sites['open_after_zw'],2)==bytes.fromhex('8bf8') and pe.get_data(sites['open_end'],2)==bytes.fromhex('8bc7')
observed={v['name'].lower():v['base'] for v in read(k.parent/'inputtrace004/veto001/module-observation001.json')['rows']}
assert observed['kbdclass.sys']==0xf8f38000 and observed['mouclass.sys']==0xf8f50000
class_sites={'kbd_enable_enter':0xf8f38f46,'kbd_enable_end':0xf8f3910d,'mou_enable_enter':0xf8f50e6e,'mou_enable_end':0xf8f50fcf}
dependencies=[k.parent/'inputtrace004/veto001/module-observation001.json',k.parent/'inputtrace004/veto001/run.json',k.parent/'inputtrace004/veto001/trace.json',k.parent/'inputtrace004/veto001/pnp-review.json',k.parent/'inputtrace003/veto001/address-check002.json',repo/'outputs/native-windows-nt5-kernel/kernel-publics.json',repo/'outputs/video-transfer-observed/layouts.json',repo/'outputs/native-windows-fatx-runtime/fatx-native-layouts.json',repo/'outputs/shutdown-popup-workload/site-review.json',k.parent/'rebalance002/veto001/fixture.json',k.parent/'rebalance002/build001.json']
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
r=dict(passed=True,scope=__doc__,physical_access=False,ordinary_qualified=False,kernel_base_expected=0x82402000,module_list_rva=pub['symbols']['_PsLoadedModuleList']['rva'],thread_owner_offset=read(repo/'outputs/shutdown-popup-workload/site-review.json')['thread_owner_offset'],providers=rows,sites=sites,class_sites=class_sites,layouts=L,dependencies={str(p):sha(p) for p in dependencies},sources={p.name:sha(p) for p in k.iterdir() if p.is_file() and p.suffix in ('.py','.ps1','.inf')},limits='Expected kernel base is an arm address, not evidence. Every interpreted hit requires loaded headers and relocated site-byte verification. Read-only observations, bounded 240s/4096 stops; no code/data/register mutation. Owner attribution requires actual retained references, not names alone.')
assert read(k.parent/'inputtrace003/veto001/address-check002.json')['inferred_base']==0x82402000
assert read(k.parent/'inputtrace004/veto001/run.json')['closed']
assert read(k.parent/'inputtrace004/veto001/pnp-review.json')['qualified_resource_only_installation']
dest=k/'preflight001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Pinned debugger preflight passed; no guest launch')
