"""Pin two closed standalone historical probes for verified offload; no QCOW chains."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'author-handoff225.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['storage-preflight-002','hardware-probe-002'];pins={}
for name in names:
 p=ws/'work/runs'/name
 assert json.loads((p/'cleanup.json').read_text())['completedUtc']
 with (p/'hdd.qcow2').open('rb') as f:header=f.read(24)
 assert header[:4]==b'QFI\xfb' and not any(header[8:20])
 pins[name]={key:sha(p/(key+'.json')) for key in ['cleanup','instance']}
parent=k/'Offload-Kernel032035.ps1';text=parent.read_text()
text=text.replace("manifest-kernel032035-20261010.json","manifest-handoff225-20261010.json")
a=text.index('$names=@(');b=text.index('$records=@()',a)
new="$names=@("+','.join("'"+n+"'" for n in names)+")\n$pinmap=@{\n"
for n,v in pins.items():new+=" '"+n+"'=@{cleanup='"+v['cleanup']+"';instance='"+v['instance']+"'}\n"
text=text[:a]+new+"}\n"+text[b:]
text=text.replace('outputs/video-gpu-handoff216/fixture-control001.json','outputs/video-loader-handoff225/fixture-trace001.json')
text=text.replace('two CLOSED historical standalone kernel032/035 runs','two CLOSED historical standalone storage-preflight/hardware-probe002 runs')
q=k/'Offload-Handoff225.ps1';assert not q.exists();q.write_text(text)
dest.write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),parent_sha256=sha(parent),script_sha256=sha(q),pins=pins,scope=__doc__,physical_access=False,guest_launch=False),indent=2)+'\n')
