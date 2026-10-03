import pathlib,subprocess,os
assert os.environ.get('XWN_BUILD_LEASE')=='held'
root=pathlib.Path('/home/paul/xbox-windows-native');src=root/'sources/reactos'
kit=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-paging-v2')
p=src/'boot/freeldr/freeldr/ntldr/winldr.c'; original=p.read_text();p.write_text(original)
assert original.count('if (Width != 640 || Height != 480')==1
try:
 p.write_text(original.replace('if (Width != 640 || Height != 480','if (Width != 641 || Height != 480'))
 command='cmake --build '+str(root/'build/handoff')+' --target rosload -- -j4\n'
 with (kit/'build-logs/forced-guard.log').open('w') as log:
  subprocess.run([str(root/'toolchains/RosBE-2.2.1/RosBE.sh'),str(src),'0','i386'],input=command,text=True,stdout=log,stderr=subprocess.STDOUT,check=True)
 (kit.parent.parent/'work/paging-v2-forced-guard.exe').write_bytes((root/'build/handoff/boot/freeldr/freeldr/rosload.exe').read_bytes())
finally:
 p.write_text(original)
 subprocess.run(['bash',str(kit/'build.sh')],check=True)
print('Forced width-641 test binary saved separately; final width-640 source and package rebuilt.')
