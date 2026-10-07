"""Collect the owned aligned installer diagnostic once, after runner cleanup."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())

def collect(case):
    run=ws/('work/runs/nt5-fatx-install-draw-'+case)
    assert (run/'cleanup.json').exists(), 'Cold collection requires owned cleanup'
    out=k/case
    manifest=out/'collection.json'
    r=read(manifest) if manifest.exists() else dict(case=case,physical_access=False,stages={})
    stages=[('audit','audit.py','audit.json'),('allocation','audit-allocation.py','allocation.json'),('package','audit-package.py','package-audit.json'),('alignment','audit-alignment.py','alignment.json'),('layout','compare-layout.py','layout-comparison.json'),('drawing','audit-drawing.py','drawing-audit.json')]
    for name,script,output in stages:
        target=out/output
        if target.exists():
            # Existing evidence is never rerun by the collector; parse it or stop.
            read(target)
            r['stages'].setdefault(name,dict(adopted_existing=True,output=output))
        else:
            script_path=(k/script).resolve()
            if sys.platform=='win32':
                posix='/mnt/'+script_path.drive[0].lower()+script_path.as_posix()[2:]
                cmd=['wsl','-d','Ubuntu','--','env',
                     'LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu',
                     'python3',posix,case]
            else:cmd=[sys.executable,str(script_path),case]
            subprocess.run(cmd,check=True)
            read(target)
            r['stages'][name]=dict(output=output,completed=True)
        r['stages'][name]['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(r,indent=2)+'\n')
    print('Cold collection complete for '+case)

if __name__=='__main__':
    assert len(sys.argv)==3 and sys.argv[1]=='collect' and sys.argv[2] in ['001','002'];collect(sys.argv[2])
