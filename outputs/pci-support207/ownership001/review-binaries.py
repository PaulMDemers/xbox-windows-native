"""Inspect pinned physical owners and new resource-only binaries without executing them."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import capstone,pefile
k=Path(__file__).resolve().parent
pci=k.parent
repo=pci.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def inspect(path,digest):
    assert sha(path)==digest
    pe=pefile.PE(str(path))
    imports={d.dll.decode():[i.name.decode() if i.name else '#'+str(i.ordinal) for i in d.imports]
             for d in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])}
    dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    dis.skipdata=True
    io=[];ports=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:continue
        for ins in dis.disasm(sec.get_data()[:sec.Misc_VirtualSize],pe.OPTIONAL_HEADER.ImageBase+sec.VirtualAddress):
            item=dict(address=hex(ins.address),instruction=ins.mnemonic+' '+ins.op_str)
            if ins.mnemonic in ('in','out','insb','insw','insd','outsb','outsw','outsd'):io.append(item)
            if any(hex(n) in ins.op_str for n in (0xc000,0xc002,0xc004,0xc006,0xc008,0xc200)):ports.append(item)
    return dict(sha256=digest,imports=imports,port_instructions=io,controller_constants=ports,
                machine=pe.FILE_HEADER.Machine,subsystem=pe.OPTIONAL_HEADER.Subsystem,
                subsystem_version=[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion]),pe

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('owners','build'));ap.add_argument('--build',default='build002');args=ap.parse_args();mode=args.mode
    dest=k/(mode+'-review'+(args.build[-3:] if mode=='build' else '001')+'.json');assert not dest.exists()
    result=dict(scope=__doc__,physical_access=False,mode=mode,binaries={},passed=True)
    if mode=='owners':
        p=read(pci/'hardware220/physical001.json')
        for label,key in (('HAL','/E/Applications/XWNFBoot/loader/halxboxnt5.dll'),('video0093','/F/winnt/system32/drivers/xboxvnt5.sys')):
            row=p['before'][key];result['binaries'][label],pe=inspect(repo/row['path'],row['sha256'])
            if label=='HAL':
                result['hal_smbus_exports']=[s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name and b'smb' in s.name.lower()]
                assert not result['hal_smbus_exports']
                # Existing physical-matched disassembly establishes the direct reboot owner.
                result['hal_power_disassembly_sha256']=sha(pci/'hal-power-disassembly.txt')
            else:assert not result['binaries'][label]['port_instructions']
        audio=k.parents[4]/'audio/repo/outputs/audio220'
        key='/F/winnt/system32/drivers/ac97xnt5.sys'
        row=read(audio/'capture002.json')['files'][key]
        result['binaries']['restored_audio'],pe=inspect(audio/('artifacts/before002'+key),row['sha256'])
        assert not result['binaries']['restored_audio']['port_instructions']
        result['limits']='Static source/import/disassembly review, not exhaustive control-flow or runtime concurrency proof. Audio input is the owner-captured/restored legacy binary. HAL has no exported shared SMBus broker; no new locking contract is inferred.'
    else:
        build=read(k/(args.build+'.json'))
        for row in build['sources']:assert sha(k/row['name'])==row['sha256']
        providers={}
        for row in read(pci/'providers001.json')['files'].values():
            p=pci/'artifacts/providers001'/row['output'];assert sha(p)==row['sha256'];providers[p.name.lower()]=p
        providers['hal.dll']=providers['halxboxnt5.dll']
        for row in build['files']:
            p=k/'artifacts'/args.build/row['name'];assert sha(p)==row['sha256']
            if p.suffix not in ('.sys','.exe'):continue
            info,pe=inspect(p,row['sha256']);resolved=[]
            assert info['machine']==0x14c and info['subsystem_version']==[5,0]
            assert not info['port_instructions']
            for dll,names in info['imports'].items():
                provider=providers[dll.lower()];exports=pefile.PE(str(provider)).DIRECTORY_ENTRY_EXPORT.symbols
                symbols={s.name.decode():s for s in exports if s.name}
                for name in names:
                    assert name in symbols and not symbols[name].forwarder
                    assert not any(t in name for t in ('READ_PORT','WRITE_PORT','BusData','SMBus'))
                    resolved.append(dict(dll=dll,name=name,provider_sha256=sha(provider)))
            info['resolved_imports']=resolved;result['binaries'][p.name]=info
        result['tests']=read(k/('tests'+args.build[-3:]+'.json'));assert result['tests']['passed']
        result['limits']='Compile/static resource-policy validation; kernel derivative has no telemetry I/O and is not installed. No PnP allocator, lifecycle or hardware functionality claim.'
    dest.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(mode+' binary review passed')
if __name__=='__main__':main()
