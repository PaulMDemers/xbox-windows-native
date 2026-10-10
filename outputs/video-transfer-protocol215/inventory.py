"""Reconstruct private copies of actual compiled sources; no borrowed-source edit."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'inventory.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=ws/'outputs/xemu-cpu-surface-evict/build003';build=read(b/'build.json');manifest=read(b/'candidate-source-pins.json')
row=next(r for r in build['builds'] if r['case']=='candidate')
assert sha(b/'candidate-source-pins.json')==row['source_manifest_sha256']
assert sha(b/'artifacts/xemu-candidate.exe')==row['sha256']
src=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
root=k/'artifacts/source';root.mkdir(parents=True,exist_ok=False);base=root/'hw/xbox/nv2a'
names=['nv2a.c','nv2a_int.h','nv2a_regs.h','pfifo.c','user.c','pgraph/pgraph.c','pgraph/pgraph.h',
 'pgraph/methods.h.inc','pgraph/gl/blit.c','pgraph/gl/surface.c','pgraph/gl/renderer.h',
 'pgraph/vk/blit.c','pgraph/vk/surface.c']
originals={}
for n in names:
 rel='hw/xbox/nv2a/'+n;p=src/rel;expected=build['original_sources'].get(rel,manifest[rel]);assert sha(p)==expected,rel
 q=base/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());originals[n]=sha(p)
resource=ws/'outputs/native-windows-physical-f/xemu-nv2a-resource-model.patch'
evict=b/'cpu-surface-evict.patch'
assert sha(resource)==build['resource_patch_sha256'] and sha(evict)==build['patch_sha256']
for patch in [resource,evict]:
 subprocess.run(['patch','--batch','--forward','-p1','-i',str(patch)],cwd=root,check=True,stdout=subprocess.DEVNULL)
pins={}
for n in names:
 assert sha(base/n)==manifest['hw/xbox/nv2a/'+n],n;pins[n]=sha(base/n)
texts={n:(base/n).read_text() for n in names}
assert 'assert(!"Failed to enter DMA mode - entered PIO mode")' in texts['user.c']
assert 'case NV_MEMORY_TO_MEMORY_FORMAT:' not in texts['pgraph/pgraph.c']
assert 'case NV_IMAGE_BLIT:' in texts['pgraph/pgraph.c']
assert 'pg->waiting_for_context_switch = true;' in texts['pgraph/pgraph.c']
assert 'dma.address &= 0x07FFFFFF;' in texts['nv2a.c'] and '*len = dma.limit;' in texts['nv2a.c']
assert 'TODO: Handle targets and classes properly' in texts['nv2a.c']
assert 'assert(subchannel < 8);' in texts['pgraph/pgraph.c']
assert 'assert(graphics_class != 0x97);' in texts['pgraph/pgraph.c']
assert 'assert(hash * 8 < ramht_size);' in texts['pfifo.c']
for n in ['pgraph/gl/blit.c','pgraph/vk/blit.c']:
 assert 'memmove(dest, source, width_bytes)' in texts[n]
 assert 'NV062_SET_COLOR_FORMAT_LE_A8R8G8B8' in texts[n] and 'patch_alpha(' in texts[n]
start=texts['pgraph/pgraph.c'].index('DEF_METHOD(NV097, BACK_END_WRITE_SEMAPHORE_RELEASE)')
end=texts['pgraph/pgraph.c'].index('\n}',start)+2
body=texts['pgraph/pgraph.c'][start:end]
assert body.index('surface_update(d, false, true, true)')<body.index('stl_le_p((uint32_t*)semaphore_data, parameter)')
symbols=['NV_DMA_FROM_MEMORY_CLASS','NV_DMA_TO_MEMORY_CLASS','NV_DMA_IN_MEMORY_CLASS',
 'NV_CONTEXT_SURFACES_2D','NV_IMAGE_BLIT','NV_KELVIN_PRIMITIVE','NV062_SET_CONTEXT_DMA_IMAGE_SOURCE',
 'NV062_SET_COLOR_FORMAT','NV062_SET_COLOR_FORMAT_LE_A8R8G8B8','NV09F_SET_CONTEXT_SURFACES',
 'NV09F_SET_OPERATION','NV09F_SET_OPERATION_SRCCOPY','NV097_SET_CONTEXT_DMA_SEMAPHORE',
 'NV097_SET_SEMAPHORE_OFFSET','NV097_BACK_END_WRITE_SEMAPHORE_RELEASE']
constants={}
for name in symbols:
 m=re.search(r'^#\s*define '+name+r'\s+(0x[0-9A-Fa-f]+|\d+)\b',texts['nv2a_regs.h'],re.M);assert m,name
 constants[name]=int(m.group(1),0)
header='/* Numeric protocol constants from exact compiled model; see inventory.json. */\n#ifndef X215_MODEL_VALUES_H\n#define X215_MODEL_VALUES_H\n'
header+=''.join('#define %s 0x%xu\n'%(n,v) for n,v in constants.items())+'#endif\n'
(k/'model-values.h').write_text(header)
pb=ws/'outputs/video-gpu-transfer-contract212/artifacts/nxdk/lib/pbkit/pbkit.c'
assert sha(pb)==read(ws/'outputs/video-gpu-transfer-contract212/binary-inventory.json')['nxdk_sources']['lib/pbkit/pbkit.c']
observations=read(ws/'outputs/video-gpu-state214/state-observations.json')
assert observations['passed'] and not observations['gpu_ownership_proven']
ramht=0x03000100;table=((ramht&0x1f0)>>4)<<12;size=1<<(((ramht&0x30000)>>16)+12)
assert (table,size)==(0x10000,0x1000)
r=dict(passed=True,source_sha256=sha(Path(__file__)),source_revision=build['source_revision'],
 xemu_sha256=row['sha256'],source_manifest_sha256=sha(b/'candidate-source-pins.json'),
 source_pins=pins,original_source_pins=originals,resource_patch_sha256=sha(resource),evict_patch_sha256=sha(evict),
 pbkit_reference_sha256=sha(pb),model_values_sha256=sha(k/'model-values.h'),constants=constants,
 observations_sha256=sha(ws/'outputs/video-gpu-state214/state-observations.json'),
 observed_ramht=dict(register=ramht,base=table,bytes=size,search_field=3),
 source_findings=['USER PIO and different current channel assert; DMA path only.',
  'Class39 is defined but no PGRAPH case; implemented62+9f blit.',
  'RAMHT single hashed slot, no implemented collision search/handle equality check in puller.',
  'nv_dma_map masks addresses to27 bits, ignores targets/classes, returns limit without plus1.',
  'Blit models perform row copies and optional alpha rewriting, not GPU timing.',
  'Kelvin97 restricted to subchannel0; semaphore release follows surface_update then32-bit store.',
  'Context mismatch stalls awaiting interrupt handling; hardware context switch asserts.',
  'Control mapping681000 excludes PRAMIN700000 and USER800000; additional mapping/ownership unresolved.'],
 guest_launch=False,physical_access=False,gpu_transfer_qualified=False,
 limits='Actual compiled source matches reconstructed privately. Source behavior does not prove physical addressing, engine ownership, completion visibility or crash drain. No model/driver/config changes.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Exact compiled protocol source pins PASS:',len(pins))
