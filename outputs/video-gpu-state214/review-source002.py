"""Prelaunch source contract review of native hooks/providers and scoped parser inputs."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review002.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for filename in ['model-inventory.json','host-tests002.json','parser-tests.json','build-review.json','native-input-review.json']:assert read(k/filename)['passed']
rows=read(k/'model-inventory.json')['registers'];header=(k/'registers.h').read_text()
offsets=[int(v,16) for v in re.findall(r'^\s+(0x[0-9a-f]+)u,',header,re.M)]
module={};exec(compile((k/'snapshot_trace.py').read_text(),'snapshot_trace.py','exec'),module)
assert offsets==module['OFFSETS']==[v['offset'] for v in rows]
source=(k/'gpu_snapshot.c').read_text();assert source.count('READ_REGISTER_ULONG(')==1
assert 'WRITE_REGISTER' not in source and 'WRITE_PORT' not in source and 'MmMap' not in source
assert 'if(InterlockedCompareExchange(&XgnSeen[Phase],1,0)) return;' in source
assert source.index('if(Phase>=2)')<source.index('XgnSeen[Phase]')<source.index('READ_REGISTER_ULONG(')
assert source.index('irql!=PASSIVE_LEVEL')<source.index('READ_REGISTER_ULONG(')
assert 'Length!=XGN_MAPPED_LENGTH' in source and 'XgnOffsets[i]>Length-sizeof(ULONG)' in source
host=read(k/'host-tests002.json');assert all(v['exit_code']==0 and not v['stderr'] for v in host['runs'])
assert read(k/'parser-tests.json')['checks']==254
assert read(k/'build-review.json')['read_register_provider']['instructions']==[['mov','edx, dword ptr [esp + 4]'],['mov','eax, dword ptr [edx]'],['ret','4']]
for p in k.glob('*.py'):ast.parse(p.read_text())
pins={name:sha(k/name) for name in ['gpu_snapshot.c','registers.h','snapshot_trace.py','host-test002.c','host-shim/ntddk.h','inventory-model.py','review-build.py','review-native-inputs.py','test-host002.py','test-parser002.py']}
review=dict(passed=True,source_sha256=sha(Path(__file__)),source_pins=pins,approved_offsets=offsets,
 native_import_delta=['ntoskrnl.exe!READ_REGISTER_ULONG'],new_gpu_writes=False,new_mmio_mapping=False,
 phase_hooks=['after retained-mode initialization before Ready','after first successful shared framebuffer mapping'],
 physical_access=False,guest_launch=False,gpu_ownership_proven=False,
 manual_review=['No GPU write/submission/reset/ack/index operation in the helper; existing baseline CRTC port writes unchanged.',
 'Existing mapping caller lifetime retained; no address stored/exported.22 bounded reads per phase,CPU-only interlocked once gate.',
 'Actual read handlers and PGRAPH regs_ helper reviewed. Raster/RDI excluded. Sequential state does not prove idle/exclusive ownership.',
 'Kernel read ABI pins old actual implementation; modern documentation is not an assertion of extra hardware ordering.',
 'Parser first failure is a harness expectation error; parser unchanged, all exact214 and strict event gates retained.'],
 limits='Human source review plus mechanical pins/guards, not exhaustive concurrency proof, physical read safety, queue/completion/drain or runtime.')
dest.write_text(json.dumps(review,indent=2)+'\n');print('Source/provider/offset contract review PASS')
