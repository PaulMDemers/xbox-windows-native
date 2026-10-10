"""Read-only source/host evidence review, including earlier preserved design gap."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checked=0
def pin(p,digest):
 global checked
 assert sha(p)==digest,str(p);checked+=1
r=read(k/'inventory.json');assert r['passed'];pin(k/'inventory.py',r['source_sha256'])
b=ws/'outputs/xemu-cpu-surface-evict/build003'
pin(b/'candidate-source-pins.json',r['source_manifest_sha256']);pin(b/'artifacts/xemu-candidate.exe',r['xemu_sha256'])
for name,digest in r['source_pins'].items():pin(k/'artifacts/source/hw/xbox/nv2a'/name,digest)
pin(ws/'outputs/native-windows-physical-f/xemu-nv2a-resource-model.patch',r['resource_patch_sha256'])
pin(b/'cpu-surface-evict.patch',r['evict_patch_sha256'])
pin(ws/'outputs/video-gpu-transfer-contract212/artifacts/nxdk/lib/pbkit/pbkit.c',r['pbkit_reference_sha256'])
pin(ws/'outputs/video-gpu-state214/state-observations.json',r['observations_sha256'])
pin(k/'model-values.h',r['model_values_sha256'])
header=(k/'artifacts/source/hw/xbox/nv2a/nv2a_regs.h').read_text()
def constant(name):
 m=re.search(r'^#\s*define '+name+r'\s+(0x[0-9A-Fa-f]+|\d+)\b',header,re.M);assert m,name;return int(m.group(1),0)
for name,v in r['constants'].items():assert constant(name)==v,name
assert [constant(n) for n in ['NV062_SET_CONTEXT_DMA_IMAGE_SOURCE','NV062_SET_CONTEXT_DMA_IMAGE_DESTIN']]==[0x184,0x188]
assert [constant(n) for n in ['NV062_SET_COLOR_FORMAT','NV062_SET_PITCH','NV062_SET_OFFSET_SOURCE','NV062_SET_OFFSET_DESTIN']]==[0x300,0x304,0x308,0x30c]
assert [constant(n) for n in ['NV09F_SET_OPERATION','NV09F_CONTROL_POINT_IN','NV09F_CONTROL_POINT_OUT','NV09F_SIZE']]==[0x2fc,0x300,0x304,0x308]
gap=read(k/'host001-review.json');pin(k/'host001.json',gap['host001_sha256'])
for name,digest in gap['source_pins'].items():pin(k/'prior-host001'/name,digest)
for name in ['host001','host002']:
 h=read(k/(name+'.json'));assert h['passed'] and h['host_only'] and not h['guest_launch'] and not h['physical_access']
 pin(k/'run-host.py',h['source_sha256']);pin(Path(h['compiler_path']),h['compiler_sha256'])
 for n,digest in h['source_pins'].items():
  pin(k/'artifacts'/name/n,digest)
  pin((k/'prior-host001'/n) if name=='host001' and n!='model-values.h' else k/n,digest)
 for row in h['runs']:
  pin(Path(row['command'][-1]),row['binary_sha256'])
  assert row['compile_exit']==0 and row['exit_code']==0 and not row['compile_stderr'] and not row['stderr']
  assert 'pixel_cases=1024 descriptor_cases=100000 accepted=12513 transition_cases=144 quarantine_terminal=1' in row['stdout']
 assert len(h['runs'])==2
current=(k/'protocol.c').read_text();old=(k/'prior-host001/protocol.c').read_text()
expected=old.replace('int x215_prepare(X215Context *c,uint32_t generation','int x215_prepare(X215Context *c,const X215Plan *p,uint32_t generation')
expected=expected.replace('if(!c || c->state!=X215_EMPTY || !generation || !budget','if(!c || !p || c->state!=X215_EMPTY || p->packet_bytes!=108 || p->words[25]!=0x41d70 || p->words[26]!=generation || !generation || !budget')
assert current==expected
assert all(s not in current for s in ['WRITE_REGISTER','READ_REGISTER','MmAllocate','MmFree','VideoPort','while(1)'])
assert 'c->state=X215_QUARANTINED' in current and 'c->state!=X215_PREPARED && c->state!=X215_DRAINED' in current
assert [read(ws/'outputs/video-gpu-state214'/('emu-'+n)/'closure.json')['closed'] for n in ['control001','candidate001']]==[True,True]
out=dict(passed=True,source_sha256=sha(Path(__file__)),checked_pins=checked,
 current_source_pins={n:sha(k/n) for n in ['protocol.h','protocol.c','test.c','model-values.h','run-host.py','inventory.py']},
 host_only=True,packet_words=27,packet_bytes=108,pixel_cases=1024,descriptor_cases=100000,transition_table_cases=144,
 accepted_descriptors=12513,checks_per_current_run=18342825,earlier_token_binding_gap_preserved=True,
 guest_launch=False,physical_access=False,native_abi_qualified=False,gpu_transfer_qualified=False,
 manual_review=['Planner limits four disjoint page-aligned resident ranges below known framebuffer reservation;16-byte guards and64-bit span checks.',
  'Seven single-slot RAMHT entries reject collisions/hash overflow and bound16-byte objects; synthetic locations only.',
  '27 increasing words bind Kelvin only on subchannel0, use A8R8G8B8/SRCCOPY, release token last.',
  'Current prepare binds final header,length/token to generation; caller must keep packet immutable and global generations unique/no wrap.',
  'Complete is not drain; foreign callbacks reject, stale token/fault/clock regression/timeout quarantine; late completion cannot release quarantine.',
  'State calls require external serialization and real resident/instance/context/address/order/clear/drain evidence. Flags in tests are mock witnesses.',
  'No MMIO, allocator, native adapter, context switch handler, crash drain or asynchronous runtime integration exists in this kit.'],
 limits='Source and host contract checks only. CPU decoder models a selected command subset, not real QEMU execution or GPU/hardware timing. No authority or permission to submit from these results.')
dest.write_text(json.dumps(out,indent=2)+'\n');print('Protocol215 source/evidence pins PASS:',checked)
