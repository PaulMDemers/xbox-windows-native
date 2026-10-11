"""Read-only sector comparison for the traced file and metadata ranges."""
import hashlib, importlib, json, sys
from pathlib import Path

k = Path(__file__).resolve().parent
case = sys.argv[1]
assert case in ['emu001','emu002']
run = k.parents[1] / ('work/runs/nt5setup-' + case)
assert (run / 'cleanup.json').exists()
canon = Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0] = [str(canon/'outputs/native-windows-paint-save'), str(canon/'outputs/fatx-mapped-eof')]
from coldio import ColdIO
m = importlib.import_module('prepare-fixture')
stage = json.loads((run/'stage.json').read_text())
f = json.loads((k/case/'forensics.json').read_text())
sectors = {}
for name, row in f['files'].items():
    if row.get('absent'):continue
    for c in row['chain']:
        for at in range(c['byte_offset'], c['byte_offset'] + ((row['length']+511)//512)*512, 512):
            sectors.setdefault(at, []).append(name+':data')
        sectors.setdefault(c['fat_byte_offset']//512*512, []).append(name+':fat')
    sectors.setdefault(row['directory_byte_offset']//512*512, []).append(name+':directory')
sectors.setdefault(f['cim_rec']['fat_byte_offset']//512*512, []).append('CIM.REC:fat')
sha = lambda b: hashlib.sha256(b).hexdigest()
art=k/case/'artifacts/sectors';art.mkdir(parents=True,exist_ok=True)
out = []
with ColdIO(run/'hdd.qcow2') as new, ColdIO(Path(stage['parent_path'])) as old:
    independent = m.SliceIO(run/'hdd.qcow2')
    for at, labels in sorted(sectors.items()):
        new.seek(at); a = new.read(512)
        old.seek(at); b = old.read(512)
        independent.seek(at); assert a == independent.read(512)
        (art/(str(at)+'-before.bin')).write_bytes(b)
        (art/(str(at)+'-after.bin')).write_bytes(a)
        out.append(dict(offset=at, lba=at//512, labels=labels, before_sha256=sha(b),
                        after_sha256=sha(a), changed_bytes=sum(x!=y for x,y in zip(a,b)), independent_exact=True))
r = dict(case=case, physical_access=False, sectors=out,
         limits='Cold sector equality shows final bytes only, not transient data or request completion.')
(k/case/'sector-comparison.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(out,indent=2))
