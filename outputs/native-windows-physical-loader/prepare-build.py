from pathlib import Path
import subprocess,os,hashlib,json
root=Path('/home/paul/xbox-windows-native');src=root/'sources/cromwell';build=root/'build/cromwell-physical-001'
out=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-loader')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not build.exists();build.mkdir()
base=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD']).decode().strip();assert base=='9fc54d0c7cbed7bc3c70373642d833684853011f'
archive=subprocess.Popen(['git','-C',str(src),'archive','HEAD'],stdout=subprocess.PIPE)
subprocess.run(['tar','-x','-C',str(build)],stdin=archive.stdout,check=True);archive.stdout.close();assert archive.wait()==0
patch=subprocess.check_output(['git','-C',str(src),'diff','--binary','HEAD']);(out/'cromwell-base.patch').write_bytes(patch)
subprocess.run(['patch','-p1'],cwd=build,input=patch,check=True)
p=build/'boot/BootResetAction.c';old=p.read_text();anchor='#ifdef XBOX_LINUX_AUTOBOOT_FATX'
block='#ifdef XWN_PHYSICAL_PREFLIGHT\n    {\n        CONFIGENTRY entry;\n        memset(&entry, 0, sizeof(entry));\n        entry.bootType = BOOT_FATX;\n        entry.bootSystem = SYS_REACTOS;\n        strcpy(entry.title, "XWN loader diagnostic");\n        strcpy(entry.szPath, "/Applications/XWNLoader/freeldr.sys");\n        printk("XWN: loading isolated E:/Applications/XWNLoader/freeldr.sys\\n");\n        BootFromDevice(&entry);\n        printk("XWN: loader failed. No fallback boot. Reboot to dashboard.\\n");\n        __asm__ __volatile__("cli");\n        for (;;) __asm__ __volatile__("hlt");\n    }\n#endif\n'
assert old.count(anchor)==1;p.write_text(old.replace(anchor,block+anchor))
import difflib
(out/'cromwell-fatx-preflight.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),p.read_text().splitlines(True),fromfile='a/boot/BootResetAction.c',tofile='b/boot/BootResetAction.c')))
(build/'.host-tools').mkdir();(build/'.host-tools/gcc').symlink_to('/usr/bin/gcc-12')
env=dict(os.environ,PATH=str(build/'.host-tools')+':'+os.environ['PATH'])
with (out/'build-logs/cromwell-physical.log').open('w') as log:
 subprocess.run(['make','all','CC=/usr/bin/gcc-12','GITREV=9fc54d0-xwn-fatx','EXTRA_CROM_CFLAGS=-DXWN_PHYSICAL_PREFLIGHT'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
import shutil
shutil.copyfile(build/'xbe/xromwell.xbe',out/'package/default.xbe')
shutil.copyfile(out.parent/'native-windows-build/artifacts/freeldr.sys',out/'package/freeldr.sys')
assert hashlib.sha256((out/'package/freeldr.sys').read_bytes()).hexdigest()=='e37214a54cd484b11ce832d01cfa0cf3ade6ba02af7bb03f152888650ff7947d'
print('Built isolated FATX Xromwell and copied verified XWN40 halt diagnostic.')
