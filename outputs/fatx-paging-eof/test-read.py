"""Compile actual old/new common-read functions with bounded I/O mocks on the host."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'artifacts';out.mkdir(exist_ok=True)
harness=(k/'read-harness.c').read_text();results=[]
for label,build in [('old','video-surface-lifecycle-001'),('fixed','fatx-paging-eof-001')]:
    p=Path('/home/paul/xbox-windows-native/build')/build/'source/drivers/filesystems/vfatfs/rw.c';s=p.read_text()
    function=s[s.index('NTSTATUS\nVfatCommonRead('):s.index('\nVOID\nNTAPI\nVfatStackOverflowRead(')]
    c=out/('read-'+label+'.c');exe=out/('read-'+label);c.write_text(harness.replace('/* INSERT_ACTUAL_FUNCTION */',function))
    subprocess.run(['gcc','-std=c99','-O2','-Wall',str(c),'-o',str(exe)],check=True)
    result=subprocess.run([str(exe)],capture_output=True,text=True)
    row=json.loads(result.stdout);row.update(label=label,source_sha256=hashlib.sha256(function.encode()).hexdigest(),returncode=result.returncode);results.append(row)
assert results[0]['failures']>0 and results[1]['failures']==0
r=dict(scope=__doc__,passed=True,results=results,
       compiler_version=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],
       harness_sha256=hashlib.sha256(harness.encode()).hexdigest(),
       limits='Source-level host build, not NT ABI, disk I/O, cache manager or concurrency. Guards surround the requested buffer; short completion, I/O failure and non-file stream exclusions exercised.')
(k/'compiled-read-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
