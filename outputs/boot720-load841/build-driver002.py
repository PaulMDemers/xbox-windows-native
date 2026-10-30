"""Build pinned diagnostic FATX841 from exact installed source baseline."""
import datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/home/paul/xbox-windows-native/boot720841-source002');O=Path('/mnt/c/xwn841/driver002')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r={'passed':False,'physical_access':False,'space':require_space(B,21.5)};O.mkdir(parents=True)
def save():(K/'driver002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 src=B/'fatx';tree=read(K/'source001.json')['trees']['fatx'];assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(src),'diff','--name-only'])
 lock=read(W/'outputs/fatx-directory-order/inputs.json');rosbe=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
 for n,h in lock['tool_sha256'].items():assert sha(rosbe/n)==h
 r['source_tree']=tree;r['tool_sha256']=lock['tool_sha256'];r['definitions']=lock['profiles']['fatx']['definitions']
 build=B/'driver-build';args=['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+k+'='+v for k,v in r['definitions'].items()]
 compile=['cmake','--build',str(build),'--target','vfatfs','--','-j4'];r['commands']=[args,compile]
 script='set -e\n'+shlex.join(args)+'\n'+shlex.join(compile)+'\n';(O/'commands.sh').write_text(script);save()
 with (O/'build.log').open('w') as log:subprocess.run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True,stdout=log,stderr=log,check=True,timeout=900)
 shutil.copyfile(build/'drivers/filesystems/vfatfs/vfatfs.sys',O/'xwnfatx.sys');r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()};r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('Diagnostic driver build:',r['passed'])
