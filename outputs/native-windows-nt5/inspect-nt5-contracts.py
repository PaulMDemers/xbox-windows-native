"""Record supplied binary evidence for legacy HAL interfaces; no execution."""
import hashlib,json,pathlib,sys
r=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(r/'work/python-packages'))
import pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
out=r/'outputs/native-windows-nt5'
dis=Cs(CS_ARCH_X86,CS_MODE_32)
result={};lines=[]
for name in ('hal.dll','ntoskrnl.exe'):
    path=r/'work/media-inspection/EN_WIN2000_PRO_SP4'/name
    pe=pefile.PE(str(path));base=pe.OPTIONAL_HEADER.ImageBase
    exports={s.name.decode():s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    selected={}
    if name=='hal.dll':
        names=['IoAssignDriveLetters','IoReadPartitionTable','IoSetPartitionInformation','IoWritePartitionTable',
               'ExAcquireFastMutex','ExReleaseFastMutex','ExTryToAcquireFastMutex',
               'KdPortInitialize','KdPortGetByte','KdPortPollByte','KdPortPutByte','KdPortSave','KdPortRestore']
        selected={n:exports[n] for n in names if n in exports}
    else:
        dispatch=exports['HalDispatchTable']
        for offset,n in [(0x18,'HalIoAssignDriveLetters'),(0x1c,'HalIoReadPartitionTable'),(0x20,'HalIoSetPartitionInformation'),(0x24,'HalIoWritePartitionTable')]:
            ptr=pe.get_dword_at_rva(dispatch+offset)
            selected['dispatch_'+n]=ptr-base
        for n in ('Kei386EoiHelper','KeUpdateSystemTime','KeUpdateRunTime','KiDeliverApc','KiDispatchInterrupt','KeProfileInterrupt','KeProfileInterruptWithSource'):
            if n in exports:selected[n]=exports[n]
    result[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'image_base':hex(base),'selected_rvas':{n:hex(a) for n,a in selected.items()}}
    for n,rva in selected.items():
        lines.append('\n'+name+'!'+n+' '+hex(base+rva))
        # Fixed-size evidence windows can include adjacent functions. The
        # printed RVA, not window length, is the verified entry point.
        for i in dis.disasm(pe.get_data(rva,256),base+rva):lines.append(f'{i.address:08x}  {i.mnemonic:8} {i.op_str}')
(out/'stock-contracts.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'stock-contracts-disassembly.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps(result,indent=2))
