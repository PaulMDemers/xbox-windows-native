"""Fresh pinned HAL baseline, shared owner patch and bounded terminal candidate."""
import difflib,hashlib,json,os,shlex,shutil,subprocess,sys,datetime
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[2]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert (repo/'.git/HEAD').read_text().strip()=='ref: refs/heads/codex/xbox-native-pci'
out=k/'artifacts/build001';assert not out.exists();out.mkdir(parents=True)
ros=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(scope=__doc__,physical_access=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='started',commands=[],sources={p.name:sha(p) for p in k.iterdir() if p.is_file()})
def run(argv,**kwargs):
    r['commands'].append([str(v) for v in argv]);subprocess.run(argv,check=True,**kwargs)
try:
    run(['gcc','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g','-o',str(out/'test-broker'),str(k/'test-broker.c')])
    with (k/'tests001.json').open('x') as f:run([str(out/'test-broker')],stdout=f)
    native=out/'native'
    run([sys.executable,str(repo/'tools/rebuild-native.py'),'--source-cache','/home/paul/xbox-windows-native/sources/reactos','--rosbe',str(ros),'--output',str(native),'--profile','boot','--jobs','4'])
    baseline=json.loads((native/'build-report.json').read_text());r['baseline']=baseline
    src=native/'source';changes={}
    reboot=src/'hal/halx86/xbox/reboot.c';original=reboot.read_text();s=original
    s=s.replace('/* PRIVATE FUNCTIONS', '#if defined(XBOX_NT5_HAL) && !defined(_MINIHAL_)\n#include "xwn-smbus-hal.inc"\n#else\n\n/* PRIVATE FUNCTIONS',1)
    s=s.replace('static DECLSPEC_NORETURN\nVOID\nHalpXboxPowerAction', '#endif\n\nstatic DECLSPEC_NORETURN\nVOID\nHalpXboxPowerAction',1)
    s=s.replace('    SMBusWriteByte(SMB_DEVICE_SMC_PIC16LC, SMC_REG_POWER, Action);', '''#if defined(XBOX_NT5_HAL) && !defined(_MINIHAL_)
    HalpSmbusTerminalResult = xb_terminal(&HalpSmbusIo, Action);
#else
    SMBusWriteByte(SMB_DEVICE_SMC_PIC16LC, SMC_REG_POWER, Action);
#endif''')
    s=s.replace('    __halt();\n    UNREACHABLE;', '    for (;;) __halt();')
    assert s!=original
    changes['hal/halx86/xbox/reboot.c']=(original,s)
    spec=src/'hal/halx86/xboxnt5/halnt5.spec';original=spec.read_text()
    changes['hal/halx86/xboxnt5/halnt5.spec']=(original,original+'\n@ stdcall XwnSmbusReadV1(long long ptr)\n')
    for source,target in [('broker.h','xwn-smbus-broker.h'),('hal-broker.inc','xwn-smbus-hal.inc')]:
        changes['hal/halx86/xbox/'+target]=('',(k/source).read_text())
    patch=''
    for name,(before,after) in changes.items():
        (src/name).write_text(after)
        patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name if before else '/dev/null',tofile='b/'+name))
    (k/'0001-hal-shared-smbus.patch').write_text(patch)
    run(['git','-C',str(src),'add','hal/halx86/xbox','hal/halx86/xboxnt5/halnt5.spec'])
    r['candidate_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()
    r['patch_sha256']=sha(k/'0001-hal-shared-smbus.patch')
    script='set -e\n'+shlex.join(['cmake','--build',str(native/'build-boot'),'--target','halxboxnt5','--','-j4'])+'\n'
    (out/'candidate-commands.sh').write_text(script)
    with (out/'candidate-build.log').open('x') as f:
        run([str(ros/'RosBE.sh'),str(src),'0','i386'],input=script,text=True,stdout=f,stderr=f)
    candidate=native/'build-boot/hal/halx86/xboxnt5/halxboxnt5.dll'
    shutil.copyfile(candidate,out/'halxboxnt5.dll')
    r['candidate_sha256']=sha(out/'halxboxnt5.dll');r['status']='compiled'
except BaseException as e:
    r.update(status='failed',error=repr(e));raise
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (k/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
