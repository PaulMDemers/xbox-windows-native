"""Bind fault RVA to exact cold NVNet symbols and the shutdown call graph."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash002';sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
p=out/'artifacts/after-nvnetnt5.sys';pe=pefile.PE(str(p));assert sha(p)=='d4aafead757f43c46ba161d2d034aafe05b7024ae693c39d224da42d485927d1'
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm',str(p).replace('\\','/').replace('C:','/mnt/c')],text=True,stderr=subprocess.DEVNULL)
names=['_MiniportShutdown@4','_NvNetIdleTransmitter','_NvNetStopTransmitter','_NvNetStopReceiver','_SidebandUnitReleaseSemaphore','_NvNetSetPowerState','_NvNetPauseProcessing']
symbols={};cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for name in names:
    row=[v.split() for v in nm.splitlines() if v.endswith(' '+name)];assert len(row)==1;rva=int(row[0][0],16)-pe.OPTIONAL_HEADER.ImageBase;s=pe.get_section_by_rva(rva)
    symbols[name]=dict(rva=hex(rva),section=s.Name.rstrip(b'\0').decode(),nonpaged=bool(s.Characteristics&0x08000000),discardable=bool(s.Characteristics&0x02000000))
assert symbols['_NvNetIdleTransmitter']['rva']=='0x7800' and symbols['_NvNetIdleTransmitter']['section']=='PAGE' and not symbols['_NvNetIdleTransmitter']['nonpaged']
assert symbols['_MiniportShutdown@4']['rva']=='0x21f0'
for n in names:
    if n!='_NvNetIdleTransmitter':assert symbols[n]['nonpaged'] and not symbols[n]['discardable']
handler=[dict(rva=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in cs.disasm(pe.get_data(0x21f0,256),0x21f0)]
assert any(v['instruction']=='call 0x7800' for v in handler)
root=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/fatx-dump-map-001/source');sources={}
for n in ['nvnet.c','nic.c','requests.c','phy.c','nvnet.h','hardware.h']:
    q=root/'drivers/network/dd/nvnet'/n
    if q.exists():sources[n]=sha(q)
r=dict(scope=__doc__,physical_access=False,driver_sha256=sha(p),symbols=symbols,handler_disassembly=handler,matched_source_tree=read(k.parent/'fatx-dump-map/inputs.json')['result_tree'],source_sha256=sources,source_note='Existing source annotations reviewed against cold symbol/section and resident handler evidence. Proposed change is only to make the shutdown-reachable idle helper resident; no driver changed in this diagnostic.',primary_references=['https://learn.microsoft.com/en-us/previous-versions/windows/hardware/network/ff550533(v=vs.85)','https://learn.microsoft.com/en-us/previous-versions/windows/hardware/network/ff557121(v=vs.85)'])
(k/'callback-review.json').write_text(json.dumps(r,indent=2)+'\n');print(symbols)
