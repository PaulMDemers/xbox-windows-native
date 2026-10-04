from pathlib import Path
import subprocess,os,hashlib,json,shutil
root=Path('/home/paul/xbox-windows-native');src=root/'sources/cromwell';build=root/'build/cromwell-physical-f-001'
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f');old=k.parent/'native-windows-physical-loader'
assert os.environ.get('XWN_BUILD_LEASE')=='held';assert not build.exists();build.mkdir();(k/'build-logs').mkdir(exist_ok=True)
base=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip();assert base=='9fc54d0c7cbed7bc3c70373642d833684853011f'
archive=subprocess.Popen(['git','-C',str(src),'archive','HEAD'],stdout=subprocess.PIPE)
subprocess.run(['tar','-x','-C',str(build)],stdin=archive.stdout,check=True);archive.stdout.close();assert archive.wait()==0
patches=[(old/'cromwell-base.patch').read_bytes(),(old/'cromwell-fatx-preflight.patch').read_bytes().replace(b'XWNLoader',b'XWNFBoot')]
(k/'cromwell-f-launcher.patch').write_bytes(patches[1])
for patch in patches:subprocess.run(['patch','-p1'],cwd=build,input=patch,check=True)
(build/'.host-tools').mkdir();(build/'.host-tools/gcc').symlink_to('/usr/bin/gcc-12')
env=dict(os.environ,PATH=str(build/'.host-tools')+':'+os.environ['PATH'])
with (k/'build-logs/launcher.log').open('w') as log:subprocess.run(['make','all','CC=/usr/bin/gcc-12','GITREV=9fc54d0-xwn-fboot','EXTRA_CROM_CFLAGS=-DXWN_PHYSICAL_PREFLIGHT'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
target=k/'artifacts/default.xbe';shutil.copyfile(build/'xbe/xromwell.xbe',target)
(k/'launcher.json').write_text(json.dumps({'base':base,'base_patch_sha256':hashlib.sha256(patches[0]).hexdigest(),'patch_sha256':hashlib.sha256(patches[1]).hexdigest(),'xbe_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'loader_path':'E:/Applications/XWNFBoot/freeldr.sys'},indent=2)+'\n')
