"""Pin the observed request's caller and existing filesystem dispatch contract."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import capstone,pefile
sha=lambda b:hashlib.sha256(b).hexdigest()
mods=json.loads((k/'modules.json').read_text());cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
p=Path(mods['ntoskrnl.exe']['path']);data=p.read_bytes();assert sha(data)==mods['ntoskrnl.exe']['sha256'];pe=pefile.PE(data=data)
rows=[]
for start,end in [(0x22ef6,0x22f4b),(0x22f61,0x22ffc)]:
    raw=pe.get_data(start,end-start)
    rows.append(dict(start_rva=hex(start),end_rva=hex(end),bytes=raw.hex(),instructions=[dict(rva=hex(i.address-pe.OPTIONAL_HEADER.ImageBase),text=i.mnemonic+' '+i.op_str) for i in cs.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+start)]))
src=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/fatx-directory-order-001/source')
files=['drivers/filesystems/vfatfs/fsctl.c','drivers/filesystems/vfatfs/vfat.h','drivers/filesystems/vfatfs/fat.c','drivers/filesystems/fastfat/fsctrl.c','sdk/include/xdk/iotypes.h']
r=dict(scope=__doc__,kernel_sha256=sha(data),kernel_windows=rows,owned_source_sha256={n:sha((src/n).read_bytes()) for n in files},observed_fsctl='0x9003b',observed_input=65536,observed_fatx_status='0xc0000010',notes=['Static instruction windows supplement trace001; they do not establish a successful mapping or dump write.','Microsoft current docs contain apparent field-description inconsistencies (GET code, clusters, paged pool). The NT5 consumer and owned sample implementation require byte lengths, byte volume offsets and a pointer to caller-owned nonpaged extent storage. Verify each before implementation.'])
out=k/'contract-review.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
for row in rows:
    for i in row['instructions']:print(i['rva'],i['text'])
