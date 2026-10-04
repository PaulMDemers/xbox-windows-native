from pathlib import Path
import subprocess,shlex,json,os
root=Path('/home/paul/xbox-windows-native');ws=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');build=root/'build/vfat-nt5-abi-research'
assert os.environ.get('XWN_BUILD_LEASE')=='held'
commands=subprocess.check_output([str(root/'toolchains/RosBE-2.2.1/bin/ninja'),'-C',str(build),'-t','commands','vfatfs'],text=True)
line=next(x for x in commands.splitlines() if '/vfatfs/iface.c' in x and ' -c ' in x);args=shlex.split(line)
args[args.index('-c')+1]=str(ws/'outputs/native-windows-fatx-runtime/fatx-abi.c');args[args.index('-o')+1]=str(ws/'outputs/native-windows-fatx-runtime/artifacts/fatx-abi.o')
# Dependencies must not update the original compilation target.
for opt in ['-MF','-MT']:
 if opt in args:i=args.index(opt);del args[i:i+2]
if '-MD' in args:args.remove('-MD')
subprocess.run(args,cwd=build,check=True)
subprocess.run([str(root/'toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-objcopy'),'-O','binary','--only-section=.rdata',str(ws/'outputs/native-windows-fatx-runtime/artifacts/fatx-abi.o'),str(ws/'outputs/native-windows-fatx-runtime/artifacts/fatx-abi.bin')],check=True)
