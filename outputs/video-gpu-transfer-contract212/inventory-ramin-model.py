"""Pin the actual built xemu source model; no hardware address inference."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'ramin-model.json'
assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=ws/'outputs/xemu-cpu-surface-evict/build003'
read=lambda p:json.loads(p.read_text())
build=read(b/'build.json');manifest=b/'candidate-source-pins.json'
row=next(r for r in build['builds'] if r['case']=='candidate')
assert sha(manifest)==row['source_manifest_sha256']
assert sha(b/'artifacts/xemu-candidate.exe')==row['sha256']
name='hw/xbox/nv2a/nv2a.c'
src=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')/name
assert sha(src)==read(manifest)[name]==build['original_sources'][name]
assert name not in build['changed_sources']
art=k/'artifacts/ramin-model';art.mkdir(parents=True,exist_ok=False)
p=art/'nv2a.c';p.write_bytes(src.read_bytes());assert sha(p)==sha(src)
text=p.read_text();start=text.index('static void nv2a_init_memory(')
end=text.index('\n}',start)+2;body=text[start:end]
assert 'memory_region_init_ram(&d->ramin' in body
assert '/* memory_region_init_alias(&d->ramin' in body
assert 'memory_region_add_subregion(&d->mmio, 0x700000, &d->ramin);' in body
lines=text[:start].count('\n')+1
r=dict(passed=True,source_sha256=sha(Path(__file__)),build_record_sha256=sha(b/'build.json'),
 source_manifest_sha256=sha(manifest),xemu_sha256=row['sha256'],source_revision=build['source_revision'],
 nv2a_sha256=sha(p),initialization_start_line=lines,initialization=body,
 separate_ramin_region=True,compiled_source_alias_to_vram=False,physical_alias_proven=False,
 guest_launch=False,physical_access=False,
 limits='Matched source manifest/build record/binary identity. The source uses separate RAMIN RAM; commented VRAM alias is not executed. This emulator model cannot itself establish physical RAMIN ownership or boot-buffer non-overlap. No model or driver changed.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Actual pinned xemu RAMIN source model: separate RAM region; physical alias NOT proven.')
