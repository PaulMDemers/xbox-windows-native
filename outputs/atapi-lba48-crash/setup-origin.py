"""New sacrificial candidate crash, gated on the matched ordinary pair."""
import json
import sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'atapi-dump-address';new=k.parent/'atapi-lba48-crash'
assert not new.exists();new.mkdir();(new/'artifacts').mkdir()
names=['trigger.c','probe.c','Build.ps1','review.py','build-review.json','hal-review.json','fatx-review.json','nvnet-review.json','layouts.json','kernel-review.json','atomic_json.py','modules.json','modules-review.py','common.py','configuration.py','cold-map.py','prepare.py','Run.ps1','preflight.py','supervise.py','record-closure.py','audit-crash.py','trace.py','verify.py','Invoke-Lba.ps1']
for name in names:
    data=(old/name).read_bytes()
    if name.endswith(('.py','.ps1')) and name not in ['Build.ps1','review.py']:
        data=data.replace(b'atapi-dump-address',b'atapi-lba48-crash').replace(b'crash005',b'crash006')
    (new/name).write_bytes(data)
for name in ['probe.exe','trigger.sys']:(new/'artifacts'/name).write_bytes((old/'artifacts'/name).read_bytes())
(new/'atapi-review.json').write_bytes((k/'build-review.json').read_bytes())
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
mod=json.loads((new/'modules.json').read_text());binary=k/'artifacts/atapi-candidate0105.sys';p=pefile.PE(str(binary));review=json.loads((k/'build-review.json').read_text())
mod['atapi.sys'].update(path=str(binary.resolve()),sha256=review['candidate_sha256'],image_size=p.OPTIONAL_HEADER.SizeOfImage)
(new/'modules.json').write_text(json.dumps(mod,indent=2)+'\n')
sites=dict(divide_call=0x1359d,divide_return=0x135a2,dispatch_call=0x1360e,selector_entry=0x15800,
           extended_entry=0x258c,extended_decoded_lba=0x2633,extended_high_byte=0x2687,extended_command_call=0x270c)
(new/'address-review.json').write_text(json.dumps(dict(candidate_sha256=review['candidate_sha256'],sites=sites),indent=2)+'\n')
p=new/'prepare.py';s=p.read_text().replace("k.parent/'nvnet-shutdown-network/", "k.parent/'atapi-lba48-network/")
needle="row['sha256']=sha(np)\nw.flush()";assert needle in s
s=s.replace(needle,"""row['sha256']=sha(np)
ap=k.parent/'atapi-dump-lba48/artifacts/atapi-candidate0105.sys';ar=read(k/'atapi-review.json');assert sha(ap)==ar['candidate_sha256']
row=next(v for v in protected if v['volume']=='F' and v['path']=='winnt/system32/drivers/atapi.sys');assert row['sha256']==ar['source_sha256'];m.replace(w,row['path'],ap.read_bytes());row['sha256']=sha(ap)
w.flush()""")
p.write_text(s)
p=new/'preflight.py';s=p.read_text().replace("'review-address.py','address-review.json','registry-state.py','registry-state.json','DESIGN.md'", "'address-review.json','atapi-review.json','DESIGN.md'")
s=s.replace("for n,m in read(k/'modules.json').items():", "assert read(k.parent/'atapi-lba48-network/candidate001/audit.json')['strict_qualification_passed']\nassert read(k.parent/'atapi-lba48-network/control001/audit.json')['strict_qualification_passed']\nfor n,m in read(k/'modules.json').items():")
p.write_text(s)
(new/'setup-origin.py').write_bytes(Path(__file__).read_bytes())
print('Created crash006 kit. No fixture preparation or launch yet.')
