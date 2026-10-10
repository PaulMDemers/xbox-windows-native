"""Review exact bounded216 read-only helper and inherited unchanged gates."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['model-inventory.json','handoff-inventory.json','host-tests001.json','parser-tests.json','build-review.json','native-input-review.json']:assert read(k/name)['passed']
module={};exec(compile((k/'snapshot_trace.py').read_text(),'snapshot_trace.py','exec'),module)
offsets=[int(v,16) for v in re.findall(r'^\s+(0x[0-9a-f]+)u,',(k/'registers.h').read_text(),re.M)]
assert offsets==module['OFFSETS']==[v['offset'] for v in read(k/'model-inventory.json')['registers']]
assert len(offsets)==len(set(offsets))==26
source=(k/'gpu_snapshot.c').read_text();assert source.count('READ_REGISTER_ULONG(')==1
assert not any(v in source for v in ['WRITE_REGISTER','WRITE_PORT','MmMap','VideoPortGetDeviceBase'])
assert source.index('if(Phase>=2)')<source.index('XgnSeen[Phase]')<source.index('READ_REGISTER_ULONG(')
assert source.index('irql!=PASSIVE_LEVEL')<source.index('READ_REGISTER_ULONG(')
assert 'Length!=XGN_MAPPED_LENGTH' in source and 'XgnOffsets[i]>Length-sizeof(ULONG)' in source
assert 'if(InterlockedCompareExchange(&XgnSeen[Phase],1,0)) return;' in source
assert read(k/'parser-tests.json')['checks']==294
assert all(v['exit_code']==0 and not v['stderr'] for v in read(k/'host-tests001.json')['runs'])
for name in ['common.py','boundary_analysis.py','upload_analysis.py','runner_analysis.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py','interval_policy.py','typed-state.py']:
 assert (k/name).read_bytes()==(k.parent/'video-gpu-state214'/name).read_bytes()
body=read(k/'model-inventory.json')['reader_bodies']
assert 'r = memory_region_size(d->vram);' in body['pfb_read']['body']
assert 'r = d->pfb.regs[addr];' in body['pfb_read']['body']
assert 'r = pgraph_reg_r(pg, addr);' in body['pgraph_read']['body']
assert all(x not in offsets for x in [0x600808,0x400754])
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
names=['gpu_snapshot.c','registers.h','snapshot_trace.py','host-test.c','host-shim/ntddk.h','build001.py','inventory-model002.py','inventory-handoff002.py']
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),source_pins={n:sha(k/n) for n in names},approved_offsets=offsets,
 native_import_delta=['ntoskrnl.exe!READ_REGISTER_ULONG'],new_gpu_writes=False,new_mmio_mapping=False,
 physical_access=False,guest_launch=False,gpu_ownership_proven=False,
 manual_review=['26 bounded reads at two retained hooks; additional CFG0/CSTATUS/DEBUG3/CTX_CONTROL use reviewed default or size read paths.',
 'No indexed/raster/RAMIN read, IRQ acknowledgement, GPU reset, handler, context initialization or device-policy change.',
 'Mock concurrent once gate is CPU-only; two sequential snapshots are not atomic/quiescence or GPU grants.',
 'Exact actual NT5 read import body pinned; no newer barrier or physical read safety inferred.',
 'Unchanged211 GDI and cold/event gates retained. Actual launcher/loader hashes match214; mutable historical loader source relationship explicit.'],
 limits='Source/import/host review only; runtime/context/backing/physical qualification still absent.'),indent=2)+'\n',encoding='utf-8')
print('Reviewed216 source and unchanged strict gates PASS')
