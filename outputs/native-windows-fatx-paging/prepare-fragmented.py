"""Create a fragmented paging-file test on a private emulator fixture."""
import hashlib, json, pathlib, shutil, struct, subprocess, sys
root = pathlib.Path('/home/paul/xbox-windows-native')
ws = pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out = ws / 'outputs/native-windows-fatx-paging'
sys.path[:0] = [str(ws / 'outputs/native-windows-fatx-runtime'), '/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source = out / 'artifacts/windows2000-fatx-full-paging-001.qcow2'
target = out / 'artifacts/windows2000-fatx-fragmented-paging-001.qcow2'
temp = root / 'fixtures/fatx-fragmented-paging-001'
assert not temp.exists() and not target.exists()
def sha(path):
    with path.open('rb') as fp:
        return hashlib.file_digest(fp, 'sha256').hexdigest()
r = {'scope': 'Private fragmented paging-file emulator fixture; no hardware access',
     'source_sha256': sha(source)}
assert r['source_sha256'] == '4f56a071d6548e5a71699a81a05d421b1b81ea8fa020c012a7f7bed31b346223'
temp.mkdir()
try:
    raw = temp / 'disk.raw'
    subprocess.run(['qemu-img', 'convert', '-O', 'raw', str(source), str(raw)], check=True)
    with raw.open('r+b') as fp:
        w = Writer(fp, fatx.open_partition(fp, raw, 'E'))
        assert 'pagefile.sys' not in w.directory(1)['entries']
        assert 'xwn-fragment-guard.bin' not in w.directory(1)['entries']
        count = 96 * 1024**2 // w.p.cluster_size
        assert w.p.cluster_size == 16384 and count % 16 == 0
        pages, guards = [], []
        for i in range(count // 16):
            pages.extend(w.allocate(16))
            guards.extend(w.allocate(1))
        pattern = bytes((i * 17 + 0x39) & 255 for i in range(w.p.cluster_size))
        for chain, block in [(pages, bytes(w.p.cluster_size)), (guards, pattern)]:
            for i, cluster in enumerate(chain):
                w.fat[cluster] = chain[i+1] if i+1 < len(chain) else w.end
                w.write_cluster(cluster, block)
        w.add(1, 'pagefile.sys', 0x26, pages[0], len(pages) * w.p.cluster_size)
        w.add(1, 'xwn-fragment-guard.bin', 0x20, guards[0], len(guards) * w.p.cluster_size)
        w.flush()
        cold = Writer(fp, w.p)
        assert list(cold.chain(pages[0])) == pages
        assert list(cold.chain(guards[0])) == guards
        assert cold.read('/pagefile.sys') == bytes(96 * 1024**2)
        guard_data = cold.read('/xwn-fragment-guard.bin')
        assert guard_data == pattern * len(guards)
        r['paging_file'] = {'bytes': len(pages)*w.p.cluster_size, 'clusters': len(pages),
            'first_cluster': pages[0], 'physical_runs': 1 + sum(y != x+1 for x,y in zip(pages,pages[1:]))}
        r['guard_file'] = {'path': '/xwn-fragment-guard.bin', 'bytes': len(guard_data),
            'sha256': hashlib.sha256(guard_data).hexdigest()}
        r['cold_readback_equal'] = True
    subprocess.run(['qemu-img', 'convert', '-O', 'qcow2', str(raw), str(target)], check=True)
    r['check'] = subprocess.check_output(['qemu-img', 'check', str(target)], text=True)
    r['sha256'] = sha(target)
    assert sha(source) == r['source_sha256']
    r['source_preserved'] = True
finally:
    assert temp.resolve().parent == (root / 'fixtures').resolve()
    shutil.rmtree(temp)
    r['temporary_raw_removed'] = True
    (out / 'fatx-fragmented-paging-disk-001.json').write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(r, indent=2))
