"""Pin native observation sites to the owned matching NT5 kernel and PDB layouts."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
kernel=ws/'outputs/native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'
src=ws/'outputs/native-windows-nt5-kernel';pubs=json.loads((src/'kernel-publics.json').read_text())
pe=pefile.PE(str(kernel));md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
sites=[]
for name,argc in [('_NtRaiseHardError@24',6),('_ExRaiseHardError@24',6),('_ExpRaiseHardError@24',6),('_NtCreateProcess@32',8),('_PspExitProcess@8',2),('_NtShutdownSystem@4',1)]:
    rva=pubs['symbols'][name]['rva'];raw=pe.get_data(rva,3)
    sites.append(dict(name=name,rva=rva,bytes=raw.hex(),argc=argc,frame='esp'))
for name,rva,expected,location in [('NtTerminateProcess_AfterReference',0xe335e,'817d0c04000140','[ebp-8] EPROCESS'),('NtResumeThread_BeforeResume',0xe55bd,'ff75dc','[ebp-0x24] ETHREAD')]:
    raw=pe.get_data(rva,len(bytes.fromhex(expected)));assert raw.hex()==expected
    sites.append(dict(name=name,rva=rva,bytes=expected,argc=2,frame='ebp',target=location))
r=dict(scope=__doc__,kernel_sha256=hashlib.sha256(kernel.read_bytes()).hexdigest(),pdb_sha256=pubs['pdb_sha256'],sites=sites,
       resume_reference_disassembly=[dict(rva=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in md.disasm(pe.get_data(0xe55a0,0x2f),0xe55a0)],
       thread_owner_offset=json.loads((src/'thread-layouts.json').read_text())['_ETHREAD']['fields']['ThreadsProcess']['offset'],
       limits='Resume observations precede KeResumeThread and do not prove the thread subsequently ran. Creation calls may fail. Target command lines can be nonresident.')
(k/'site-review.json').write_text(json.dumps(r,indent=2)+'\n')
