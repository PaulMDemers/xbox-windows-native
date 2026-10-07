"""Test live-discovery logic against an existing frozen private RAM snapshot."""
import hashlib,json,re,sys
from pathlib import Path
from discover_kernel import discover
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'video-shared-trace2'));from walk import read_virtual
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=k.parent/'video-direct-ddi/candidate001';meta=json.loads((source/'timeout-memory.json').read_text());raw=source/'artifacts/timeout.ram'
assert sha(raw)==meta['raw_sha256'];data=raw.read_bytes();cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',meta['registers'])[1],16)
kernel=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe');pe=pefile.PE(str(kernel))
public=k.parent/'native-windows-nt5-kernel/kernel-publics.json';pubs=json.loads(public.read_text())['symbols']
base,r=discover(lambda a,n:read_virtual(data,cr3,a,n),meta['registers'],pe,pubs)
previous=json.loads((source/'timeout-analysis.json').read_text());assert base==int(previous['kernel_base'],16)
r.update(passed=True,scope='Read-only replay of an earlier closed snapshot; no new guest observation',snapshot_sha256=sha(raw),kernel_sha256=sha(kernel),publics_sha256=sha(public),discovery_sha256=sha(k/'discover_kernel.py'),prior_independent_decoder_base=previous['kernel_base'])
dest=k/'discovery-replay.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Two IDT gates agree with prior independent page-table discovery:',hex(base))
