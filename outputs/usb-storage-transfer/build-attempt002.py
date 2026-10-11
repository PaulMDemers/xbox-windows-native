"""Private source/build copy; source-pinned instrumentation, no borrowed edits."""
import hashlib,json,os,shutil,subprocess,runpy
from pathlib import Path
from patch import apply
assert os.environ.get('XWN_BUILD_LEASE')=='held'
k=Path(__file__).resolve().parent;repo=k.parents[1]
original=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
s=repo/'work/builds/xemu-transfer001'
assert not (k/'build.json').exists()
resume=s.exists()
if resume:
    failure=json.loads((k/'build-failure.json').read_text())
    assert 'CalledProcessError' in failure['error'] and "'cp'" in failure['error']
    shutil.copyfile(k/'build-failure.json',k/'copy-failure001.json')
    shutil.copyfile(k/'build-closure.json',k/'copy-closure001.json')
assert shutil.disk_usage('/mnt/c').free > 20*1024**3+256*1024**2
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda name,r:(k/name).write_text(json.dumps(r,indent=2)+'\n')
report=dict(physical_access=False,toolchain=image,source_revision=(original/'.source-revision').read_text().strip(),private_source=str(s),original_source=str(original))
save('build-start.json',report)
try:
    s.parent.mkdir(parents=True,exist_ok=True)
    if not resume:
        with (k/'copy-console.txt').open('wb') as log:
            subprocess.run(['cp','-a',str(original),str(s)],check=True,stdout=log,stderr=subprocess.STDOUT)
    materialized=[]
    for root,dirs,files in os.walk(original):
        rel=Path(root).relative_to(original)
        if not rel.parts:dirs[:]=[n for n in dirs if n not in ['build','.git']]
        for name in dirs+files:
            p=Path(root)/name
            if p.is_symlink() and p.exists():
                dest=s/p.relative_to(original)
                assert not dest.exists(),str(dest)
                if p.is_dir():shutil.copytree(p.resolve(),dest,symlinks=False)
                else:shutil.copy2(p.resolve(),dest)
                materialized.append(str(p.relative_to(original)))
    report['materialized_source_links']=materialized
    report['readonly_build_mounts']=['build/pyvenv','scripts','python']
    resource=repo/'outputs/native-windows-physical-f/xemu-nv2a-resource-model.patch'
    assert sha(resource)=='d82eb50cebf46256e39273734427aa977d5033cc7426c31c69fb00efc83aacdb'
    subprocess.run(['patch','--batch','--forward','-p1','-i',str(resource)],cwd=s,check=True)
    reconstruct=runpy.run_path(str(repo/'outputs/xemu-cpu-surface-evict/build003/patch.py'))['apply']
    a=s/'hw/xbox/nv2a/pgraph/gl/surface.c';b=s/'hw/xbox/nv2a/pgraph/gl/renderer.h'
    x,y=reconstruct(a.read_text(),b.read_text());a.write_text(x);b.write_text(y)
    baseline=json.loads((repo/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json').read_text())
    mismatches=[n for n,h in baseline.items() if not (s/n).is_file() or sha(s/n)!=h]
    report['baseline_manifest_sha256']=sha(repo/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json')
    report['baseline_files_checked']=len(baseline);report['baseline_mismatches']=mismatches
    save('source-check.json',report)
    assert not mismatches,mismatches
    report['build_configuration_hashes']={n:sha(s/'build'/n) for n in ['config-host.h','config.status','config-meson.cross','config-meson.native','build.ninja','compile_commands.json']}
    apply(s,k)
    pins={n:sha(s/n) for n in baseline};pins['include/qemu/xwn-transfer.h']=sha(s/'include/qemu/xwn-transfer.h')
    save('instrumented-source-pins.json',pins)
    changed=[n for n in baseline if pins[n]!=baseline[n]]
    assert changed==['block/block-backend.c','system/dma-helpers.c'],changed
    report['changed_sources']=changed+['include/qemu/xwn-transfer.h']
    report['patch_sha256']=sha(k/'transfer.patch');report['header_sha256']=sha(k/'xwn-transfer.h')
    (k/'artifacts').mkdir(exist_ok=False)
    with (k/'artifacts/build.log').open('wb') as log:
        subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-v',str(original/'build/pyvenv')+':/src/build/pyvenv:ro','-v',str(original/'scripts')+':/src/build/scripts:ro','-v',str(original/'python')+':/src/build/python:ro','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],check=True,stdout=log,stderr=subprocess.STDOUT)
    exe=k/'artifacts/xemu-transfer.exe';shutil.copyfile(s/'build/qemu-system-i386w.exe',exe)
    report.update(passed=True,sha256=sha(exe),bytes=exe.stat().st_size)
    save('build.json',report)
except BaseException as error:
    report.update(passed=False,error=repr(error));save('build-failure.json',report);raise
finally:
    report['borrowed_sources_modified']=False;save('build-closure.json',report)
print(json.dumps(report,indent=2))
