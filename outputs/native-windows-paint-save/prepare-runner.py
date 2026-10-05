"""Prepare an isolated emulator fixture for the physical one-shot launcher."""
import importlib,json,subprocess
m=importlib.import_module('prepare-fixture');k=m.k
base=json.loads((k/'fixture.json').read_text());source=m.target.with_name(base['fixture_name'])
assert m.filehash(source)==base['fixture_sha256']
m.target=source.with_name('paint-runner-001.qcow2');assert not m.target.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(m.target)],check=True)
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512);f=m.SliceIO(m.target);w=m.Writer(f,m.fatx.open_partition(f,m.target,'F'))
helpers=[]
for name in ['replay','runner']:
 data=(k/'artifacts'/(name+'.exe')).read_bytes();helpers.append(w.write('xwnpaint/'+name+'.exe',data))
startup=b'@echo off\r\nC:\\xwnpaint\\runner.exe\r\nexit\r\n'
m.replace(w,'Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',startup);w.flush()
for row in helpers:assert m.sha(w.read(row['path']))==row['sha256']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(m.target)],check=True)
seed=m.ws/'work/paint-runner-seed.qcow2';assert not seed.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(m.target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+m.target.name,str(seed)],check=True)
assert m.filehash(source)==base['fixture_sha256']
(k/'runner-fixture.json').write_text(json.dumps(dict(scope=__doc__,source_sha256=base['fixture_sha256'],fixture_sha256=m.filehash(m.target),helpers=helpers,startup_sha256=m.sha(startup),runner_source_sha256=m.sha((k/'runner.c').read_bytes())),indent=2)+'\n')
