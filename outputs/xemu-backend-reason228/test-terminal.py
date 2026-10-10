"""Compile the actual candidate terminal helper under C11 atomic adapters."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'terminal-test001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((k/'build002.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
p=k/'artifacts/build002/source/hw/xbox/nv2a/nv2a.c';manifest=json.loads((k/'candidate002-source-pins.json').read_text());assert sha(p)==manifest['hw/xbox/nv2a/nv2a.c']
s=p.read_text();start=s.index('void nv2a_preserve227_finish(');end=s.index('\nstatic void nv2a_realize',start)
helper=s[start:end];assert 'qatomic_cmpxchg' in helper and 'expected, 7' in helper
out=k/'artifacts/terminal-test001';out.mkdir(exist_ok=False)
(out/'terminal-actual.inc').write_text(helper);(out/'test-terminal.c').write_bytes((k/'test-terminal.c').read_bytes())
results=[]
for level in ['0','2']:
 exe=out/('terminal-O'+level)
 command=['gcc','-std=c11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',str(out/'test-terminal.c'),'-o',str(exe)]
 result=subprocess.run(command,capture_output=True,text=True,timeout=120);assert result.returncode==0,result.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);assert run.returncode==0 and not run.stderr,run.stderr
 assert 'checks=100390 concurrent_pairs=100000 ' in run.stdout,run.stdout
 results.append(dict(command=command,compile_exit=result.returncode,exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,executable_sha256=sha(exe)))
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),test_sha256=sha(k/'test-terminal.c'),compiled_source_sha256=sha(p),actual_helper_sha256=sha(out/'terminal-actual.inc'),runs=results,scope='Actual compiled helper byte extraction with C11 atomic adapters, injected interleavings and concurrent timeout/publication pairs. No GPU or guest qualification.'),indent=2)+'\n')
print('Actual terminal helper O0/O2 atomic race checks PASS')
