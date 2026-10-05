"""Emulator-only replay with the same memory helper, no automatic restart."""
import importlib,json,pathlib,subprocess
m=importlib.import_module('prepare-fixture');k=m.k;source=m.target.with_name('paint-pressure-001.qcow2')
expected=json.loads((k/'pressure-fixture.json').read_text())['fixture_sha256'];assert m.filehash(source)==expected
m.target=source.with_name('paint-replay-001.qcow2');assert not m.target.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(m.target)],check=True)
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512);f=m.SliceIO(m.target);w=m.Writer(f,m.fatx.open_partition(f,m.target,'F'))
helper=(k/'artifacts/replay.exe').read_bytes();info=w.write('xwnpaint/replay.exe',helper)
startup=b'@echo off\r\nstart /min C:\\xwnpaint\\pressure.exe\r\nC:\\xwnpaint\\replay.exe\r\nexit\r\n'
m.replace(w,'Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',startup);w.flush()
assert w.read('xwnpaint/replay.exe')==helper
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(m.target)],check=True)
seed=m.ws/'work/paint-replay-seed.qcow2';assert not seed.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(m.target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+m.target.name,str(seed)],check=True)
assert m.filehash(source)==expected
(k/'replay-fixture.json').write_text(json.dumps(dict(scope=__doc__,source_sha256=expected,fixture_sha256=m.filehash(m.target),helper=info,startup_sha256=m.sha(startup)),indent=2)+'\n')
