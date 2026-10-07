"""Pin owned NT5 modules and actual GDI syscall stubs; static sites are leads."""
import hashlib,json,sys,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
mods={};pes={}
for name in ['ntoskrnl.exe','gdi32.dll','win32k.sys','framebuf.dll','probe.exe']:
 path=k/'artifacts/probe.exe' if name=='probe.exe' else system/name;p=pefile.PE(str(path));pes[name]=p
 mods[name]=dict(path=str(path.resolve()),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage,exports={x.name.decode():x.address for x in p.DIRECTORY_ENTRY_EXPORT.symbols if x.name} if hasattr(p,'DIRECTORY_ENTRY_EXPORT') else {})
assert mods['gdi32.dll']['sha256']=='4525e25c187364c82be9f1885b1edc9c6f0465fe326e5087b167257f9e75b46f'
assert mods['win32k.sys']['sha256']=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
assert mods['framebuf.dll']['sha256']=='5da1fe7c3cdaf67a4a487c8872c2034fbc425bfd36d2b7715b2a1c4caa51df86'
p=pes['gdi32.dll'];stubs={}
for name,rva,number,args in [('NtGdiBitBlt',0x3211c,0x100d,11),('NtGdiFlush',0x32774,0x1093,0)]:
 raw=p.get_data(rva,14 if args else 12);assert raw[:1]==b'\xb8' and struct.unpack_from('<I',raw,1)[0]==number and raw[5:11]==bytes.fromhex('8d542404cd2e')
 assert raw[11:]==(b'\xc2'+struct.pack('<H',args*4) if args else b'\xc3')
 stubs[name]=dict(rva=rva,service_number=number,argument_count=args,raw=raw.hex())
pub=read(ws/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols'];dump=read(ws/'outputs/dump-map-trace/sites.json')
r=dict(scope=__doc__,modules=mods,stubs=stubs,kernel_base_expected=dump['kernel_base_expected'],module_list_rva=pub['_PsLoadedModuleList']['rva'],service_shadow_rva=pub['_KeServiceDescriptorTableShadow']['rva'],thread_owner_offset=read(ws/'outputs/shutdown-popup-workload/site-review.json')['thread_owner_offset'],surfobj_x86_offsets=dict(sizlBitmap=16,cjBits=24,pvBits=28,pvScan0=32,lDelta=36,iBitmapFormat=44,iType=48,fjBitmap=50),dependencies={str(p.relative_to(ws)):sha(p) for p in [ws/'outputs/native-windows-nt5-kernel/kernel-publics.json',ws/'outputs/shutdown-popup-workload/site-review.json',k/'layouts.json',ws/'outputs/native-windows-nt5-kernel/trace-entry.py',ws/'outputs/native-windows-prebuild/monitor_capture.py']},limits='NT5 x86 SURFOBJ layout from owned historical winddi header, validated against actual dimensions/stride at runtime. Modern headers add fields and are not used as NT5 offsets. Service-table function addresses must be read from the live pinned kernel; static names alone are not proof of execution.')
assert 'XwnPhase' in mods['probe.exe']['exports'];r['source_sha256']=sha(Path(__file__))
p=pes['ntoskrnl.exe'];assert mods['ntoskrnl.exe']['sha256']=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
assert mods['ntoskrnl.exe']['exports']['memmove']==0x608f0
assert p.get_data(0x60923,2)==p.get_data(0x60aa4,2)==b'\xf3\xa5'
loops=[dict(rva=0x60923,label='forward_rep_movsd',width=4),dict(rva=0x60aa4,label='backward_rep_movsd',width=4)]
decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
for backward,table in [(False,0x609cc),(True,0x60b80)]:
 for count in range(1,8):
  slot=table+(-count if backward else count)*4
  target=struct.unpack('<I',p.get_data(slot,4))[0]-p.OPTIONAL_HEADER.ImageBase
  ins=next(decoder.disasm(p.get_data(target,8),target));assert ins.mnemonic=='mov' and ins.operands[0].reg==capstone.x86.X86_REG_EAX
  operand=ins.operands[1];assert operand.type==capstone.x86.X86_OP_MEM and operand.size==4
  assert operand.mem.base==capstone.x86.X86_REG_ESI and operand.mem.index==capstone.x86.X86_REG_ECX and operand.mem.scale==4
  assert operand.mem.disp==(count*4 if backward else -count*4)
  loops.append(dict(rva=target,label=('backward' if backward else 'forward')+'_scalar_dword',width=4,count=count,table_slot_rva=slot,displacement=operand.mem.disp,raw=bytes(ins.bytes).hex()))
r['memmove_loops']=loops
dest=k/'sites.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Pinned NT5 modules, marker, syscall stubs and aligned memmove loop sites')
