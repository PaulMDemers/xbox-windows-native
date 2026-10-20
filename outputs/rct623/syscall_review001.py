"""Resolve original-control syscall return sites from exact cached NT5 DLL."""
from pathlib import Path
import hashlib,json,sys
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import pefile,capstone
out=K/'syscall-review001.json';assert not out.exists()
seed=json.loads((K.parent/'rct621/seed-symbols001.json').read_text());f=next(x for x in seed['files'] if x['name']=='ntdll.dll')
p=Path(f['path'].replace('/mnt/c/','C:/'));assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
m=json.loads(Path('C:/xwn623/pc001/cold1-002/manifest.json').read_text());assert m['winnt/system32/ntdll.dll']['sha256']==f['sha256']
pe=pefile.PE(str(p));ex={e.name.decode():e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name};cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
rows=[]
for base,off,name in [(0x8f08,0x8f13,'NtWaitForSingleObject'),(0x8398,0x83a3,'NtDelayExecution')]:
 assert ex[name]==base
 ins={i.address:i for i in cs.disasm(pe.get_data(base,16),base)};assert ins[off-2].mnemonic=='int' and ins[off-2].op_str=='0x2e' and ins[off].mnemonic=='ret'
 rows.append(dict(export=name,export_rva=hex(base),saved_return_rva=hex(off)))
loc=json.loads((K/'location-review001.json').read_text());assert loc['passed']
for i in ['5','7']:assert loc['cases'][i]==[dict(module='ntdll.dll',offset='0x83a3',label='module offset only',samples=224)]
out.write_text(json.dumps(dict(passed=True,dll_sha256=f['sha256'],sites=rows,
 conclusion='Paced controls stop in NtDelayExecution; busy controls also have NtWaitForSingleObject returns from zero-timeout release checks. The API name alone does not supply wait duration or CPU cost.',
 scope='Exact on-disk exports and decoded syscall-return boundaries. No kernel stacks/runtime bytes captured.'),indent=2)+'\n')
