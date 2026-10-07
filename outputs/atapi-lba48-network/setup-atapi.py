"""Prepare a fresh ordinary control/candidate kit; only ATAPI differs."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'nvnet-shutdown-network';new=k.parent/'atapi-lba48-network'
assert not new.exists();new.mkdir();(new/'artifacts').mkdir()
skip={'REPORT.md','NEXT.md','pair-review.json','fixture-control001.json','fixture-candidate001.json'}
for p in old.iterdir():
    if not p.is_file() or p.name in skip:continue
    data=p.read_bytes()
    # Preserve helper, compiler command and implementation provenance exactly.
    if p.name in ['common.py','prepare.py','Run.ps1','preflight.py','supervise.py','audit.py',
                  'configuration.py','cold-map.py','record-closure.py','verify-evidence.py',
                  'verify-network.py','verify-pair.py','network-server.py']:
        data=data.replace(b'nvnet-shutdown-network',b'atapi-lba48-network')
    (new/p.name).write_bytes(data)
for name in ['probe.exe','nvnet-candidate001.sys']:
    (new/'artifacts'/name).write_bytes((old/'artifacts'/name).read_bytes())
(new/'atapi-review.json').write_bytes((k/'build-review.json').read_bytes())
(new/'atapi-host-tests.json').write_bytes((k/'host-tests.json').read_bytes())
p=new/'common.py';s=p.read_text().replace("'nvnetnt5.sys','ndis.sys'", "'nvnetnt5.sys','atapi.sys','ndis.sys'");p.write_text(s)
p=new/'prepare.py';s=p.read_text().replace("read(k/'nvnet-review.json')[case]", "read(k/'nvnet-review.json')['candidate001']")
needle="nvnet_before=nvnet_row['sha256'];m.replace(w,nvnet_row['path'],nvnet.read_bytes());nvnet_row['sha256']=sha(nvnet)"
assert needle in s
s=s.replace(needle,needle+"\natapi=read(k/'atapi-review.json');ar=next(row for row in protected if row['volume']=='F' and row['path']=='winnt/system32/drivers/atapi.sys');assert ar['sha256']==atapi['source_sha256']\nif case=='candidate001':\n    ap=k.parent/'atapi-dump-lba48/artifacts/atapi-candidate0105.sys';assert sha(ap)==atapi['candidate_sha256'];m.replace(w,ar['path'],ap.read_bytes());ar['sha256']=sha(ap)")
s=s.replace('Only rebuilt NVNet control/candidate differs.', 'Both use NVNet0104; only ATAPI dump selector differs.')
p.write_text(s)
p=new/'preflight.py';s=p.read_text().replace("read(k/'nvnet-review.json')[case]", "read(k/'nvnet-review.json')['candidate001']")
s=s.replace("paths=['probe.c'", "atapi=read(k/'atapi-review.json');assert read(k/'atapi-host-tests.json')['passed'];assert sha(k.parent/'atapi-dump-lba48/artifacts/atapi-candidate0105.sys')==atapi['candidate_sha256']\nassert next(v['sha256'] for v in f['protected'] if v['path']=='winnt/system32/drivers/atapi.sys')==atapi['candidate_sha256' if case=='candidate001' else 'source_sha256']\npaths=['atapi-review.json','atapi-host-tests.json','setup-atapi.py','probe.c'")
p.write_text(s)
p=new/'verify-pair.py';s=p.read_text().replace('ordinary NVNet comparison', 'ordinary ATAPI comparison').replace("diff==['F/winnt/system32/drivers/nvnetnt5.sys']", "diff==['F/winnt/system32/drivers/atapi.sys']");p.write_text(s)
(new/'setup-atapi.py').write_bytes(Path(__file__).read_bytes())
print('Fresh matched ordinary kit; no drivers built or guests launched here.')
