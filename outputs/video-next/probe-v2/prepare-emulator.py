"""Isolated GDI correctness boot using the existing one-shot normal-restart runner."""
import importlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent.parent/'native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
base=json.loads((m.k/'fixture.json').read_text());source=m.target.with_name(base['fixture_name'])
assert m.filehash(source)==base['fixture_sha256']
m.target=source.with_name('gdi-baseline-002.qcow2');assert not m.target.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(m.target)],check=True)
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
f=m.SliceIO(m.target);w=m.Writer(f,m.fatx.open_partition(f,m.target,'F'))
payloads=[]
for name,p in [('replay.exe',k/'artifacts/gdi-probe.exe'),('runner.exe',m.k/'artifacts/runner.exe')]:
    payloads.append(w.write('xwnpaint/'+name,p.read_bytes()))
startup=b'@echo off\r\nC:\\xwnpaint\\runner.exe\r\nexit\r\n'
m.replace(w,'Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',startup);w.flush()
for row in payloads:assert m.sha(w.read(row['path']))==row['sha256']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(m.target)],check=True)
seed=m.ws/'work/gdi-baseline-v2-seed.qcow2';assert not seed.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(m.target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+m.target.name,str(seed)],check=True)
assert m.filehash(source)==base['fixture_sha256']
(k/'fixture.json').write_text(json.dumps(dict(scope=__doc__,source_sha256=base['fixture_sha256'],fixture_sha256=m.filehash(m.target),payloads=payloads,startup_sha256=m.sha(startup),seed_sha256=m.filehash(seed)),indent=2)+'\n')
