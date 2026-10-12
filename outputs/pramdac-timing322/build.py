"""Exact-parent reconstruction, host qualification and matched leased builds."""
import difflib,hashlib,importlib.util,json,os,re,shutil,subprocess
from pathlib import Path
from patch import apply
from host import run
assert os.environ.get('XWN_BUILD_LEASE')=='held'
k=Path(__file__).resolve().parent;ws=k.parents[1]
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet');out=Path('/mnt/d/xwn322/build001')
assert not out.exists() and not (k/'build001.json').exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,r:p.write_text(json.dumps(r,indent=2)+'\n')
prior=ws/'outputs/xemu-cpu-surface-evict/build003'
spec=importlib.util.spec_from_file_location('evict_parent',prior/'patch.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pramdac.c','hw/xbox/nv2a/nv2a_regs.h']
original={n:(s/n).read_bytes() for n in names}
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73'
report=dict(passed=False,source_revision=(s/'.source-revision').read_text().strip(),toolchain=image,builds=[],physical_access=False,inputs={n:sha(k/n) for n in ['patch.py','host.py','build.py','Build.ps1','DESIGN.md']})
assert report['source_revision']=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
resource=ws/'outputs/native-windows-physical-f/xemu-nv2a-resource-model.patch';assert sha(resource)=='d82eb50cebf46256e39273734427aa977d5033cc7426c31c69fb00efc83aacdb'
try:
    subprocess.run(['patch','--batch','--forward','-p1','-i',str(resource)],cwd=s,check=True)
    a,b=mod.apply(original[names[2]].decode(),original[names[3]].decode());(s/names[2]).write_text(a);(s/names[3]).write_text(b)
    pins=json.loads((prior/'candidate-source-pins.json').read_text())
    differences=[n for n,digest in pins.items() if not (s/n).is_file() or sha(s/n)!=digest]
    save(out/'parent-source-review.json',dict(passed=not differences,pins=len(pins),differences=differences))
    assert not differences,differences
    control={n:(s/n).read_text() for n in names};candidate=apply(control)
    changed=[n for n in names if control[n]!=candidate[n]];assert sorted(changed)==sorted([names[0],names[1],names[4],names[5]])
    report['parent_source_pins']=len(pins);report['changed_sources']=changed
    for case,files in [('control',control),('candidate',candidate)]:
        for n,value in files.items():
            p=out/case/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
    diff=''.join(''.join(difflib.unified_diff(control[n].splitlines(True),candidate[n].splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n in changed)
    (k/'timing-registers.patch').write_text(diff)
    host=run(control,candidate,Path('/mnt/d/xwn322/host001'));save(k/'host001.json',host);assert host['passed']
    for case,files in [('control',control),('candidate',candidate)]:
        for n,value in files.items():(s/n).write_text(value)
        manifest={n:sha(s/n) for n in pins};save(out/(case+'-source-pins.json'),manifest)
        with (out/(case+'.log')).open('wb') as log:
            subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        assert all(sha(s/n)==h for n,h in manifest.items()),'Sources changed during build'
        exe=out/('xemu-'+case+'.exe');shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
        report['builds'].append(dict(case=case,path=str(exe),sha256=sha(exe),bytes=exe.stat().st_size,source_manifest_sha256=sha(out/(case+'-source-pins.json'))))
        save(k/'build-progress001.json',report)
    warnings={case:re.findall(r'warning: (.*)',(out/(case+'.log')).read_text(errors='replace')) for case in ['control','candidate']}
    report['warnings']=warnings;assert not set(warnings['candidate'])-set(warnings['control']),'New warning message'
    report['passed']=True
except Exception as e:report['failure']=repr(e)
finally:
    for n,value in original.items():(s/n).write_bytes(value)
    report['borrowed_sources_restored']=all((s/n).read_bytes()==value for n,value in original.items())
    report['private_files']={str(p):sha(p) for p in out.rglob('*') if p.is_file()}
    save(k/'build001.json',report)
print(json.dumps({n:report.get(n) for n in ['passed','failure','borrowed_sources_restored','builds']},indent=2));assert report['passed'] and report['borrowed_sources_restored']
