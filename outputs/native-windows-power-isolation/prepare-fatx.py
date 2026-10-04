"""Build an emulator-only service-isolation derivative; preserve source disk."""
import argparse, hashlib, json, pathlib, shutil, struct, subprocess, sys

p = argparse.ArgumentParser()
p.add_argument('--mode', choices=['no-audio', 'no-audio-network'], required=True)
a = p.parse_args()
root = pathlib.Path('/home/paul/xbox-windows-native')
ws = pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out = ws / 'outputs/native-windows-power-isolation'
sys.path[:0] = [str(root / 'toolchains/offline-disk/root/usr/lib/python3/dist-packages'),
               str(ws / 'outputs/native-windows-nt5-kernel'),
               str(ws / 'outputs/native-windows-fatx-runtime'),
               '/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import hivex
import fatx_stage_boot as fatx
from bulk_fatx import Writer
from nt5_hive_indexes import normalize

source = ws / 'outputs/native-windows-fatx-flush/artifacts/windows2000-fatx-full-flush-001.qcow2'
target = out / ('artifacts/windows2000-fatx-' + a.mode + '-001.qcow2')
temp = root / ('fixtures/power-isolation-' + a.mode)
assert not temp.exists() and not target.exists()
temp.mkdir()
target.parent.mkdir(exist_ok=True)
services = ['ac97xnt5'] + (['nvnetnt5'] if a.mode == 'no-audio-network' else [])

def sha(path):
    with path.open('rb') as fp:
        return hashlib.file_digest(fp, 'sha256').hexdigest()

r = {'scope': 'Offline emulator-only power isolation; not a hardware deployment',
     'mode': a.mode, 'services_disabled': services, 'source_sha256': sha(source), 'changes': []}
assert r['source_sha256'] == '0c94140b312f4b74e5e0c2ce3109ac6e8e83520d5a6898ca652945fe160c2a57'
try:
    raw = temp / 'disk.raw'
    subprocess.run(['qemu-img', 'convert', '-O', 'raw', str(source), str(raw)], check=True)
    with raw.open('r+b') as fp:
        part = fatx.open_partition(fp, raw, 'E')
        w = Writer(fp, part)
        hive = temp / 'system'
        path = '/WINNT/system32/config/system'
        hive.write_bytes(w.read(path))
        h = hivex.Hivex(str(hive), write=True)
        def node(path):
            n = h.root()
            for component in path.split('\\'):
                n = h.node_get_child(n, component)
                assert n, path
            return n
        for cs in h.node_children(h.root()):
            name = h.node_name(cs)
            if not name.startswith('ControlSet'):
                continue
            for service in services:
                n = node(name + '\\Services\\' + service)
                before = h.value_dword(h.node_get_value(n, 'Start'))
                h.node_set_value(n, {'key': 'Start', 't': 4, 'value': struct.pack('<I', 4)})
                r['changes'].append({'key': name + '\\Services\\' + service,
                                     'value': 'Start', 'before': before, 'after': 4})
        h.commit(str(hive))
        del h
        data, r['nt5_indexes'] = normalize(hive.read_bytes())
        hive.write_bytes(data)
        h = hivex.Hivex(str(hive))
        for item in r['changes']:
            assert h.value_dword(h.node_get_value(node(item['key']), 'Start')) == 4
        del h
        # Replace the hive within its existing allocation; do not reallocate it.
        at = 1
        parts = w.parts(path)
        for component in parts[:-1]:
            e = w.directory(at)['entries'][component.lower()][2]
            assert e[1] & 16
            at = struct.unpack_from('<I', e, 44)[0]
        c, offset, e = w.directory(at)['entries'][parts[-1].lower()]
        chain = list(w.chain(struct.unpack_from('<I', e, 44)[0]))
        assert len(data) <= len(chain) * part.cluster_size
        for i, cluster in enumerate(chain):
            w.write_cluster(cluster, data[i*part.cluster_size:(i+1)*part.cluster_size])
        entry = bytearray(w.read_cluster(c))
        struct.pack_into('<I', entry, offset + 48, len(data))
        w.write_cluster(c, entry)
        w.flush()
        assert Writer(fp, part).read(path) == data
        r['hive_sha256'] = hashlib.sha256(data).hexdigest()
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
    (out / (a.mode + '-disk-001.json')).write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
