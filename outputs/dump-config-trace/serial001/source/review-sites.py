"""Pin relocated NT5 dump-init instruction windows, with static candidates only."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
p=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe')
b=p.read_bytes();sha=lambda d:hashlib.sha256(d).hexdigest();pe=pefile.PE(data=b)
old=json.loads((k.parent/'fatx-map-rendezvous/flush001/audit.json').read_text())
assert sha(b)==next(r['sha256'] for r in old['protected'] if r['path'].endswith('/ntoskrnl.exe'))
K=json.loads((k.parent/'fatx-paging-buffer/sites.json').read_text())['kernel_base_expected']
delta=K-pe.OPTIONAL_HEADER.ImageBase;cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
sites=[]
for name,rva,n in [('entry',0x22e84,16),('handle_return',0x22eaa,16),('query_call',0x22ed3,5),('query_return',0x22ed8,16),('query_pending_return',0x22ef3,3),('fsctl_call',0x22f46,5),('fsctl_return',0x22f4b,16),('fsctl_pending_return',0x22f61,3),('return',0x22ff9,3),('caller_status',0x235c8,8),('caller_error',0x235d0,8)]:
    raw=pe.get_data(rva,n);data=bytearray(raw);relocs=[]
    for block in pe.DIRECTORY_ENTRY_BASERELOC:
        for e in block.entries:
            if e.type==3 and rva<=e.rva<rva+n:
                at=e.rva-rva;assert at+4<=n
                struct.pack_into('<I',data,at,(struct.unpack_from('<I',data,at)[0]+delta)&0xffffffff);relocs.append(at)
    first=next(cs.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+rva))
    sites.append(dict(name=name,rva=rva,address=K+rva,raw=raw.hex(),relocated=bytes(data).hex(),relocations=relocs,first_instruction=first.mnemonic+' '+first.op_str))
files=['native-windows-nt5-kernel/kernel-publics.json','native-windows-nt5-kernel/process-layouts.json','shutdown-popup-workload/site-review.json','native-windows-nt5-kernel/trace-entry.py']
r=dict(scope=__doc__,kernel_sha256=sha(b),kernel_base_expected=K,kernel_timestamp=pe.FILE_HEADER.TimeDateStamp,sites=sites,dependencies={name:sha((k.parent/name).read_bytes()) for name in files})
out=k/'sites.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print('Pinned11 static dump-init sites, not runtime coverage')
