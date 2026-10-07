import json,subprocess,pathlib,hashlib
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/raw-c-inventory';source=k/'artifacts/fixture-001.qcow2';dest=k/'artifacts/flat-002.qcow2';seed=ws/'work/raw-c-seed-002.qcow2'
assert not dest.exists() and not seed.exists()
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=digest(source)
subprocess.run(['qemu-img','convert','-O','qcow2',str(source),str(dest)],check=True)
subprocess.run(['qemu-img','compare',str(source),str(dest)],check=True)
assert digest(source)==before
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(dest),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/raw-c-inventory/artifacts/flat-002.qcow2',str(seed)],check=True)
(k/'flat-fixture.json').write_text(json.dumps(dict(reason='Host001 failed opening deep backing chain before guest launch',source_sha256=before,source_unchanged=True,virtual_contents_equal=True,flat_sha256=digest(dest)),indent=2)+'\n')
