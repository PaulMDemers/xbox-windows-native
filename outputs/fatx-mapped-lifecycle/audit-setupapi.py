"""Verify exact original SetupAPI identity in immutable and closed owned disks."""
import importlib,json,sys,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002']
out=k/case;dest=out/'setupapi-identity.json';assert not dest.exists()
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
f=json.loads((k/('fixture-'+case+'.json')).read_text());base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert m.filehash(base)==f['fixture_sha256']
run=ws/('work/runs/nt5-fatx-mapped-lifecycle-'+case);assert (run/'cleanup.json').exists()
site=out/'sites-source.json' if (out/'sites-source.json').exists() else k/'sites.json'
review=json.loads(site.read_text());m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
rows=[]
for disk in [base,run/'hdd.qcow2']:
    with ColdIO(disk) as io:data=m.Writer(io,m.fatx.open_partition(io,disk,'F')).read('winnt/system32/setupapi.dll')
    digest=hashlib.sha256(data).hexdigest();rows.append(dict(disk=disk.name,sha256=digest,matched=digest==review['setupapi_sha256']))
r=dict(physical_access=False,read_only=True,checks=rows,matched=all(v['matched'] for v in rows),sites_sha256=hashlib.sha256(site.read_bytes()).hexdigest())
dest.write_text(json.dumps(r,indent=2)+'\n');assert r['matched'];print('Before/after SetupAPI exact identity verified')
