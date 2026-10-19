"""MIT. Read only the uncollected tail of the still-open physical565 run."""
import copy
import importlib.util
import json
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('candidate565', K / 'controller004.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
m = c.m


def main():
    assert not (K / 'final001.json').exists(), 'Runtime already closed'
    supervisor = c.read(K / 'supervisor004-collect.json')
    previous = c.read(K / 'collection001.json')
    assert supervisor['closed'] and supervisor['deadline_reached']
    assert not supervisor['completed'] and not previous['completed']
    assert previous['hook_removed'] and previous['protected_code_exact']
    q = c.verify()
    c.budget()
    stage = c.read(K / 'stage004.json')
    out = K / 'collection002.json'
    assert not out.exists()
    for row in previous['files'].values():
        p = Path(row['path'])
        assert p.stat().st_size == row['bytes'] and m.sha(p.read_bytes()) == row['sha256']
    paths = list(dict.fromkeys(c.FILES + list(stage['staged']) + list(previous['game_rows'])
                 + [c.USED] + c.result_names(previous['result_directory'])
                 + ['/E/winnt/system32/' + n for n in q['runtime_module_pins']]))
    remaining = [n for n in paths if n not in previous['files']]
    assert 0 < len(remaining) <= 40, 'Unexpected remaining scope'
    r = copy.deepcopy(previous)
    r.update(utc=m.utc(), original_collection_utc=previous['utc'],
             partial_collection_sha256=m.sha((K / 'collection001.json').read_bytes()),
             failed_supervisor_sha256=m.sha((K / 'supervisor004-collect.json').read_bytes()),
             source_sha256=m.sha(Path(__file__).read_bytes()),
             continuation_remote_writes=[], inherited_file_count=len(previous['files']),
             remaining_paths=remaining, new_collected_paths=[])
    m.write_json(out, r)
    with m.connect(timeout=15) as f:
        m.baseline(f, '720p')
        assert c.startup(f, False) == previous['startup_listing']
        assert m.get(f, c.HOOK, True) is None and m.get(f, c.USED) == c.hook()
        assert m.names(f, c.RESULT) == previous['result_directory']
        assert m.sha(m.get(f, c.KIT + '/owner.json')) == stage['staged'][c.KIT + '/owner.json']['sha256']
    for n in remaining:
        b = m.cold_pair(n, r, out)
        assert b is not None, n
        prior = stage['before'].get(n) or stage['staged'].get(n)
        if n.startswith(c.KIT + '/game/') and prior and m.sha(b) == prior['sha256']:
            original = q['files'][n[len(c.KIT) + 1:]]
            row = dict(path=original['path'], bytes=len(b), sha256=m.sha(b),
                       unchanged=True, identical_payload_retained_once=True)
        else:
            p = c.P / 'after' / n.lstrip('/')
            if p.exists():
                assert p.read_bytes() == b, 'Unjournaled retained file differs'
                row = dict(path=str(p), bytes=len(b), sha256=m.sha(b),
                           unjournaled_file_verified=True)
            else:
                row = m.keep(c.P / 'after', n, b)
        if prior:
            row['unchanged'] = row['sha256'] == prior['sha256']
        if n.startswith(c.RESULT + '/'):
            assert len(b) == previous['result_directory'][n.rsplit('/', 1)[1]]['bytes']
        r['files'][n] = row
        r['new_collected_paths'].append(n)
        m.write_json(out, r)
    assert set(r['files']) == set(paths)
    r.update(completed=True, ended_utc=m.utc(), normal_shutdown_proved=False, graphics_pass=False)
    m.write_json(out, r)
    print(json.dumps(dict(completed=True, inherited=len(previous['files']), newly_collected=len(remaining))))


if __name__ == '__main__':
    main()
