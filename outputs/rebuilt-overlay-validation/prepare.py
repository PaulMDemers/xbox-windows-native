"""Install all eight rebuilt components into a new owned emulator child only."""
import importlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

k = Path(__file__).resolve().parent
ws = k.parents[1]
sys.path.insert(0, str(ws/'outputs/native-windows-paint-save'))
m = importlib.import_module('prepare-fixture')
base = ws/'outputs/native-windows-fatx-forensics/artifacts/gdi-baseline-003.qcow2'
expected = json.loads((ws/'outputs/video-next/probe-v3/fixture.json').read_text())['fixture_sha256']
assert m.filehash(base) == expected
archive = Path('/mnt/e/Codex-archive/xbox-windows-native/reconstructed-overlay-20261005/native-overlay.zip')
report = json.loads((ws/'outputs/reproducible-build/pipeline-002-package.json').read_text())
assert m.filehash(archive) == report['archive_sha256']
m.target = base.with_name('rebuilt-overlay-001.qcow2')
seed = ws/'work/rebuilt-overlay-001-seed.qcow2'
assert not m.target.exists() and not seed.exists()
assert __import__('shutil').disk_usage('/mnt/c').free > 8*1024**3
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(m.target)],check=True)
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io = m.SliceIO(m.target)
writers = {letter:m.Writer(io,m.fatx.open_partition(io,m.target,letter)) for letter in ['E','F']}
payloads=[]
with zipfile.ZipFile(archive) as z:
    manifest=json.loads(z.read('manifest.json'))
    assert len(manifest['files'])==8
    for row in manifest['files']:
        letter,path=row['path'].split('/',1)
        data=z.read(row['path'])
        assert m.sha(data)==row['sha256'] and len(data)==row['bytes']
        writer=writers[letter]
        old=writer.read(path)
        m.replace(writer,path,data)
        payloads.append(dict(**row,before_sha256=m.sha(old),before_bytes=len(old)))
for writer in writers.values(): writer.flush()
for row in payloads:
    letter,path=row['path'].split('/',1)
    check=m.Writer(io,m.fatx.open_partition(io,m.target,letter))
    assert m.sha(check.read(path))==row['sha256']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(m.target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(m.target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+m.target.name,str(seed)],check=True)
assert m.filehash(base)==expected
result=dict(scope=__doc__,source_sha256=expected,archive_sha256=report['archive_sha256'],
            fixture_sha256=m.filehash(m.target),seed_sha256=m.filehash(seed),payloads=payloads,
            workload='Unchanged GDI probe v3 and one-shot normal-restart runner',physical_access=False)
(k/'fixture.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
