import hashlib,json,subprocess
from pathlib import Path
p=Path('/mnt/c/xwn403/install-restore001');raw=p/'installed.raw';target=p/'refused.qcow2';assert raw.is_file() and not target.exists()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True)
r={'preserved_failure':'E contains factory TDATA/UDATA; no payload writes','virtual_bytes':raw.stat().st_size,'qcow_bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'virtual_equality_verified':True,'removed_only_verified_staging_raw':str(raw)}
assert raw.resolve()==Path('/mnt/c/xwn403/install-restore001/installed.raw');raw.unlink()
Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/release-readiness403/refusal-preservation001.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
