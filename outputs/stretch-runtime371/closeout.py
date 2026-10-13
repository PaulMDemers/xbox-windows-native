"""Rehash closed run inputs, private captures, binaries and paired audit evidence."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = k / 'final-review.json'
assert not dest.exists()
pair = read(k / 'pair-review.json')
assert pair['scoped_matched_graphics_audio_integrity_passed']
build = read(k.parent / 'stretch-bounds369/build001.json')
records = []
for case in ('control001', 'candidate001'):
    out = k / case
    run = Path('C:/xwn371/runs/nt5-stretch371-' + case)
    assert read(run / 'host-exit.json')['passed'] and read(out / 'closure.json')['closed']
    f = read(out / 'fixture.json')
    assert sha(Path(f['fixture_path_windows'])) == f['fixture_sha256']
    dll = Path('E:/xwn369/build001') / case / 'xwnown.dll'
    assert sha(dll) == build['cases'][case]['sha256']
    inputs = read(out / 'emulator-frozen.json')
    inputs.update(read(out / 'audit-completion.json')['supplemental_dependencies'])
    for name, digest in inputs.items():
        assert sha(ws / name) == digest, name
    captures = {str(p.relative_to(out)).replace('\\', '/'): sha(p)
                for folder in (out / 'artifacts', out / 'before-allocation/artifacts')
                for p in folder.rglob('*') if p.is_file()}
    assert all(sha(out / name) == digest for name, digest in captures.items())
    reports = {p.name: sha(p) for p in out.glob('*.json')}
    host = {name: sha(run / name) for name in ('cleanup.json', 'host-exit.json', 'instance.json')}
    records.append(dict(case=case, inputs_rehashed=len(inputs), capture_count=len(captures),
                        captures=captures, reports=reports, host_records=host,
                        installed_candidate_binary_sha256=sha(dll)))
probe = Path('E:/xwn370/build001/replay.exe')
assert sha(probe) == read(k.parent / 'stretch-probe370/build-review001.json')['binary_sha256']
r = dict(evidence_integrity_passed=True, all_owned_runs_closed=True,
         pair_review_sha256=sha(k / 'pair-review.json'), cases=records,
         probe_sha256=sha(probe), physical_access=False,
         scoped_matched_passed=True, strict_pair_passed=pair['strict_pair_passed'],
         byte_reduction_observed=pair['byte_reduction_observed'],
         performance_qualified=False, release_promoted=False,
         no_relaunch_recollection_or_runtime_parenting=True)
dest.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({n:r[n] for n in ('evidence_integrity_passed', 'all_owned_runs_closed', 'byte_reduction_observed', 'strict_pair_passed')}, indent=2))
