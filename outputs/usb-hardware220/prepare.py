"""Freeze host trial controller and previously reviewed USB207 binary; no network."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;repo=K.parents[1];prev=K.parent/'usb-identification207'
canon=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
dest=K/'prepared.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
git=['C:/Program Files/Git/cmd/git.exe','-c','safe.directory='+repo.as_posix(),'-C',str(repo)]
assert subprocess.check_output(git+['branch','--show-current'],text=True).strip()=='codex/xbox-native-usb'
assert subprocess.check_output(git+['remote','get-url','origin'],text=True).strip()=='https://github.com/PaulMDemers/xbox-windows-native.git'
for p in K.glob('*.py'):ast.parse(p.read_text())
build=read(prev/'build-review.json');exe=prev/build['binary']
assert build['passed'] and sha(exe)==build['binary_sha256'] and sha(prev/'probe.c')==build['source_sha256']
assert read(prev/'emu003/audit.json')['descriptor_scope_observed']
completed=subprocess.run([sys.executable,'-B',str(K/'test-controller.py')],capture_output=True,text=True)
assert completed.returncode==0,completed.stdout+completed.stderr
files=list(K.glob('*.py'))+[prev/n for n in ['probe.c','analyze.py','build-review.json','emu003/audit.json','owned-provider-review.json','package-review.json']]+[exe]
files += [canon/'outputs'/n for n in ['device-hardware220/HANDOFF.md','device-hardware220/queue.py','video-upload-runtime211/capture.json','native-windows-physical-f/physical-cache-preflight.json','native-windows-physical-f/decode-legacy-events.py']]
r=dict(prepared=True,physical_access=False,physical_tested=False,driver_installed=False,binary=str(exe),
    binary_sha256=sha(exe),pins={str(p):sha(p) for p in files},offline_fault_checks=5,
    test_output=completed.stdout+completed.stderr,
    gates='Queue predecessor closed/USB claimed; actual incoming bytes; before-hive audit; one launch; startup-first collection; post-hive audit; exact restore and dashboard readback before close.',
    report=str(K/'REPORT.md'),limits='Descriptor-only existing-stack trial. Manual normal restart. Unbound XID reports unavailable; no replacement controller driver.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Frozen USB220 physical-trial inputs; five offline fault checks passed; no console access')
