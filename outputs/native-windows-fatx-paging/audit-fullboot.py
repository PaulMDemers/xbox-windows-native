"""Cold, read-only structural and immutable-file audit of a stopped test disk."""
import argparse, hashlib, json, os, pathlib, re, shutil, struct, subprocess, sys

p = argparse.ArgumentParser()
p.add_argument('--run', required=True)
p.add_argument('--driver-manifest', default='outputs/native-windows-fatx-paging/fatx-full-paging-disk-001.json')
p.add_argument('--pressure-manifest', help='Require the extra paging probe and all eight retention passes')
p.add_argument('--filesystem-manifest', help='Require the bounded file API probe and its complete success log')
p.add_argument('--registry-trees', action='store_true', help='Require read-only traversal of every reachable hive key/value')
a = p.parse_args()
assert re.fullmatch(r'nt5-fatx-boot-(?:paging|image-read|paging-flags|flush|power|wide|hal-paging|bootvid|bootvid-ram|pressure|metadata|name-boundary)-[0-9]+', a.run)
ws = pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
root = pathlib.Path('/home/paul/xbox-windows-native')
run = ws / 'work/runs' / a.run
source = run / 'hdd.qcow2'
assert (run / 'cleanup.json').is_file()
sys.path[:0] = [str(ws / 'outputs/native-windows-fatx-runtime'), '/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer

def sha(path):
    with path.open('rb') as fp:
        return hashlib.file_digest(fp, 'sha256').hexdigest()

temp = root / 'fixtures' / ('audit-' + a.run)
assert not temp.exists()
temp.mkdir()
r = {'scope': 'Cold read-only emulator disk audit; no physical access', 'source_sha256': sha(source),
     'directories': 0, 'files': 0, 'allocated_clusters': 0, 'immutable_files_checked': 0,
     'structural_errors': [], 'immutable_mismatches': [], 'registry_headers': []}
try:
    raw = temp / 'disk.raw'
    subprocess.run(['qemu-img', 'convert', '-O', 'raw', str(source), str(raw)], check=True)
    baseline = json.loads((ws / 'outputs/native-windows-fatx-runtime/fatx-boot-disk-001.json').read_text())
    expected = {item['path'].lower(): item for item in baseline['files']}
    driver = json.loads((ws / a.driver_manifest).read_text())['driver_sha256']
    expected['/winnt/system32/drivers/xwnfatx.sys'] = {'sha256': driver}
    extensions = {'.exe', '.dll', '.sys', '.nls', '.fon', '.ttf', '.cpl', '.ocx'}
    with raw.open('rb') as fp:
        w = Writer(fp, fatx.open_partition(fp, raw, 'E'))
        owners = {}
        found = set()
        def claim(start, path):
            chain = list(w.chain(start))
            for c in chain:
                if c in owners:
                    raise ValueError('Cross-linked cluster %x: %s and %s' % (c, owners[c], path))
                owners[c] = path
            return chain
        def walk(start, path):
            try:
                claim(start, path)
                entries = w.directory(start)['entries']
            except Exception as ex:
                r['structural_errors'].append({'path': path, 'error': repr(ex)})
                return
            r['directories'] += 1
            for name, (_, _, entry) in entries.items():
                full = path.rstrip('/') + '/' + name
                cluster, size = struct.unpack_from('<II', entry, 44)
                if entry[1] & 16:
                    walk(cluster, full)
                    continue
                r['files'] += 1
                found.add(full)
                try:
                    chain = claim(cluster, full) if cluster else []
                    if len(chain) * w.p.cluster_size < size:
                        raise ValueError('File exceeds allocated chain')
                    if full == '/pagefile.sys':
                        r['paging_file'] = {'bytes': size, 'clusters': len(chain),
                            'first_cluster': cluster,
                            'physical_runs': 1 + sum(y != x + 1 for x, y in zip(chain, chain[1:])) if chain else 0}
                    if full in expected and pathlib.PurePosixPath(full).suffix in extensions:
                        actual = hashlib.sha256(w.read(full)).hexdigest()
                        r['immutable_files_checked'] += 1
                        if actual != expected[full]['sha256']:
                            r['immutable_mismatches'].append({'path': full, 'sha256': actual,
                                'expected_sha256': expected[full]['sha256']})
                except Exception as ex:
                    r['structural_errors'].append({'path': full, 'error': repr(ex)})
        walk(1, '/')
        r['allocated_clusters'] = len(owners)
        # Header consistency is separate from a full registry-tree audit and
        # does not prove that the guest completed shutdown. A sequence mismatch
        # can require log replay after a host-stopped run.
        hive_paths = {'/winnt/system32/config/' + name
                      for name in ('system', 'software', 'sam', 'security', 'default')}
        hive_paths.update(path for path in found if pathlib.PurePosixPath(path).name in ('ntuser.dat', 'usrclass.dat'))
        for path in sorted(hive_paths):
            item = {'path': path}
            try:
                data = w.read(path)
                assert len(data) >= 4096 and data[:4] == b'regf'
                first, second = struct.unpack_from('<II', data, 4)
                bins = struct.unpack_from('<I', data, 40)[0]
                assert bins % 4096 == 0 and bins + 4096 <= len(data)
                checksum = 0
                for word in struct.unpack_from('<127I', data):
                    checksum ^= word
                if checksum == 0xffffffff:
                    checksum = 0xfffffffe
                if checksum == 0:
                    checksum = 1
                stored = struct.unpack_from('<I', data, 508)[0]
                item.update(bytes=len(data), sequence1=first, sequence2=second,
                            sequences_match=first == second,
                            checksum_matches=stored == checksum)
                if a.registry_trees:
                    copy = temp / 'hive-audit-copy'
                    copy.write_bytes(data)
                    env = dict(os.environ, LD_LIBRARY_PATH=str(root / 'toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu'))
                    item['tree'] = json.loads(subprocess.check_output(
                        [sys.executable, str(pathlib.Path(__file__).with_name('audit-hive.py')), str(copy)], env=env))
                    copy.unlink()
            except Exception as ex:
                item['error'] = repr(ex)
            r['registry_headers'].append(item)
        logs = run / 'guest-logs'
        logs.mkdir(exist_ok=True)
        try:
            log = w.read('/xwn-check.log')
            (logs / 'xwn-check.log').write_bytes(log)
            text = log.decode('ascii')
            r['endurance'] = {'bytes': len(log), 'sha256': hashlib.sha256(log).hexdigest(),
                'passed': all(s in text for s in [
                    '4 MiB write/flush/reopen/read comparison passed',
                    'GUI response passed', 'Memory pass: 20',
                    '8 MiB memory retention passed across 20 intervals', 'Failures: 0'])}
        except Exception as ex:
            r['endurance'] = {'passed': False, 'error': repr(ex)}
        if a.pressure_manifest:
            try:
                manifest = json.loads((ws / a.pressure_manifest).read_text())
                probe = next(f for f in manifest['files'] if f['path'].lower() == '/xwnpaging.exe')
                probe_hash = hashlib.sha256(w.read('/xwnpaging.exe')).hexdigest()
                log = w.read('/xwn-paging.log')
                (logs / 'xwn-paging.log').write_bytes(log)
                text = log.decode('ascii')
                passes = re.findall(r'^Pass: ([0-9]+)\r?$', text, re.M)
                comparisons = text.count('40 MiB comparison passed')
                failures = re.findall(r'^Failures: ([0-9]+)\r?$', text, re.M)
                r['paging_pressure'] = {
                    'scope': 'Retention under working-set trimming; fault counts alone do not prove disk page-ins',
                    'probe_sha256': probe_hash, 'log_sha256': hashlib.sha256(log).hexdigest(),
                    'passes': passes, 'comparisons': comparisons, 'failures': failures,
                    'passed': probe_hash == probe['sha256'] and passes == [str(i) for i in range(1, 9)]
                              and comparisons == 8 and failures == ['0']}
            except Exception as ex:
                r['paging_pressure'] = {'passed': False, 'error': repr(ex)}
        if 'xwn-fragment-guard.bin' in w.directory(1)['entries']:
            guard = json.loads((ws / 'outputs/native-windows-fatx-paging/fatx-fragmented-paging-disk-001.json').read_text())['guard_file']
            actual = hashlib.sha256(w.read(guard['path'])).hexdigest()
            r['fragment_guard'] = {'sha256': actual, 'passed': actual == guard['sha256']}
        if a.filesystem_manifest:
            try:
                manifest = json.loads((ws / a.filesystem_manifest).read_text())
                probe = next(f for f in manifest['files'] if f['path'].lower() == '/xwnfs.exe')
                probe_hash = hashlib.sha256(w.read('/xwnfs.exe')).hexdigest()
                log = w.read('/xwn-fs.log'); text = log.decode('ascii')
                (logs / 'xwn-fs.log').write_bytes(log)
                names = ['42-byte ASCII name accepted', '43-byte ASCII name rejected',
                         'Case-insensitive reopen', 'Reopened full data comparison',
                         'Shrink at cluster-crossing boundary', 'Shrunk size',
                         'Regrow with explicit data', 'Rename across directories',
                         'Renamed regrown data comparison', 'Remove test directory',
                         '42-byte component limit advertised', 'OEM case-preserved capabilities']
                checks = {name: 'PASS: ' + name + '\r\n' in text for name in names}
                directory_removed = 'xwnfstest' not in w.directory(1)['entries']
                r['filesystem_api'] = {'probe_sha256': probe_hash,
                    'log_sha256': hashlib.sha256(log).hexdigest(), 'checks': checks,
                    'test_directory_removed': directory_removed,
                    'passed': probe_hash == probe['sha256'] and all(checks.values())
                              and 'FAIL:' not in text and 'Failures: 0\r\n' in text and directory_removed}
            except Exception as ex:
                r['filesystem_api'] = {'passed': False, 'error': repr(ex)}
        for path, item in expected.items():
            if pathlib.PurePosixPath(path).suffix in extensions and path not in found:
                r['immutable_mismatches'].append({'path': path, 'error': 'Missing file'})
    assert sha(source) == r['source_sha256']
    r['source_preserved'] = True
    r['passed'] = (not r['structural_errors'] and not r['immutable_mismatches']
                   and r['endurance']['passed'] and r.get('fragment_guard', {'passed': True})['passed']
                   and r.get('paging_pressure', {'passed': True})['passed'])
    r['passed'] = r['passed'] and r.get('filesystem_api', {'passed': True})['passed']
    if a.registry_trees:
        r['passed'] = r['passed'] and bool(r['registry_headers']) and all(
            h.get('tree', {}).get('passed', False) for h in r['registry_headers'])
finally:
    assert temp.resolve().parent == (root / 'fixtures').resolve()
    shutil.rmtree(temp)
    r['temporary_raw_removed'] = True
    (run / 'cold-integrity.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
