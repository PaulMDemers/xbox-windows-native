"""Fresh matched boot-provider builds; pinned reused objects, no deployment."""
import datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'tools'))
from build_space import require_space
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=k/'artifacts/build001';dest=k/'build001.json';assert not out.exists() and not dest.exists()
space=require_space(out);out.mkdir(parents=True)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/candidate001')
src=old.parent/'source';ros=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
review=read(k/'source-review.json');assert review['passed'] and read(k/'host-tests002.json')['passed']
gcc=ros/'i386/bin/i686-w64-mingw32-gcc';assert sha(gcc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
boot='drivers/base/bootvid/i386/xbox/bootvid.c'
assert sha(src/boot)==review['parent_source_pins'][boot]
r=dict(status='started',source_sha256=sha(Path(__file__)),space=space,
    started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    compiler_sha256=sha(gcc),parent_tree=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip(),
    source_pins={},dependency_pins={},copied_inputs={},builds=[],physical_access=False,guest_launch=False,
    limits='Fresh changed bootvid translation unit and matching control; exact unchanged objects/import libraries retained. Not a complete clean-tree reconstruction.')
assert r['parent_tree']=='53e9aedc58152d03116c00579185000483379837'
try:
    commands=subprocess.check_output([str(ros/'bin/ninja'),'-C',str(old),'-t','commands','xboxbvidnt5'],text=True)
    (out/'parent-commands.txt').write_text(commands);lines=commands.splitlines()
    args=shlex.split(next(x for x in lines if ' -c '+str(src/boot) in x));assert args[0]==str(gcc)
    linkargs=shlex.split(lines[-1].split(' && cd ',1)[0].removeprefix(': && '));assert linkargs[0]==str(gcc)
    changed_token='drivers/base/bootvid/CMakeFiles/xboxbvidnt5.dir/i386/xbox/bootvid.c.obj'
    for i,token in enumerate(linkargs):
        if token.endswith(('.obj','.res','.a','.def')):
            p=old/token;q=out/'inputs'/token;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
            assert sha(q)==sha(p);r['copied_inputs'][token]=sha(q);linkargs[i]=str(q)
            if q.read_bytes().startswith(b'!<thin>\n'):
                ar=ros/'i386/bin/i686-w64-mingw32-ar';ranlib=ros/'i386/bin/i686-w64-mingw32-ranlib'
                members=subprocess.check_output([str(ar),'t',str(p)],text=True).splitlines();assert 0<len(members)<4096
                copies=[];pins={}
                for no,member in enumerate(members):
                    original=Path(member);original=original if original.is_absolute() else p.parent/original
                    copy=out/'thin-members'/str(no)/original.name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy)
                    assert sha(copy)==sha(original);pins[str(original)]=sha(copy);copies.append(copy)
                regular=q.with_name('regular-'+q.name)
                subprocess.run([str(ar),'cq',str(regular),*map(str,copies)],check=True)
                subprocess.run([str(ranlib),str(regular)],check=True);linkargs[i]=str(regular)
                r.setdefault('thin_materialized',{})[token]=dict(original_sha256=sha(p),regular_sha256=sha(regular),members=pins)
    script=src/'sdk/cmake/init-section.lds';shutil.copyfile(script,out/'init-section.lds')
    r['source_pins']['init-section.lds']=sha(script)
    linkargs=[x.replace(str(script),str(out/'init-section.lds')) for x in linkargs]
    pefix=old/'host-tools/bin/pefixup';r['pefixup_sha256']=sha(pefix)
    for case,source in [('control001',src/boot),('candidate001',k/'artifacts/source'/boot)]:
        d=out/case;d.mkdir();local=d/'bootvid.c';shutil.copyfile(source,local)
        if case=='candidate001':shutil.copyfile(k/'boot_layout.h',d/'boot_layout.h')
        r['source_pins'][case]=sha(local);obj=d/'bootvid.obj';dep=d/'bootvid.d';a=list(args)
        for flag,value in [('-o',obj),('-c',local),('-MF',dep),('-MT',obj)]:a[a.index(flag)+1]=str(value)
        with (out/'compile.log').open('a') as log:subprocess.run(a,cwd=old,check=True,stdout=log,stderr=log)
        names=shlex.split(dep.read_text().replace('\\\n',' ').split(': ',1)[1])
        for name in names:
            p=Path(name);p=p if p.is_absolute() else old/p;digest=sha(p)
            if str(p) in r['dependency_pins']:assert r['dependency_pins'][str(p)]==digest
            r['dependency_pins'][str(p)]=digest
        la=list(linkargs);la[la.index('-o')+1]=str(d/'xboxbvid.dll')
        token=str(out/'inputs'/changed_token);assert la.count(token)==1;la[la.index(token)]=str(obj)
        with (out/'compile.log').open('a') as log:
            subprocess.run(la,cwd=old,check=True,stdout=log,stderr=log)
            subprocess.run([str(pefix),'--kerneldll',str(d/'xboxbvid.dll')],check=True,stdout=log,stderr=log)
        r['builds'].append(dict(case=case,commands=[a,la],sha256=sha(d/'xboxbvid.dll'),object_sha256=sha(obj),bytes=(d/'xboxbvid.dll').stat().st_size))
    for name,digest in r['dependency_pins'].items():assert sha(Path(name))==digest
    assert sha(src/boot)==review['parent_source_pins'][boot]
    r['status']='compiled'
except Exception as exc:r.update(status='failed',error=repr(exc));raise
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
