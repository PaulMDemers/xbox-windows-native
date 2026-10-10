"""Fresh small matched miniport builds from pinned210 command/object inputs.
No edits to210, guest launch, GPU access or physical access. Every compiler
dependency is individually pinned; existing unchanged objects/import libraries
are privately copied and hashed. This is not a full source reconstruction.
"""
import datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'tools'))
from build_space import require_space
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=k/'artifacts/build003';dest=k/'build003.json';assert not out.exists() and not dest.exists()
space=require_space(out);out.mkdir(parents=True)
old=Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/candidate001')
src=old.parent/'source';ros=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert read(k.parent/'video-gpu-transfer-contract212/abi-review.json')['passed']
assert read(k.parent/'video-gpu-transfer-contract212/host-tests001.json')['passed']
assert read(k/'host-tests003.json')['passed']
gcc=ros/'i386/bin/i686-w64-mingw32-gcc'
assert sha(gcc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
r=dict(status='started',space=space,physical_access=False,guest_launch=False,gpu_submission=False,
 compiler_sha256=sha(gcc),source_pins={},dependency_pins={},copied_inputs={},builds=[],
 parent_tree=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip(),
 started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
assert r['parent_tree']=='53e9aedc58152d03116c00579185000483379837'
try:
 assert sha(oldc_expected:=src/'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c')==read(k.parent/'video-gpu-transfer-contract212/source-inventory002.json')['files']['win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c']['sha256']
 commands=subprocess.check_output([str(ros/'bin/ninja'),'-C',str(old),'-t','commands','xboxvnt5'],text=True)
 (out/'parent-commands.txt').write_text(commands)
 lines=commands.splitlines();oldc=src/'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'
 compileline=next(x for x in lines if ' -c '+str(oldc) in x)
 args=shlex.split(compileline);assert args[0]==str(gcc)
 linkline=lines[-1];assert ' -o win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.sys ' in linkline
 # Extract only the actual compiler/link invocation, never execute a shell chain.
 first,fixup=linkline.split(' && cd ',1)
 linkargs=shlex.split(first.removeprefix(': && '));assert linkargs[0]==str(gcc)
 mini=out/'source/win32ss/drivers/miniport/xboxvmp';(mini/'nt5').mkdir(parents=True)
 for p in [oldc,oldc.parent.parent/'xboxvmp.h']:
  name=p.relative_to(src).as_posix();r['source_pins'][name]=sha(p)
  q=out/'source'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
 text=(mini/'nt5/xboxvnt5.c').read_text();needle='    V->Ready = FALSE;'
 assert text.count(needle)==1;text=text.replace(needle,needle+'\n    { BOOLEAN NTAPI XgtNativeProbe(VOID); if(!XgtNativeProbe()) return FALSE; }')
 (mini/'nt5/xboxvnt5.c').write_text(text)
 for name in ['staging_probe.c','transfer_plan.h']:
  p=k/name if name.endswith('.c') else k.parent/'video-gpu-transfer-contract212'/name
  shutil.copyfile(p,mini/'nt5'/name);r['source_pins']['new/'+name]=sha(p)
 libraries=[];objects=[]
 for i,token in enumerate(linkargs):
  if token.endswith(('.obj','.res','.a')):
   p=old/token;q=out/'inputs'/token;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
   assert sha(p)==sha(q);r['copied_inputs'][token]=sha(q);linkargs[i]=str(q)
   if q.read_bytes().startswith(b'!<thin>\n'):
    ar=ros/'i386/bin/i686-w64-mingw32-ar';ranlib=ros/'i386/bin/i686-w64-mingw32-ranlib'
    members=subprocess.check_output([str(ar),'t',str(p)],text=True).splitlines();assert 0<len(members)<4096
    copied=[];member_pins={}
    for number,member in enumerate(members):
     original=Path(member);original=original if original.is_absolute() else p.parent/original
     copy=out/'thin-members'/str(number)/original.name;copy.parent.mkdir(parents=True,exist_ok=True)
     shutil.copyfile(original,copy);assert sha(copy)==sha(original);copied.append(copy);member_pins[str(original)]=sha(copy)
    regular=q.with_name('regular-'+q.name)
    subprocess.run([str(ar),'cq',str(regular),*map(str,copied)],check=True)
    subprocess.run([str(ranlib),str(regular)],check=True);assert regular.read_bytes().startswith(b'!<arch>\n')
    r.setdefault('materialized_thin',{})[token]=dict(original_sha256=sha(p),regular_sha256=sha(regular),members=member_pins,ar_sha256=sha(ar),ranlib_sha256=sha(ranlib))
    linkargs[i]=str(regular)
   (objects if token.endswith(('.obj','.res')) else libraries).append(token)
 script=src/'sdk/cmake/init-section.lds';shutil.copyfile(script,out/'init-section.lds')
 r['source_pins']['sdk/cmake/init-section.lds']=sha(script)
 linkargs=[x.replace(str(script),str(out/'init-section.lds')) for x in linkargs]
 pefix=old/'host-tools/bin/pefixup';r['pefixup_sha256']=sha(pefix)
 def compile(source,obj,mode,dep):
  a=list(args);a[a.index('-o')+1]=str(obj);a[a.index('-c')+1]=str(source)
  a[a.index('-MF')+1]=str(dep);a[a.index('-MT')+1]=str(obj)
  a+=['-DXWN_STAGING_PROBE='+str(mode)]
  with (out/'compile.log').open('a') as log:subprocess.run(a,cwd=old,check=True,stdout=log,stderr=log)
  deptext=dep.read_text().replace('\\\n',' ');names=shlex.split(deptext.split(': ',1)[1])
  for name in names:
   p=Path(name);p=p if p.is_absolute() else old/p
   r['dependency_pins'][str(p)]=sha(p)
  return a
 for name,mode in [('control001',0),('candidate001',1)]:
  d=out/name;d.mkdir();main=d/'main.obj';helper=d/'helper.obj'
  ca=compile(mini/'nt5/xboxvnt5.c',main,mode,d/'main.d');cb=compile(mini/'nt5/staging_probe.c',helper,mode,d/'helper.d')
  la=list(linkargs);la[la.index('-o')+1]=str(d/'xboxvnt5.sys')
  oldobject=str(out/'inputs/win32ss/drivers/miniport/xboxvmp/nt5/CMakeFiles/xboxvnt5.dir/xboxvnt5.c.obj')
  assert la.count(oldobject)==1;la[la.index(oldobject)]=str(main);la.insert(la.index('-lgcc'),str(helper))
  with (out/'compile.log').open('a') as log:
   subprocess.run(la,cwd=old,check=True,stdout=log,stderr=log)
   subprocess.run([str(pefix),'--kernelmodedriver',str(d/'xboxvnt5.sys')],check=True,stdout=log,stderr=log)
  r['builds'].append(dict(case=name,mode=mode,commands=[ca,cb,la],sha256=sha(d/'xboxvnt5.sys'),bytes=(d/'xboxvnt5.sys').stat().st_size))
 r['status']='compiled'
except Exception as exc:r.update(status='failed',error=repr(exc));raise
finally:
 r['source_sha256']=sha(Path(__file__));r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 dest.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
