"""Exact reused build and narrowly matched original INF review, before launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-restart-guard178';dest=k/'input-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
same={}
for n in ['runner.c','restart_gate.h','test-gate.c','gdi-probe.c','artifacts/runner.exe','artifacts/gdi-probe.exe','artifacts/host-gate']:
 assert (k/n).read_bytes()==(old/n).read_bytes(),n
 same[n]=sha(k/n)
review=json.loads((old/'build-review.json').read_text());assert review['passed'] and review['sha256']==same['artifacts/runner.exe']
text=(k/'xwnunused179.inf').read_text();models=[v for v in text.splitlines() if '=XWN.Unused,PCI' in v]
ids=[v.split(',',1)[1] for v in models]
expected=['PCI\\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1','PCI\\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1','PCI\\VEN_1B36&DEV_0005&SUBSYS_00000000&REV_00']
assert ids==expected and text.count('AddService=,2')==1
assert all(v not in text for v in ['CopyFiles=','DelReg=','AddReg=','ConfigFlags','ExcludeFromSelect','ServiceBinary=','StartType='])
inv=json.loads((old/'candidate001/device-inventory.json').read_text())
for row in inv['hives'][0]['devices']:assert any(v in row['values']['HardwareID']['decoded'].split('\0') for v in expected[:2])
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sites=json.loads((k/'sites.json').read_text());providers={}
for name,row in sites['binaries'].items():assert sha(ws/row['path'])==row['sha256'];providers[name]=row['sha256']
setup=pefile.PE(str(k/'artifacts/setupapi.dll'));export=next(v for v in setup.DIRECTORY_ENTRY_EXPORT.symbols if v.name==b'CMP_WaitNoPendingInstallEvents');assert not export.forwarder
r=dict(passed=True,physical_access=False,guest_launched=False,reused_exact_builds=same,build_review_sha256=sha(old/'build-review.json'),actual_provider_sha256=providers,
 original_inf_sha256=sha(k/'xwnunused179.inf'),exact_hardware_ids=ids,no_function_service=True,no_binary=True,no_offline_registry_edits=True,
 wait_export_rva=export.address,reference='https://learn.microsoft.com/en-us/windows-hardware/drivers/install/installing-a-null-driver',
 inherited_host_tests=dict(header_sha256=same['restart_gate.h'],source_sha256=same['test-gate.c'],binary_sha256=same['artifacts/host-gate'],cases=8,asan_ubsan=True,rerun=False),
 limits='Static exact reuse/package review; normal SetupAPI runtime binding and guarded restart unvalidated. Explicit unused-device compatibility configuration, not functional hardware support or physical promotion.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Exact reused build and three complete hardware-ID null models reviewed')
