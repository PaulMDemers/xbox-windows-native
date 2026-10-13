"""Fresh exact303 source checkout, two HD builds differing only in body clocks."""
import datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
base=Path('/home/paul/xbox-windows-native/build/hd-profile345-build001');out=Path('/mnt/e/xwn345/build001');dest=K/'build001.json'
assert not base.exists() and not out.exists() and not dest.exists()
space=require_space(base);assert all(v['free_bytes']-512*1024**2>=20*1024**3 for v in space['checks']);assert shutil.disk_usage('/mnt/e').free-512*1024**2>=20*1024**3
old=json.loads((K.parent/'hd-surface303/build003.json').read_text());tree=old['source_tree'];assert tree=='e48e031228a0d6d483c7ac8273c40a34b75644e7'
parent=Path('/home/paul/xbox-windows-native/build/hd-surface303-build001/source');src=base/'source';rosbe=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in old['tool_sha256'].items():assert sha(rosbe/n)==h
out.mkdir(parents=True);base.mkdir();r=dict(status='started',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_tree=tree,space=space,tool_sha256=old['tool_sha256'],cases={},physical_access=False,guest_launch=False)
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    with (out/'source.log').open('w') as log:
        subprocess.run(['git','clone','--shared','--no-checkout',str(parent),str(src)],check=True,stdout=log,stderr=log)
        subprocess.run(['git','-C',str(src),'read-tree',tree],check=True,stdout=log,stderr=log)
        subprocess.run(['git','-C',str(src),'checkout-index','--all'],check=True,stdout=log,stderr=log)
        assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==tree
        assert not subprocess.check_output(['git','-C',str(src),'diff','--name-only'])
    r['source_files']={str(p.relative_to(src)):sha(p) for p in (src/'win32ss/drivers/displays/framebuf').rglob('*') if p.is_file()}
    for case,enabled in [('control001','OFF'),('candidate001','ON')]:
        defs=dict(old['cases']['candidate001']['definitions']);assert defs['XWN_HD_SURFACE_BOUNDS']=='ON' and defs['XWN_UC_STORES']=='OFF' and defs['XWN_TEXT_BOUNDS']=='ON';defs['XWN_BODY_PROFILE']=enabled
        build=base/case;commands=[['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+k+'='+v for k,v in defs.items()],['cmake','--build',str(build),'--target','xwnown','--','-j4']]
        script='set -e\n'+'\n'.join(shlex.join(c) for c in commands)+'\n';(out/(case+'-commands.sh')).write_text(script)
        with (out/(case+'.log')).open('w') as log:subprocess.run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True,stdout=log,stderr=log,check=True,timeout=600)
        target=out/case;target.mkdir();p=target/'xwnown.dll';shutil.copyfile(build/'win32ss/drivers/displays/framebuf/xwnown.dll',p)
        r['cases'][case]=dict(definitions=defs,sha256=sha(p),bytes=p.stat().st_size,commands=commands,status='compiled');save();print(case,'compiled',flush=True)
    assert [k for k in r['cases']['control001']['definitions'] if r['cases']['control001']['definitions'][k]!=r['cases']['candidate001']['definitions'][k]]==['XWN_BODY_PROFILE']
    assert not subprocess.check_output(['git','-C',str(src),'diff','--name-only'])
    r['status']='compiled'
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
    r.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),logs={p.name:sha(p) for p in out.glob('*.log')});save()
