"""Pin actual compiled accounting OFF stub/ON publication, no guest access."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
from capstone.x86_const import X86_OP_MEM,X86_OP_REG,X86_REG_ESP,X86_REG_EBP
dest=k/'instruction-review.json';assert not dest.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm';rows=[]
for name in ['control001','candidate001']:
 p=(k/name/'artifacts/xwnown.dll').resolve();pe=pefile.PE(str(p));linux='/mnt/c/'+p.as_posix()[3:]
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--',tool,linux],text=True,stderr=subprocess.DEVNULL)
 funcs={}
 for symbol in ['XwnUploadRecord','XwnUploadSnapshot']:
  a=int(re.search(r'^([0-9a-fA-F]+) [Tt] _'+symbol+r'$',nm,re.M).group(1),16)
  b=min(int(v,16) for v in re.findall(r'^([0-9a-fA-F]+) [Tt] ',nm,re.M) if int(v,16)>a)
  rva=a-pe.OPTIONAL_HEADER.ImageBase;sec=pe.get_section_by_rva(rva);assert sec.Characteristics&0x08000000
  raw=pe.get_data(rva,b-a);dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True;ins=list(dis.disasm(raw,a))
  assert sum(v.size for v in ins)==len(raw)
  for v in ins:
   assert not v.mnemonic.startswith('f')
   for operand in v.operands:
    if operand.type==X86_OP_REG:assert not v.reg_name(operand.reg).startswith(('xmm','ymm','zmm','mm','st'))
  calls=[v for v in ins if v.mnemonic=='call'];stores=[v for v in ins if v.mnemonic in ['mov','add','adc','or','and'] and v.operands and v.operands[0].type==X86_OP_MEM and v.operands[0].mem.base not in [X86_REG_ESP,X86_REG_EBP]]
  if symbol=='XwnUploadRecord':
   if name=='control001':assert not calls and not stores and any(v.mnemonic=='ret' for v in ins)
   else:assert len(calls)>=2 and stores,'Actual protected publication missing'
  funcs[symbol]=dict(rva=rva,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),resident_section=sec.Name.rstrip(b'\0').decode(),calls=len(calls),nonstack_stores=len(stores),assembly=[v.mnemonic+' '+v.op_str for v in ins])
 rows.append(dict(case=name,binary_sha256=sha(p),functions=funcs))
r=dict(passed=True,physical_access=False,guest_launch=False,no_vector_or_fpu=True,control_publication_compiled_out=True,candidate_protected_publication_observed=True,builds=rows,
 limits='Instruction identity and actual ON/OFF publication only. Runtime counters/pixels, normal shutdown and cold integrity remain independently required.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Actual OFF publication stub and ON protected writes/residency PASS')
