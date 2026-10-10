"""Fresh source-consumer inventory; no old case replay or source modification."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
dest=k/'inventory001.json';assert not dest.exists()
b=ws/'outputs/xemu-cpu-surface-evict/build003'
pins=read(b/'candidate-source-pins.json')
src=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
root=k/'artifacts/source';root.mkdir(parents=True,exist_ok=False)
names=['pgraph/gl/renderer.c','pgraph/gl/display.c','pgraph/vk/renderer.c','pgraph/vk/draw.c','pgraph/vk/renderer.h']
original={}
for n in names:
 rel='hw/xbox/nv2a/'+n;p=src/rel;assert sha(p)==pins[rel],rel
 q=root/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());original[rel]=sha(q)
old=ws/'outputs/video-transfer-protocol215/artifacts/source/hw/xbox/nv2a'
derived={}
for n in ['nv2a.c','nv2a_int.h','nv2a_regs.h','pfifo.c','pgraph/pgraph.c','pgraph/gl/surface.c','pgraph/vk/surface.c']:
 rel='hw/xbox/nv2a/'+n;p=old/n;assert sha(p)==pins[rel],rel
 q=root/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());derived[rel]=sha(q)
texts={p.relative_to(root).as_posix():p.read_text() for p in root.rglob('*') if p.is_file()}
hits={name:[{'file':n,'line':i,'text':s.strip()} for n,t in texts.items() for i,s in enumerate(t.splitlines(),1) if name in s] for name in ['NV_PFIFO_RAMFC','NV_PFIFO_RAMRO','fifo_idle_cond','pre_shutdown','flush_complete']}
assert all(x['file'].endswith('nv2a_regs.h') for n in ['NV_PFIFO_RAMFC','NV_PFIFO_RAMRO'] for x in hits[n])
gl=texts['hw/xbox/nv2a/pgraph/gl/renderer.c'];surface=texts['hw/xbox/nv2a/pgraph/gl/surface.c']
assert 'qemu_event_wait(&r->shader_cache_writeback_complete)' in gl
assert '// pgraph_gl_surface_download_if_dirty(d, s);' in surface
assert 'Both the pusher and puller are waiting for some action' in texts['hw/xbox/nv2a/pfifo.c']
e=read(ws/'outputs/video-loader-handoff225/evidence-review.json');assert e['passed']
state=e['states'][-1];assert state['ramht']['valid_entries'] and state['pfifo_channel']==1
r=dict(passed=True,source_sha256=sha(Path(__file__)),compiled_manifest_sha256=sha(b/'candidate-source-pins.json'),
 xemu_sha256=sha(b/'artifacts/xemu-candidate.exe'),revision='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d',
 unchanged_original_sources=original,prior_reconstructed_candidate_sources=derived,consumer_hits=hits,
 prior225_evidence_sha256=sha(ws/'outputs/video-loader-handoff225/evidence-review.json'),
 old_ramht=dict(start=65536,bytes=4096,valid_entries=22,fully_captured=True),
 retained_old_aperture=dict(start=65536,bytes=20480,whole_range_protected=True,free_space_claim=False),
 ramfc=dict(raw=8978704,base1_field=(8978704&0x1fc)>>2,base2_field=(8978704&0xfe0000)>>17,size_field=(8978704&0x10000)>>16,extent_verified=False),
 ramro=dict(raw=0,extent_verified=False),
 plan_allowed=False,reasons=['RAMFC/RAMRO extent/backing and old backend references unresolved.','No guest/loader ownership receipts or native adapter.'],
 findings=['FIFO idle broadcast means worker waiting; stalled context/access can still have unconsumed DMA.',
 'OpenGL shutdown waits shader cache only; Vulkan shutdown trigger/wait are no-ops.',
 'OpenGL surface flush invalidates surfaces; all-dirty download is commented out.',
 'Flush completion event does not by itself establish queue consumption or old-reference retirement.',
 'RAMFC/RAMRO have no consumers beyond definitions in the examined matched model files; physical structures remain required.',
 'Context IRQ acknowledge clears waiting; valid own-channel context must be installed/verified before acknowledge.'],
 guest_launch=False,physical_access=False,gpu_ownership_qualified=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('226 matched source-consumer inventory PASS; actual ownership plan REFUSED')
