"""Prepare new host controllers, not guest fixtures or launches."""
from pathlib import Path
import hashlib,json
k=Path(__file__).resolve().parent;old=k.parent/'texture-boundary278';pins={}
for name in ['protocol.py','model.py','objects.py','oracle.py','graph_base.py','graph_extra.py','terminal.py','atomic_json.py']:
 p=k/name;assert not p.exists();p.write_bytes((old/name).read_bytes());pins[name]=hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['trace.py','prepare.py','Run.ps1','audit.py','analyze-disk-delta.py']:
 s=(old/name).read_text().replace("case=='emu001'","case in ('control001','candidate001')").replace("[ValidateSet('emu001')]","[ValidateSet('control001','candidate001')]")
 s=s.replace('xwn278','xwn282').replace('4784','4824').replace('4785','4825').replace('texture-boundary278','release-pair282').replace('Consumed278','Consumed282')
 if name=='prepare.py':
  s=s.replace('boundary278-build002/xemu-boundary278.exe','runtime281-build001/xemu-runtime281.exe').replace('dcc08133f6627f387da3a584ba9eed2bdbac73e3cb3fcb19d1edb78c05e1ac93','1e42e331771f34199e3895dfecb5f6560d416723b1b2092671ab456e11b8176c')
  s=s.replace('release_installed=False',"release_installed=case.startswith('candidate')").replace("Prepared unique278 child","Prepared unique282 child")
  s=s.replace('out.mkdir();root.mkdir',"assert case=='control001' or json.loads((k/'control001/final-review.json').read_text())['scoped_unchanged_guest_reuse_passed']\nassert json.loads((k/'preflight001.json').read_text())['passed']\nout.mkdir();root.mkdir")
 if name=='trace.py':s=s.replace('release_installed=False',"release_installed=case.startswith('candidate')")
 p=k/name;assert not p.exists();p.write_bytes(s.encode());pins[name]=dict(parent_sha256=hashlib.sha256((old/name).read_bytes()).hexdigest(),generated_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
for name in ['decode.py','transport.py']:
 p=k/name;assert not p.exists();p.write_bytes((k.parent/'release-worker280'/name).read_bytes());pins[name]=hashlib.sha256(p.read_bytes()).hexdigest()
s=(old/'proof.py').read_text();s=s[:s.index('def qualify(')].replace('from decode import validate_graph','from decode import validate_graph').replace('from backend import validate_report,numbers','from backend import numbers')
(k/'proof.py').write_bytes(s.encode())
s=(k.parent/'unbound-release279/review.py').read_text();s=s[s.index('def inspect('):s.index("if __name__=='__main__':")]
s='import graph_base,graph_extra\nfrom decode import validate_graph\n'+s.replace('proof.validate_graph(g,1,allocations)','validate_graph(g,1,allocations,False)')
(k/'edges.py').write_bytes(s.encode())
(k/'controller-lineage.json').write_text(json.dumps(pins,indent=2)+'\n')
