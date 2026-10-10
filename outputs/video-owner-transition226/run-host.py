"""One fresh bounded host/native-compile case. No guest or hardware access."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host001.json';assert not dest.exists()
assert shutil.disk_usage('/mnt/c').free>=20*1024**3
art=k/'artifacts/host001';art.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,host_only=True,guest_launch=False,physical_access=False,native_grants=0,
 source_sha256=sha(Path(__file__)),pins={},runs=[])
for n in ['owner.c','owner.h','test.c']:
 q=art/n;q.write_bytes((k/n).read_bytes());r['pins'][n]=sha(q)
cc=Path(shutil.which('gcc')).resolve();r['compiler']=dict(path=str(cc),sha256=sha(cc))
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:abort_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
try:
 for optimize in ['-O0','-O2']:
  exe=art/('host'+optimize[-1]);cmd=[str(cc),'-std=c11',optimize,'-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(art/'owner.c'),str(art/'test.c'),'-o',str(exe)]
  build=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
  row=dict(command=cmd,compile_exit=build.returncode,compile_stdout=build.stdout,compile_stderr=build.stderr);r['runs'].append(row);assert build.returncode==0
  trial=subprocess.run([str(exe)],env=env,capture_output=True,text=True,timeout=60)
  row.update(binary_sha256=sha(exe),exit_code=trial.returncode,stdout=trial.stdout,stderr=trial.stderr)
  assert trial.returncode==0 and not trial.stderr and 'native_grants=0' in trial.stdout
 native=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
 assert sha(native)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
 obj=art/'owner-i686.o';cmd=[str(native),'-std=c99','-O2','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(art/'owner.c'),'-o',str(obj)]
 build=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
 r['native_compile']=dict(command=cmd,compiler_sha256=sha(native),exit_code=build.returncode,stdout=build.stdout,stderr=build.stderr)
 assert build.returncode==0
 nm=native.parent/'i686-w64-mingw32-nm';symbols=subprocess.check_output([str(nm),'-u',str(obj)],text=True)
 r['native_compile'].update(object_sha256=sha(obj),nm_sha256=sha(nm),undefined_symbols=symbols)
 assert not symbols.strip();r['passed']=True
except Exception as exc:r['error']=repr(exc);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('226 host ASan/UBSan ordering/ranges PASS; import-free RosBE i686 compile PASS; no native ownership grant')
