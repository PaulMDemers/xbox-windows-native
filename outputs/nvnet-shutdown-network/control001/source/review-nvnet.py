"""Review matched NVNet builds, exact imports and shutdown code residency."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
paths={'ntoskrnl.exe':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe'),'hal.dll':k.parent/'hal-dump-path/artifacts/hal-candidate001.dll','ndis.sys':k.parent/'controlled-dump-observe/crash002/artifacts/after-ndis.sys'}
assert sha(paths['ntoskrnl.exe'])=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
assert sha(paths['hal.dll'])=='7c6a3bfb9b6794c3b6fbce95fb76dc57d003843c19512b3ddb186604f668ed08'
assert sha(paths['ndis.sys'])=='57e1423903b55ff30e800438c0cf024b3ff7161fd332f8b6eafbc02699b9d877'
exports={n:{v.name for v in pefile.PE(str(p)).DIRECTORY_ENTRY_EXPORT.symbols if v.name} for n,p in paths.items()}
names=['_MiniportShutdown@4','_NvNetIdleTransmitter','_NvNetStopTransmitter','_NvNetStopReceiver','_SidebandUnitReleaseSemaphore','_NvNetSetPowerState','_NvNetPauseProcessing']
r={};cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for case,folder,lockname in [('control001','nvnet-shutdown-control-001','control-inputs.json'),('candidate001','nvnet-shutdown-resident-002','inputs.json')]:
    root=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build')/folder;build=read(root/'build-report.json');lock=read(k/lockname)
    assert build['status']=='compiled' and build['verified_source_tree']==lock['result_tree'] and build['inputs_sha256']==sha(k/lockname)
    target=k/'artifacts'/('nvnet-'+case+'.sys');data=(root/'artifacts/nvnetnt5.sys').read_bytes()
    if target.exists():assert target.read_bytes()==data
    else:target.write_bytes(data)
    assert len(build['artifacts'])==1 and sha(target)==build['artifacts'][0]['sha256']
    (k/('nvnet-build-'+case+'.json')).write_bytes((root/'build-report.json').read_bytes())
    pe=pefile.PE(data=data);assert pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
    imports=[dict(dll=e.dll.decode().lower(),name=v.name.decode()) for e in pe.DIRECTORY_ENTRY_IMPORT for v in e.imports]
    assert all(v['dll'] in exports and v['name'].encode() in exports[v['dll']] for v in imports)
    nm=subprocess.check_output(['wsl','-d','Ubuntu','--','/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm','/home/paul/xbox-windows-native/build/'+folder+'/artifacts/nvnetnt5.sys'],text=True)
    sites={};disassembly={}
    for name in names:
        rows=[v.split() for v in nm.splitlines() if v.endswith(' '+name)];assert len(rows)==1
        rva=int(rows[0][0],16)-pe.OPTIONAL_HEADER.ImageBase;s=pe.get_section_by_rva(rva)
        sites[name]=dict(rva=hex(rva),section=s.Name.rstrip(b'\0').decode(),nonpaged=bool(s.Characteristics&0x08000000),discardable=bool(s.Characteristics&0x02000000))
        assert not sites[name]['discardable']
        assert sites[name]['nonpaged']==(case=='candidate001' or name!='_NvNetIdleTransmitter')
        ins=[]
        ends=[int(v.split()[0],16)-pe.OPTIONAL_HEADER.ImageBase for v in nm.splitlines() if len(v.split())==3 and v.split()[1].upper()=='T' and int(v.split()[0],16)>rva+pe.OPTIONAL_HEADER.ImageBase];size=min(ends)-rva
        for i in cs.disasm(pe.get_data(rva,size),rva):
            ins.append(dict(rva=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str))
        disassembly[name]=ins
    assert any(v['instruction']=='call '+sites['_NvNetIdleTransmitter']['rva'] for v in disassembly['_MiniportShutdown@4'])
    assert any(v['dll']=='hal.dll' and v['name']=='KeStallExecutionProcessor' for v in imports)
    source=root/'source/drivers/network/dd/nvnet/nic.c'
    r[case]=dict(name=target.name,sha256=sha(target),source_tree=lock['result_tree'],source_sha256=sha(source),imports=imports,functions=sites,disassembly=disassembly,checksum_valid=True)
assert r['control001']['imports']==r['candidate001']['imports']
assert read(k/'inputs.json')['profiles']==read(k/'control-inputs.json')['profiles']
r.update(scope=__doc__,export_binary_sha256={n:sha(p) for n,p in paths.items()},physical_access=False,runtime_qualified=False)
(k/'nvnet-review.json').write_text(json.dumps(r,indent=2)+'\n');print({c:r[c]['sha256'] for c in ['control001','candidate001']})

