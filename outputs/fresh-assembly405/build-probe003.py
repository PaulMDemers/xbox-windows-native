import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn405/probe-build003');assert not P.exists() and os.environ.get('XWN_BUILD_LEASE')=='held';P.mkdir()
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
rows=[]
for name,source,libs,extra in [('probe.exe','probe003.c',['kernel32','user32','advapi32','gdi32','winmm','ws2_32'],[])]:
    cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0',*extra,'-o',str(P/name),str(K/source)]+['-l'+v for v in libs]
    with (P/(name+'.log')).open('xb') as f:ret=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
    row=dict(name=name,source_sha256=sha(K/source),command=cmd,exit_code=ret);rows.append(row)
    if not ret:row.update(path=str(P/name),sha256=sha(P/name))
    (K/'probe-build003.json').write_text(json.dumps(rows,indent=2)+'\n');assert not ret
print('Bounded installation and post-install witnesses compiled')
