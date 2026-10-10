"""Preserve exact read-only emulator source leads for the next design review."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;report=k/'transfer-source-preservation.json';assert not report.exists()
base=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
r=json.loads((k/'transfer-source-leads.json').read_text());assert r['passed']
out=k/'artifacts/transfer-leads211';out.mkdir(exist_ok=False)
pins={}
for name,row in r['files'].items():
 data=(base/name).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];pins[name]=row['sha256']
result=dict(passed=True,guest_launch=False,physical_access=False,source_pins=pins,
 inventory_sha256=hashlib.sha256((k/'transfer-source-leads.json').read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 limits='Read-only model sources preserved privately, no code borrowing, new register writes, DMA experiment or GPU/hardware qualification.')
report.write_text(json.dumps(result,indent=2)+'\n');print('Private transfer lead sources preserved:',len(pins))
