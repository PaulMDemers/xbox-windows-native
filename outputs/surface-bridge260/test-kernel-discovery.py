"""Verify next-attempt IDT decoder; synthetic gates only, not live evidence."""
import hashlib,importlib.util,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'kernel-discovery-review.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('discovery',k/'kernel-discovery.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
p=ws/'outputs/native-windows-nt5-kernel/kernel-publics.json';j=json.loads(p.read_text());assert j['pdb_sha256']=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
rvas={0:j['symbols']['_KiTrap00']['rva'],14:j['symbols']['_KiTrap0E']['rva']};idt=0x828cb400;checks=0
def gates(base):
 return {idt+8*v:struct.pack('<HHBBH',(base+rva)&65535,8,0,0x8e,(base+rva)>>16) for v,rva in rvas.items()}
for base in [0x80400000,0x823d0000,0x823df000,0x82400000]:
 m=gates(base);actual,rows=mod.discover(lambda a,n:m[a],idt,2047,rvas);assert actual==base and len(rows)==2;checks+=1
for label,vector,field,value in [('absent',0,3,0x0e),('reserved',0,2,1),('LDT',0,1,12),('16bit',14,3,0x86),('data',14,3,0x9e),('otherbase',14,0,0)]:
 m=gates(0x823d0000);parts=list(struct.unpack('<HHBBH',m[idt+8*vector]));parts[field]=value;m[idt+8*vector]=struct.pack('<HHBBH',*parts)
 try:mod.discover(lambda a,n:m[a],idt,2047,rvas)
 except AssertionError:checks+=1
 else:raise AssertionError(label)
r=dict(passed=True,checks=checks,guest_used=False,physical_access=False,
 inputs={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['kernel-discovery.py','test-kernel-discovery.py']},
 symbol_source=p.relative_to(ws).as_posix(),symbol_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),trap_rvas=rvas,
 limits='Static PDB plus synthetic IDT arithmetic only; next fresh attempt must read actual IDTR/gates and validate matching PE and resident trap bytes.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('IDT-based next-attempt discovery:10 synthetic checks PASS')
