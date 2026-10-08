"""Freeze a private pbkit core with only read-only depth-buffer accessors."""
import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sdk=Path('C:/nxdk')
build=ws/'work/gpu-cpu-coherence143-build001'
assert not build.exists() and not (k/'build-inputs.json').exists()
assert shutil.disk_usage(ws).free >= 20*1024**3
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rev=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()
assert rev=='58427c078b4ccb0121f359b6b6c536b3b2914976'
build.mkdir();private=build/'pbkit-private';private.mkdir()
inputs=[]
for p in sorted((sdk/'lib/pbkit').glob('*')):
    if p.is_file() and p.suffix in ['.c','.h']:
        inputs.append(dict(path=str(p),sha256=sha(p)));shutil.copyfile(p,private/p.name)
for p in sorted((sdk/'lib').rglob('*.lib')):
    inputs.append(dict(path=str(p),sha256=sha(p)))
original=(private/'pbkit.c').read_bytes()
accessors=b'\n/* Owned diagnostic accessors: read only; shared SDK is unmodified. */\nDWORD *xwn_depth_buffer(void) { return (DWORD *)pb_DSAddr; }\nDWORD xwn_depth_pitch(void) { return pb_DepthStencilPitch; }\n'
(private/'pbkit.c').write_bytes(original+accessors)
for name in ['main.c','Makefile']:shutil.copyfile(k/name,build/name)
r=dict(sdk_revision=rev,sdk_status=subprocess.check_output(['git','-C',str(sdk),'status','--short','--untracked-files=no'],text=True),
       sdk_inputs=inputs,source_sha256=sha(k/'main.c'),makefile_sha256=sha(k/'Makefile'),private_core_sha256=sha(private/'pbkit.c'),
       accessor_text=accessors.decode(),shared_sdk_modified=False,build=str(build),physical_access=False)
(k/'build-inputs.json').write_text(json.dumps(r,indent=2)+'\n')
print('Private sources pinned; no guest launched')
