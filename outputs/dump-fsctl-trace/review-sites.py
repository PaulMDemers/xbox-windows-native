"""Pin exact dump-initialization sites and candidate HAL/FATX identities."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=read(k.parent/'dump-config-trace/sites-v4.json');usage=read(k.parent/'dump-usage-trace/sites.json')
names=['configure_entry','configure_handle_return','dump_stack_return','complete_call','caller_status','caller_error','stack_entry','stack_usage_call','stack_usage_return','stack_final_return','entry','handle_return','query_call','query_return','query_pending_return','fsctl_call','fsctl_return','fsctl_pending_return','return']
r=dict(prior);r['scope']=__doc__;r['sites']=[v for v in prior['sites'] if v['name'] in names];assert len(r['sites'])==len(names)
r['loaded_module_list_rva']=usage['loaded_module_list_rva']
paths={'ntoskrnl.exe':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe'),'xwnfatx.sys':k.parent/'fatx-directory-order/artifacts/xwnfatx.sys','hal.dll':k/'artifacts/hal-candidate001.dll'}
mods={}
for name,path in paths.items():
    p=pefile.PE(str(path));mods[name]=dict(path=str(path.resolve()),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage)
assert mods['ntoskrnl.exe']['sha256']==prior['kernel_sha256']
assert mods['hal.dll']['sha256']==read(k/'hal-review.json')['candidate001']['sha256']
assert mods['xwnfatx.sys']['sha256']=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
r['fatx_entry_rva']=0xfc90
r['hal_functions']=read(k/'hal-review.json')['candidate001']['resident_functions']
r['dependencies'].update({n:sha(k.parent/n) for n in ['dump-config-trace/sites-v4.json','dump-usage-trace/sites.json','fatx-directory-order/fatx-layouts.json']})
for name,data in [('sites.json',r),('modules.json',mods)]:
    path=k/name;assert not path.exists();path.write_text(json.dumps(data,indent=2)+'\n')
print('Pinned19 kernel boundaries plus exact HAL/FATX identities')
