"""Resolve sampled Windows RVAs against exact immutable-seed DLLs; no guest mutation."""
from pathlib import Path
import hashlib,json,sys
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import pefile,capstone
out=K/'site-symbols001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
seed=read('seed-symbols001.json');result=read('cost-review001.json');assert seed['passed'] and result['passed']
files={};exports={};dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for row in seed['files']:
 p=Path(row['path'].replace('/mnt/c/','C:/'));data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
 files[row['name']]=pefile.PE(data=data);exports[row['name']]={x.name.decode():x.address for x in files[row['name']].DIRECTORY_ENTRY_EXPORT.symbols if x.name}
w=files['winmm.dll'];assert exports['winmm.dll']['timeGetTime']==0x7bbc and exports['winmm.dll']['DriverCallback']==0x7c45
wi={i.address:i for i in dis.disasm(w.get_data(0x7bbc,0x89),0x7bbc)}
assert wi[0x7bf1].mnemonic=='call' and wi[0x7bf1].op_str=='0x7bfd' and wi[0x7bfc].mnemonic=='ret' and wi[0x7c42].mnemonic=='ret'
n=files['ntdll.dll'];assert exports['ntdll.dll']['NtSetInformationThread']==exports['ntdll.dll']['ZwSetInformationThread']==0x8cdc
ni={i.address:i for i in dis.disasm(n.get_data(0x8cdc,16),0x8cdc)}
assert ni[0x8ce5].mnemonic=='int' and ni[0x8ce5].op_str=='0x2e' and ni[0x8ce7].mnemonic=='ret'
g=files['gdi32.dll'];gi={i.address:i for i in dis.disasm(g.get_data(0x52d2,14),0x52d2)}
assert gi[0x52db].mnemonic=='int' and gi[0x52dd].mnemonic=='ret'
rows=[]
for s in result['sites']:
 m=s['module'];off=int(s['offset'],16)
 if m=='winmm.dll':
  assert off in wi
  label='timeGetTime export body' if off<0x7bfd else 'helper directly called by timeGetTime'
 elif m=='ntdll.dll':assert off==0x8ce7;label='NtSetInformationThread/ZwSetInformationThread syscall return site'
 elif m=='gdi32.dll':assert off==0x52dd;label='internal GDI syscall return site; function name not assigned'
 else:assert m=='rct.exe';label='game RVA only; packed on-disk code not substituted for runtime bytes'
 rows.append(dict(**s,attribution=label))
out.write_text(json.dumps(dict(passed=True,files=seed['files'],disassembler_version=capstone.__version__,rows=rows,
 scope='Exact protected on-disk DLL addresses and decoded instruction boundaries. Runtime code bytes and kernel stacks were not captured. Counts are saved-user locations, not CPU-time fractions; syscall returns do not establish sleeping or kernel costs.'),indent=2)+'\n')
print('Exact DLL address review passed; WINMM samples map to timeGetTime and its direct helper')
