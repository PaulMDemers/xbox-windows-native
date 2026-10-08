"""Preserve failed160 and create a unique reconstruction; never modify its child."""
import datetime,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-physical-rehearsal160'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failure=old/'preparation-failure.json';assert not failure.exists()
partial=ws/'outputs/native-windows-fatx-forensics/artifacts/video-physical-rehearsal160-control001.qcow2'
failure.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    case='control001',closed=True,session=98842,exit_code=1,stage='offline fixture restoration',
    error="KeyError: 'xboxvnt5.pre-dim'",cause='Existing-only replace helper used on absent archived backup file.',
    prepare_source_sha256=sha(old/'prepare.py'),partial_qcow_sha256=sha(partial),
    guest_launched=False,physical_writes=False,never_relaunch_or_reprepare=True),indent=2)+'\n',encoding='utf-8')
text=(old/'prepare.py').read_text(encoding='utf-8').replace('rehearsal160','rehearsal161')
text=text.replace("from allocation import scan", "from allocation import scan\nfrom restore import restore")
text=text.replace("inputs=read(k/'inputs.json')", "inputs=read(k.parent/'video-physical-rehearsal160/inputs.json')")
text=text.replace("(k/'artifacts',inputs['files'])", "(k.parent/'video-physical-rehearsal160/artifacts',inputs['files'])")
text=text.replace("c.m.replace(w,", "restore(w,")
text=text.replace("assert c.m.sha(rr[v].read(path))==digest", "assert c.m.sha(rr[v].read(path))==digest")
text=text.replace("sha(k/'inputs.json')", "sha(k.parent/'video-physical-rehearsal160/inputs.json')")
text=text.replace("write_text(json.dumps(r,indent=2)+'\\n')", "write_text(json.dumps(r,indent=2)+'\\n',encoding='utf-8')")
(k/'prepare.py').write_text(text,encoding='utf-8')
(k/'DESIGN.md').write_text((old/'DESIGN.md').read_text(encoding='utf-8')+'\n\n161 corrects only the offline restoration helper: absent files are created, files\nthat fit retain allocation, and larger files receive a new verified chain. The\nfailed160 child is preserved and never launched. Host writer tests do not qualify\nguest FATX or power-loss behavior. Both preparation targets are unique.\n',encoding='utf-8')
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in [
    k/'prepare.py',k/'restore.py',k/'test-restore.py',k/'restore-tests.json',
    old/'inputs.json',k.parent/'video-physical-review159/capture.json',
    k.parent/'video-physical-review159/binding-edit.json',
    k.parent/'video-hardware-candidate158/package-review.json',
    k.parent/'video-next/probe-v3/gdi-probe.c',k.parent/'video-next/probe-v3/build-review.json',
    k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe',
    k.parent/'video-trace-reuse-settled/runner.c',k.parent/'video-trace-reuse-settled/artifacts/runner.exe',
    k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe']}
(k/'frozen-inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print('Failed160 preserved; new161 preparation sources pinned')
