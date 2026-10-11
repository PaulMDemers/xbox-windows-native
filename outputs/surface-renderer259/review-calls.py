"""Verify every native checkpoint call survived optimization with three arguments."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'callsite-review.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import capstone,pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((k/'probe-review001.json').read_text());file=k/'artifacts/build001/probe.exe'
assert sha(file)==review['native_sha256'];pe=pefile.PE(str(file));base=pe.OPTIONAL_HEADER.ImageBase
target=base+review['checkpoint_rva'];reply=base+review['symbols_rva']['_Reply']
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
section=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
ins=list(md.disasm(section.get_data(),base+section.VirtualAddress));calls=[]
for index,i in enumerate(ins):
    if i.mnemonic=='call' and i.op_str==hex(target):
        before=ins[index-3:index];stage=len(calls)+1
        assert [(v.mnemonic,v.op_str) for v in before]==[
            ('mov','dword ptr [esp + 8], ebx'),('mov',f'dword ptr [esp + 4], {reply:#x}'),
            ('mov',f'dword ptr [esp], {stage}')]
        calls.append(dict(stage=stage,rva=i.address-base,bytes=i.bytes.hex(),argument_instructions=[dict(rva=v.address-base,bytes=v.bytes.hex(),text=v.mnemonic+' '+v.op_str) for v in before]))
assert len(calls)==5
logs=['renderer-build001.log','artifacts/admission001/run.log','artifacts/admission002/run.log',
      'artifacts/build001/host-build.txt','artifacts/build001/host-run.txt','artifacts/build001/native-build.txt']
r=dict(passed=True,guest_executed=False,source_sha256=sha(Path(__file__)),native_sha256=sha(file),
       calls=calls,private_log_pins={n:sha(k/n) for n in logs},
       limits='Static callsites only; actual process, relocation, handle and driver owner must still be attested live.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Five native checkpoint calls verified; private build/test logs pinned')
