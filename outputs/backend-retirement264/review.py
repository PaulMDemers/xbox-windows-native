"""Derive remaining references from CLOSED 263 evidence, without recollection."""
import collections
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRACE = ROOT / 'outputs/surface-pending263/emu001/trace.json'
FAMILIES = ('surface', 'texture', 'palette', 'cached_vertex', 'scanout',
            'overlay', 'cpu_callback')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def parse(report, stage, arena):
    # Use the actual quoted HMP value, never its echoed command or older slots.
    values = [json.loads(line) for line in report.splitlines()
              if line.startswith('"version=260 ') and line.endswith('"')]
    assert len(values) == 1, 'ambiguous/missing terminal report'
    tokens = values[0].split()
    fields = {}
    for token in tokens:
        key, value = token.split('=', 1)
        assert key not in fields, 'duplicate field'
        fields[key] = value
    prefix = f'slot{stage}_'
    for name, expected in [('state', '5'), ('reason', '0'), ('result', '0'),
                           ('callback_result', '0'), ('pending_mask', '0'),
                           ('unknown_vertex', '0'), ('cpu0_done', '1'),
                           ('cpu1_done', '1'), ('cpu0_reason', '0'),
                           ('cpu1_reason', '0')]:
        assert fields[prefix + name] == expected, name
    count = int(fields[prefix + 'refs'])
    assert 0 <= count <= 1024
    rows = []
    seen = set()
    names = {k for k in fields if k.startswith(f's{stage}_ref')}
    assert names == {f's{stage}_ref{i}' for i in range(count)}, 'missing/extra refs'
    for i in range(count):
        f, identity, begin, length = map(int, fields[f's{stage}_ref{i}'].split(':'))
        assert 0 <= f < len(FAMILIES), 'unknown family'
        assert identity > 0 and begin >= 0 and length > 0
        assert begin + length <= 64 * 1024 * 1024, 'outside actual 64MiB fixture'
        assert (f, identity) not in seen, 'duplicate owner within family'
        seen.add((f, identity))
        assert begin + length <= arena or begin >= arena + 16384, 'test-arena overlap'
        rows.append(dict(index=i, family=FAMILIES[f], identity=identity,
                         begin=begin, length=length, end=begin + length))
    return rows

def negative_controls(checkpoint):
    raw, stage = checkpoint['renderer_report'], checkpoint['stage']
    arena = checkpoint['attestation']['physical']
    cases = {}
    key = f's{stage}_ref0='
    value = re.search(key + r'([0-9:]+)', raw).group(1)
    cases['missing_reference'] = raw.replace(key + value, '', 1)
    cases['duplicate_reference'] = raw.replace(key + value, key + value + ' ' + key + value, 1)
    cases['unknown_family'] = raw.replace(key + value, key + '9:' + value.split(':', 1)[1], 1)
    identity = value.split(':')[1]
    cases['test_arena_overlap'] = raw.replace(key + value, key + f'1:{identity}:{arena}:1', 1)
    cases['out_of_ram'] = raw.replace(key + value, key + f'1:{identity}:67108864:1', 1)
    cases['zero_length'] = raw.replace(key + value, key + f'1:{identity}:0:0', 1)
    for field, old, new in [('state','5','6'), ('pending_mask','0','1'),
                            ('unknown_vertex','0','1'), ('cpu1_done','1','0')]:
        cases[field] = raw.replace(f'slot{stage}_{field}={old}',
                                  f'slot{stage}_{field}={new}', 1)
    rejected = []
    for name, changed in cases.items():
        assert changed != raw
        try:
            parse(changed, stage, arena)
        except (AssertionError, KeyError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError('accepted negative control: ' + name)
    return rejected

def main():
    verified = []
    for manifest in ['source-review.json', 'source-review002.json']:
        data = json.loads((HERE / manifest).read_text(encoding='utf-8'))
        pins_path = Path(data['source_pin_manifest'])
        assert digest(pins_path.read_bytes()) == data['source_pin_manifest_sha256']
        pins = json.loads(pins_path.read_text(encoding='utf-8'))
        for row in data['files']:
            path = Path(data['destination']) / row['path']
            assert digest(path.read_bytes()) == row['sha256'] == pins[row['path']]
            verified.append(row['path'])
    trace = json.loads(TRACE.read_text(encoding='utf-8'))
    assert trace['closed'] and trace['passed'] and not trace['native_gpu_ownership']
    assert trace['remaining_breakpoints'] == 0 and trace['physical_mode_restored']
    stages = []
    for checkpoint in trace['checkpoints'][:4]:
        rows = parse(checkpoint['renderer_report'], checkpoint['stage'],
                     checkpoint['attestation']['physical'])
        counts = collections.Counter(r['family'] for r in rows)
        assert counts == dict(texture=24, cached_vertex=93, scanout=1)
        stages.append(dict(stage=checkpoint['stage'], counts=dict(counts),
                           references=rows, negative_controls=negative_controls(checkpoint)))
    # Compare owners and byte spans, not order in the LRU.
    canonical = lambda s: sorted((r['family'], r['identity'], r['begin'], r['length'])
                                for r in s['references'])
    unchanged = all(canonical(s) == canonical(stages[0]) for s in stages[1:])
    out = dict(schema=1, scope='new analysis of closed263 evidence; no new guest run',
               source_files_verified=verified, trace=str(TRACE), trace_sha256=digest(TRACE.read_bytes()),
               stages=stages, same_reference_sets_all_stages=unchanged,
               old_backend_retirement_proved=False, native_gpu_grant=False,
               strict_qualification_passed=False,
               limitations=['Seven guest-memory reference families are not a complete GL object/actor inventory.',
                            'Texture unit-to-binding relationships and refcounts were not captured by these rows.',
                            'Scanout row is a conservative tail reservation, not a measured fetch length.',
                            'Renderer cleanup, guest PTE aliases and physical GPU handoff remain separate.'])
    with (HERE / 'inventory-review.json').open('x', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(source_files=len(verified), stages=len(stages),
                         references_per_stage=len(stages[0]['references']),
                         same_reference_sets=unchanged,
                         rejected_mutations=sum(len(s['negative_controls']) for s in stages))))

if __name__ == '__main__':
    main()
