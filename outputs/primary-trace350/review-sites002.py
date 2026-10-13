"""Pin existing348 binary callsites and exact kernel layout inputs; no runtime claim."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'sites002.json';assert not dest.exists()
sys.path.insert(0,str(W/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
old=read(K.parent/'video-row-copy-trace/sites.json')
paths={'ntoskrnl.exe':Path(old['modules']['ntoskrnl.exe']['path']),'replay.exe':Path('E:/xwn348/probe/build001/replay.exe'),'xwnown.dll':Path('E:/xwn348/build001/candidate001/xwnown.dll')}
assert sha(paths['ntoskrnl.exe'])==old['modules']['ntoskrnl.exe']['sha256']
assert sha(paths['replay.exe'])==read(K.parent/'primary-copy348/probe/build001.json')['binary_sha256']
assert sha(paths['xwnown.dll'])==read(K.parent/'primary-copy348/build001.json')['cases']['candidate001']['sha256']
mods={};pes={}
for name,path in paths.items():
    p=pes[name]=pefile.PE(str(path));mods[name]=dict(path=str(path),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage)
for name in ['win32k.sys','gdi32.dll']:
    path=Path(old['modules'][name]['path']);assert sha(path)==old['modules'][name]['sha256']
    p=pes[name]=pefile.PE(str(path));mods[name]=dict(path=str(path),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
sites={'interval':('replay.exe',0x5290),'operation':('replay.exe',0x5439),'bitblt_return':('replay.exe',0x543f),'flush_return':('replay.exe',0x54a6),'primary':('xwnown.dll',0x4550),'primary_return':('xwnown.dll',0x327d),'owner_dst_return':('xwnown.dll',0x459e),'owner_src_return':('xwnown.dll',0x45ad),'copy':('xwnown.dll',0x31d0)}
rows={}
for label,(name,rva) in sites.items():
    code=pes[name].get_data(rva,32);ins=list(md.disasm(code,mods[name]['preferred_base']+rva))
    assert ins and sum(i.size for i in ins)>15
    rows[label]=dict(module=name,rva=rva,raw=code.hex(),instructions=[dict(address=i.address,mnemonic=i.mnemonic,operands=i.op_str,size=i.size) for i in ins])
assert rows['interval']['instructions'][0]['mnemonic']=='call' and rows['operation']['instructions'][0]['mnemonic']=='call'
assert rows['primary']['raw'].startswith('5589e5') and rows['primary_return']['raw'].startswith('8945dc')
pub=read(K.parent/'native-windows-nt5-kernel/kernel-publics.json')
dependencies={p.relative_to(W).as_posix():sha(p) for p in [Path(__file__),K/'create-kit.py',K.parent/'video-row-copy-trace/sites.json',K.parent/'video-row-copy-trace/layouts.json',K.parent/'native-windows-nt5-kernel/kernel-publics.json',K.parent/'native-windows-nt5-kernel/trace-entry.py',K.parent/'native-windows-prebuild/monitor_capture.py',K.parent/'surface-bridge260/atomic_json.py',K.parent/'video-cursor-scanout/discover_kernel.py']}
r=dict(modules=mods,sites=rows,module_list_rva=old['module_list_rva'],thread_owner_offset=old['thread_owner_offset'],dependencies=dependencies,scope='Static instruction leads; live module identity, relocated instructions, thread/frame pairing and full teardown still required.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('350 static callsites/binaries pinned, no guest mutation')
