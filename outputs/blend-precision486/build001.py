"""Compile private characterization and controller with pinned RosBE; no execution."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/blend-precision486-runner-build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
assert shutil.disk_usage(P.parent).free-16*1024**2>=20*1024**3
P.mkdir();rows=[]
for stem,exe,receipt,libs in [('precision','d3d.exe','sample-build001.json',['kernel32','user32','gdi32']),('runner','run486.exe','build001.json',['kernel32','user32','advapi32'])]:
    out=K/receipt;assert not out.exists();shutil.copyfile(K/(stem+'.c'),P/(stem+'.c'))
    cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',str(P/(stem+'.d')),'-o',str(P/exe),str(P/(stem+'.c'))]+['-l'+lib for lib in libs]
    r=dict(command=cmd,compiler=str(cc),compiler_sha256=sha(cc),source_sha256=sha(P/(stem+'.c')),host_execution=False)
    with (P/(stem+'.log')).open('xb') as f:r['exit_code']=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
    r['log_sha256']=sha(P/(stem+'.log'))
    if r['exit_code']==0:
        deps=(P/(stem+'.d')).read_text().replace('\\\n','').split(': ',1)[1].split()
        r['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/(stem+'.c')}
        r.update(executable_sha256=sha(P/exe),executable_bytes=(P/exe).stat().st_size)
        rows.append(dict(path=str(P/exe),sha256=sha(P/exe),bytes=(P/exe).stat().st_size))
        if stem=='runner':r['rows']=list(reversed(rows))
    out.write_text(json.dumps(r,indent=2)+'\n');assert r['exit_code']==0
print('Private arithmetic sample and restart controller compiled.')
