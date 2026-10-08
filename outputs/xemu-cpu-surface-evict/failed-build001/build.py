"""Matched private xemu builds under the build lease; restore all borrowed sources."""
import difflib,hashlib,json,os,shutil,subprocess
from pathlib import Path
from patch import apply
assert os.environ.get('XWN_BUILD_LEASE')=='held'
k=Path(__file__).resolve().parent;ws=k.parents[1]
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
assert not (k/'build.json').exists() and not (k/'artifacts').exists()
assert (s/'.source-revision').read_text().strip()=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/renderer.h']
original={n:(s/n).read_bytes() for n in names}
assert sha(s/names[2])=='c3dcde0513f3d3d1068997c91ccc88e011059c32f9d802c3d7fc64080bf40403'
art=k/'artifacts';art.mkdir();(k/'build-logs').mkdir()
resource=ws/'outputs/native-windows-physical-f/xemu-nv2a-resource-model.patch'
assert sha(resource)=='d82eb50cebf46256e39273734427aa977d5033cc7426c31c69fb00efc83aacdb'
report=dict(toolchain=image,source_revision=(s/'.source-revision').read_text().strip(),
    original_sources={n:sha(s/n) for n in names},resource_patch_sha256=sha(resource),patch_generator_sha256=sha(k/'patch.py'),builds=[])
save(k/'build-start.json',report)
try:
    subprocess.run(['patch','--batch','--forward','-p1','-i',str(resource)],cwd=s,check=True)
    for case in ['control','candidate']:
        if case=='candidate':
            a,b=apply(original[names[2]].decode(),original[names[3]].decode())
            (s/names[2]).write_text(a);(s/names[3]).write_text(b)
            diff=[]
            for n in names[2:]:diff.extend(difflib.unified_diff(original[n].decode().splitlines(True),(s/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
            (k/'cpu-surface-evict.patch').write_text(''.join(diff))
        tracked=subprocess.check_output(['git','ls-files','-z'],cwd=s).decode().split('\0')
        pins={n:sha(s/n) for n in tracked if n and (s/n).is_file()}
        save(k/(case+'-source-pins.json'),pins)
        with (k/'build-logs'/(case+'.log')).open('wb') as log:
            subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],check=True,stdout=log,stderr=subprocess.STDOUT)
        exe=art/('xemu-'+case+'.exe');shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
        row=dict(case=case,sha256=sha(exe),bytes=exe.stat().st_size,source_manifest_sha256=sha(k/(case+'-source-pins.json')))
        report['builds'].append(row);save(k/'build-progress.json',report)
finally:
    for n,b in original.items():(s/n).write_bytes(b)
    report['borrowed_sources_restored']=all((s/n).read_bytes()==b for n,b in original.items())
    save(k/'build-closure.json',report)
assert report['borrowed_sources_restored'] and len(report['builds'])==2
control=json.loads((k/'control-source-pins.json').read_text());candidate=json.loads((k/'candidate-source-pins.json').read_text())
changed=[n for n in control if control[n]!=candidate[n]];assert changed==sorted(names[2:]),changed
report.update(passed=True,changed_sources=changed,patch_sha256=sha(k/'cpu-surface-evict.patch'))
save(k/'build.json',report)
print(json.dumps(report,indent=2))
