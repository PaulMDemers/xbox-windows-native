"""Compile only the isolated stock-E boot chain with pinned toolchains."""
import datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/home/paul/xbox-windows-native/build/stock-boot334-build001');O=Path('/mnt/e/xwn334/build001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(B);O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
review=read(K/'source-review001.json')
for label,tree in review['trees'].items():
    assert subprocess.check_output(['git','-C',str(B/label),'write-tree'],text=True).strip()==tree
    assert not subprocess.check_output(['git','-C',str(B/label),'diff','--name-only'])
lock=read(W/'outputs/video-trace-reuse/inputs.json');rosbe=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
for n,h in lock['tool_sha256'].items():assert sha(rosbe/n)==h
cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
defs=dict(read(W/'outputs/hd-reservation300/build001.json')['cases']['candidate001']['definitions'])
defs.update(XBOX_NATIVE_FATX_F_BOOT='OFF',XBOX_NATIVE_EXTENDED_NT5_BOOT='OFF',XBOX_NATIVE_FATX_E_BOOT='ON')
r=dict(status='building',physical_access=False,guest_launch=False,source_review_sha256=sha(K/'source-review001.json'),definitions=defs,tool_sha256=lock['tool_sha256'],gcc12_sha256=sha(cc),space=space,commands=[],started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    # Execute the exact new CMake guard in a small script with target calls recorded.
    cm=(B/'reactos/boot/freeldr/freeldr/pcat.cmake').read_text().split('option(XBOX_NATIVE_FATX_E_BOOT',1)[1]
    block='option(XBOX_NATIVE_FATX_E_BOOT'+cm
    cases=[('valid',{},True)]+[(n,{n:'ON' if n in ('XBOX_NATIVE_FATX_F_BOOT','XBOX_NATIVE_EXTENDED_NT5_BOOT','XBOX_NATIVE_FATX_IO_PREFLIGHT','XBOX_NATIVE_FATX_NT5_PREFLIGHT') else 'OFF'},False) for n in ['XBOX_NATIVE_IO_PREFLIGHT','XBOX_NATIVE_NT5_HANDOFF','XBOX_NATIVE_NT5_ENTER','XBOX_NATIVE_NT5_AUTORUN','XBOX_NATIVE_FATX_F_BOOT','XBOX_NATIVE_EXTENDED_NT5_BOOT','XBOX_NATIVE_FATX_IO_PREFLIGHT','XBOX_NATIVE_FATX_NT5_PREFLIGHT']]+[('wrong_arch',{'SARCH':'pc'},False)]
    r['profile_tests']=[]
    for i,(name,overrides,expected) in enumerate(cases):
        values={**defs,**overrides};script=O/f'guard{i}.cmake'
        script.write_text('cmake_policy(SET CMP0077 NEW)\n'+''.join(f'set({n} "{v}")\n' for n,v in values.items())+'function(target_compile_definitions)\nendfunction()\n'+block)
        p=subprocess.run([str(rosbe/'bin/cmake'),'-P',str(script)],capture_output=True,text=True)
        assert (p.returncode==0)==expected,(name,p.stderr)
        r['profile_tests'].append(dict(case=name,accepted=p.returncode==0,expected=expected))
    src=B/'reactos';build=B/'nt5'
    configure=['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+a+'='+b for a,b in defs.items()]
    compile=['cmake','--build',str(build),'--target','freeldr','rosload','--','-j4']
    script='set -e\n'+shlex.join(configure)+'\n'+shlex.join(compile)+'\n';(O/'commands.sh').write_text(script)
    r['commands']+=[configure,compile];save()
    with (O/'nt5.log').open('w') as log:subprocess.run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True,stdout=log,stderr=log,check=True,timeout=900)
    for rel,name in [('boot/freeldr/freeldr/freeldr.sys','freeldr.sys'),('boot/freeldr/freeldr/rosload.exe','rosload.exe')]:shutil.copyfile(build/rel,O/name)
    # Cromwell source copy is private; original reviewed parent is untouched.
    host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
    env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH'])
    csrc=B/'cromwell';flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_1080I=1'
    args=['make','all','CC='+str(cc),'GITREV=9fc54d0-xwn-eboot','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(csrc/'scripts/ldscript-crom.ld')+' -Map='+str(O/'image-crom.map')]
    r['commands'].append(args);r['cromwell_flags']=flags;save()
    with (O/'cromwell.log').open('w') as log:subprocess.run(args,cwd=csrc,env=env,stdout=log,stderr=log,check=True,timeout=300)
    for rel,name in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/image-crom.bin','image-crom.bin')]:shutil.copyfile(csrc/rel,O/name)
    r['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file() and p.suffix in ['.sys','.exe','.xbe','.elf','.bin','.map']}
    r['status']='compiled'
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['logs']={p.name:sha(p) for p in O.glob('*.log')};save();print(r['status'],flush=True)
