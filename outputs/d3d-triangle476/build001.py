"""Build namespace-only children of qualified471 boot diagnostic and455 runner."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn476/build001');P=Path('/mnt/c/xwn471/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-64*1024**2>=20*1024**3
parent=json.loads((K.parent/'busy-handoff471/build001.json').read_text())
for n,v in parent['files'].items():assert sha(Path(n))==v['sha256'],n
assert json.loads((K.parent/'d3d-triangle474/final-review.json').read_text())['scoped_triangle_passed']
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc');assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
source=(P/'xbeboot.S').read_text().replace('471','476');assert source.replace('476','471')==(P/'xbeboot.S').read_text()
runner=(K/'runner.c').read_text();assert runner.replace('476','474').replace('Owned physical Xbox Windows fixture only','Owned NT5 PC fixture only').replace('C:'+chr(92)*2+'xwn474-kit'+chr(92)*2+'d3d.exe','A:'+chr(92)*2+'D3D.EXE')==(K.parent/'d3d-triangle474/runner.c').read_text()
O.mkdir(parents=True);(O/'xbeboot.S').write_text(source);(O/'runner.c').write_text(runner)
for n in ['xbe.S','font.S','payload.bin']:shutil.copyfile(P/n,O/n)
r=dict(status='building',exit_code=None,physical_access=False,source_namespace_only=True,runner_namespace_only=True,parent_sha256=parent['sha256'],commands=[],compiler_sha256=sha(cc))
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
def run(cmd):
 r['commands'].append(cmd)
 with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=f,check=True,timeout=180)
save()
try:
 run(['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
 run(['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf']);run(['objcopy','-O','binary','wrapper.elf','wrapper.bin'])
 symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True);(O/'symbols.txt').write_text(symbols)
 sym={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3};assert sym==parent['wrapper_symbols']
 old=(P/'default.xbe').read_bytes();prefix=(O/'wrapper.bin').read_bytes();assert len(prefix)==0x3000
 xbe=bytearray(prefix+old[0x3000:]);xbe[:4096]=old[:4096]
 normalized=bytes(xbe[4096:0x3000]).replace(b'476',b'471').replace(struct.pack('<I',0x47600101),struct.pack('<I',0x47100101))
 assert normalized==old[4096:0x3000] and xbe[0x3000:]==old[0x3000:]
 xbe[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(xbe)-4096)+xbe[4096:]).digest();(O/'default.xbe').write_bytes(xbe)
 run([str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF','headers.d','-o','run476.exe','runner.c','-lkernel32','-luser32','-ladvapi32'])
 sample=Path('/home/paul/xbox-windows-native/d3d-triangle474-runner-build001/d3d.exe');assert sha(sample)=='eee41bde74531434f777b5b0bd98784d0e56d5e992c7d541c91fe5f05848be59';shutil.copyfile(sample,O/'d3d.exe')
 deps=(O/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split();r['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n).is_absolute()}
 r.update(status='compiled',exit_code=0,sha256=sha(O/'default.xbe'),bytes=len(xbe),payload_byte_exact=True,wrapper_symbols=sym,rows=[dict(path=str(O/n),sha256=sha(O/n),bytes=(O/n).stat().st_size) for n in ['run476.exe','d3d.exe']])
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
