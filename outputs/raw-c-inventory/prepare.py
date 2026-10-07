"""Stage the read-only C probe on E in a new owned emulator child only."""
import importlib.util,json,os,pathlib,subprocess
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/raw-c-inventory'
spec=importlib.util.spec_from_file_location('ranges',ws/'outputs/native-windows-paint-save/prepare-fixture.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=ws/'outputs/native-windows-fatx-preflight/artifacts/preflight-fixture-001.qcow2';target=k/'artifacts/fixture-001.qcow2';seed=ws/'work/raw-c-seed-001.qcow2'
assert not target.exists() and not seed.exists();before=m.filehash(source);m.target=target
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'E'));data=(k/'artifacts/default.xbe').read_bytes();item=w.write('Apps/XWNRawC/default.xbe',data);w.flush()
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'E'));assert w.read('Apps/XWNRawC/default.xbe')==data
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',os.path.relpath(source,target.parent),str(target)],check=True)
assert before==m.filehash(source)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/raw-c-inventory/artifacts/fixture-001.qcow2',str(seed)],check=True)
r=dict(scope=__doc__,source=str(source.relative_to(ws)),source_sha256=before,source_unchanged=True,fixture_sha256=m.filehash(target),file=item,readback_verified=True)
(k/'fixture.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
