"""Close unique captures and distinguish CPU allocator facts from GPU ownership."""
import ast,hashlib,json,re,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
def pin(p,h):assert sha(p)==h,str(p);pins[str(p)]=h
for f in ['frozen.json','frozen002.json','frozen003.json','frozen004.json','frozen005.json']:
 for n,h in read(k/f).items():pin(Path(n),h)
inputs=read(k/'inputs.json');pin(Path(inputs['parent']),inputs['parent_sha256'])
for n,h in inputs['inputs'].items():pin(Path(n) if Path(n).is_absolute() else ws/n,h)
rows=[]
for name,report in [('dashboard001','capture.json'),('dashboard002','capture002.json'),('dashboard003','capture003.json'),('kernel004','capture004.json'),('map005','capture005.json')]:
 run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/instance217-runs/nt5-instance217-'+name)
 assert read(run/'cleanup.json')['completedUtc'] and not (run/'hdd.qcow2').exists()
 r=read(k/report);assert not r['nt5_launched'] and not r['allocator_invoked'] and not r['gpu_writes'] and r['breakpoints_installed']==0
 if name in ['kernel004','map005']:assert r['passed'] and r['resumed'] and 'resume_error' not in r
 else:assert not r['passed'] and r['error']
 rows.append(dict(case=name,passed=r['passed'],capture_sha256=sha(k/report),cleanup_sha256=sha(run/'cleanup.json'),instance_sha256=sha(run/'instance.json'),snapshot_clone_discarded=True))
r=read(k/'capture004.json');p=k/'artifacts/kernel004/kernel-resident.bin';pin(p,r['kernel_resident_sha256']);data=p.read_bytes();base=r['kernel_base']
window=k/'artifacts/kernel004/claim-window.bin';pin(window,r['claim_window_sha256']);assert data[r['claim_rva']:r['claim_rva']+1024]==window.read_bytes()
pe=struct.unpack_from('<I',data,0x3c)[0];exp=struct.unpack_from('<I',data,pe+120)[0];fields=struct.unpack_from('<IIHHIIIIIII',data,exp)
version_rva=struct.unpack_from('<I',data,fields[8]+(324-fields[5])*4)[0];version=struct.unpack_from('<HHHH',data,version_rva);assert version==(1,0,4627,1)
for off,n in [(r['claim_rva'],0xbc),(0x800360d0-base,4),(version_rva,8)]:assert not any(v['rva']<off+n and off<v['rva']+v['bytes'] for v in r['unmapped_pages'])
actual_claim_size=struct.unpack_from('<I',data,0x800360d0-base)[0];assert actual_claim_size==0x5000
tests=read(k/'claim-arithmetic-tests.json');assert tests['passed'] and tests['cases']==99 and tests['checks']==891
pin(k/'test-claim.py',tests['source_sha256']);assert hashlib.sha256(window.read_bytes()[:0xbc]).hexdigest()==tests['function_sha256']
m=read(k/'capture005.json');assert m['cpu_alias_proven'] and not m['gpu_ramin_alias_proven'] and not m['nt5_ownership_granted']
assert [(v['virtual'],v['physical']) for v in m['page_walks']]==[(0x83feb000,0x03feb000),(0x83feffff,0x03feffff),(0x83ff0000,0x03ff0000),(0x83ffffff,0x03ffffff)]
pin(k/'capture004.json',m['reference_capture_sha256'])
assert 'MmClaimGpuInstanceMemory@8               @ 168 NONAME' in (k/'artifacts/xboxkrnl.exe.def').read_text()
pb=ws/'outputs/video-gpu-transfer-contract212/artifacts/nxdk/lib/pbkit/pbkit.c';text=pb.read_text();assert text.count('MmClaimGpuInstanceMemory(')==1 and 'MmClaimGpuInstanceMemory(0xFFFFFFFF,&baseaddr)' in text
assert 'pb_GpuInstMem-=INSTANCE_MEM_MAXSIZE' in text
reservations=read(ws/'outputs/video-gpu-transfer-contract212/boot-reservation.json');b=reservations['reservations'][0]
assert (b['indexed_backbuffer_start'],b['indexed_backbuffer_end'])==(0x03fb2d00,0x04000000)
lo,hi=0x03feb000,0x03ff0000;overlap=max(0,min(hi,b['indexed_backbuffer_end'])-max(lo,b['indexed_backbuffer_start']));assert overlap==0x5000
for p in k.glob('*.py'):ast.parse(p.read_text())
for p in k.glob('capture*.py'):
 s=p.read_text();assert 'def write(' not in s and 'def bp(' not in s and 'Z0,' not in s
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),pins=pins,cases=rows,kernel_version=version,actual_claim_size=actual_claim_size,cpu_allocation_start=lo,cpu_allocation_end=hi,padding_bytes=0x10000,bootvid_overlap_bytes=overlap,pbkit_query_only=True,pbkit_source_sha256=sha(pb),boot_reservation_sha256=sha(ws/'outputs/video-gpu-transfer-contract212/boot-reservation.json'),gap_pages=len(r['unmapped_pages']),ordinary_qualified=False,physical_access=False,gpu_ramin_alias_proven=False,nt5_ownership_granted=False,all_owned_sessions_closed=True,limits='Resident Complex4627 code and CPU page walks, private kernel gaps retained, modeled arithmetic callees, closed discarded snapshot children and unchanged parent. Arithmetic overlap is real for this stock CPU allocation and retained NT5 layout; no actual GPU alias/collision, physical kernel equivalence, ownership transfer, context acquisition or GPU copy qualification.'),indent=2)+'\n',encoding='utf-8')
print('217 reviewed closed captures and CPU allocation facts; GPU handoff remains unqualified')
