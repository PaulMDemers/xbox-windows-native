"""Review frozen inputs and closed diagnostic records before private publication."""
import ast, datetime, hashlib, json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = k / 'checkpoint-review.json'
assert not dest.exists()
counts = {}
for name in ['emulator-frozen.json', 'frozen002.json', 'frozen003.json']:
    pins = read(k / name)
    for p, digest in pins.items():
        assert sha(ws / p) == digest, p
    counts[name] = len(pins)
python_sources = sorted(k.glob('*.py'))
for p in python_sources:
    ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p))
pair = read(k / 'pair-verification003.json')
assert pair['passed'] and not pair['gpu_ownership_qualified'] and not pair['natural_TRUE_qualified']
cases = {}
for name in ['control003', 'candidate003']:
    h = read(k / name / 'host-state.json')
    a = read(k / name / 'audit.json')
    t = read(k / name / 'trace.json')
    assert h['closed'] and not h.get('still_running_pids')
    assert all(h[n] == 0 for n in ['runner_exit', 'tracer_exit', 'supervisor_exit', 'audit_exit'])
    assert a['cpu_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count'] == 1
    assert not a['strict_qualification_passed'] and not a['ordinary_qualified']
    assert t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints']
    cases[name] = dict(host_sha256=sha(k/name/'host-state.json'), audit_sha256=sha(k/name/'audit.json'),
                       trace_sha256=sha(k/name/'trace.json'), resident_provider_pins=len(t['pins']))
r = dict(passed=True, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), frozen_counts=counts,
         python_syntax_sources=len(python_sources), pair_sha256=sha(k/'pair-verification003.json'), cases=cases,
         report_sha256=sha(k/'REPORT.md'), next_sha256=sha(k/'NEXT.md'), native_changes=False,
         physical_access=False, strict_overall=False,
         reviewed=['Actual PE/caller/frame/mapping checks precede the two explicit BOOLEAN mutations and tail seed.',
                   'NIC-ready barrier precedes monitor lock acquisition; one recorded launch per fresh case.',
                   'Bounded trace removes breakpoints and resumes before cold audit; closed IDs guarded against reuse.',
                   'Independent byte comparison retains exact candidate preservation and explicit control destruction.',
                   '001 startup and002 trace coverage failures preserved; no altered frozen sources or waived event gates.',
                   'No new GPU context/DMA submission; existing reset/palette hardware accesses are not excluded.',
                   'Selected protected hashes and structural hives do not establish exhaustive file-content safety.'])
dest.write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(passed=r['passed'], frozen_counts=counts, python_sources=len(python_sources))))
