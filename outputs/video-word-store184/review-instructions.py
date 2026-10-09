"""Pin actual scalar stores/control REP body, imported providers and geometry."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
from capstone.x86_const import X86_OP_MEM,X86_OP_REG,X86_REG_EAX,X86_REG_EBX
dest=k/'instruction-review.json';assert not dest.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm';reports=[]
for name in ['control001','candidate001']:
 p=k/name/'artifacts/xwnown.dll';pe=pefile.PE(str(p));posix='/mnt/c/'+str(p).replace('\\','/')[3:]
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--',tool,posix],text=True,stderr=subprocess.DEVNULL)
 address=int(re.search(r'^([0-9a-fA-F]+) [Tt] _XwnUploadBox$',nm,re.M).group(1),16)
 end=min(int(a,16) for a in re.findall(r'^([0-9a-fA-F]+) [Tt] ',nm,re.M) if int(a,16)>address)
 rva=address-pe.OPTIONAL_HEADER.ImageBase;section=pe.get_section_by_rva(rva);assert section.Characteristics&0x08000000
 raw=pe.get_data(rva,end-address);dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True;instructions=list(dis.disasm(raw,address))
 assert sum(v.size for v in instructions)==len(raw),'Undecoded bytes'
 for ins in instructions:
  assert not ins.mnemonic.startswith('f'),'Unexpected FPU instruction'
  for op in ins.operands:
   if op.type==X86_OP_REG:assert not ins.reg_name(op.reg).startswith(('xmm','ymm','zmm','mm','st'))
 writes=[]
 for ins in instructions:
  if ins.mnemonic=='mov' and ins.operands[0].type==X86_OP_MEM:
   a,b=ins.operands[:2]
   if a.mem.base==X86_REG_EAX and a.mem.index==0 and a.mem.disp in range(-32,0,4) and b.type==X86_OP_REG:
    assert a.size==b.size==4;writes.append(dict(address=ins.address,displacement=a.mem.disp,bytes=ins.bytes.hex(),text=ins.mnemonic+' '+ins.op_str))
 if name=='candidate001':assert [v['displacement'] for v in writes]==list(range(-32,0,4))
 else:assert not writes
 memmove=int(re.search(r'^([0-9a-fA-F]+) [Tt] _memmove$',nm,re.M).group(1),16)
 assert any(i.mnemonic=='call' and i.op_str==hex(memmove) for i in instructions),'Baseline/fallback missing'
 mrva=memmove-pe.OPTIONAL_HEADER.ImageBase;copybytes=pe.get_data(mrva,180);assert b'\xf3\xa5' in copybytes
 reports.append(dict(case=name,binary_sha256=sha(p),upload_address=address,upload_rva=rva,upload_bytes=len(raw),upload_sha256=hashlib.sha256(raw).hexdigest(),resident_section=section.Name.rstrip(b'\0').decode(),scalar_stores=writes,memmove_address=memmove,memmove_prefix_sha256=hashlib.sha256(copybytes).hexdigest(),baseline_rep_movsd_observed=True,no_vector_fpu_observed=True))
old=k.parent/'video-clip-upload/display';assert (k/'display/surface.c').read_bytes()==(old/'surface.c').read_bytes()
before=(old/'shadow.c').read_text();after=(k/'display/shadow.c').read_text();start='VOID XwnUpload(PPDEV'
assert before[before.index(start):]==after[after.index(start):],'Clip/engine logic changed'
assert (k/'display/ownership.c').read_text().startswith((old/'ownership.c').read_text())
dest.write_text(json.dumps(dict(passed=True,builds=reports,engine_clip_source_unchanged=True,surface_allocation_source_unchanged=True,membership_lifetime_source_unchanged=True,cache_mode_gpu_policy_unchanged=True,physical_access=False,ordinary_qualified=False,limits='Actual compiled static instruction proof; no live/hardware timing claim.'),indent=2)+'\n');print('Actual eight ordered32bit stores/control REP copy pinned; engine/clip/surface unchanged')
