"""Require179 closure/configuration and byte-identical helper/providers before preparing180."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'device-unused-package179';dest=k/'input-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(old/'candidate001/closure.json')['closed'] and read(old/'candidate001/package-verification.json')['configuration_observed']
same={}
for n in ['runner.c','gdi-probe.c','restart_gate.h','test-gate.c','xwnunused179.inf','artifacts/runner.exe','artifacts/gdi-probe.exe','artifacts/host-gate']:
 assert (k/n).read_bytes()==(old/n).read_bytes(),n;same[n]=sha(k/n)
for row in read(k/'sites.json')['binaries'].values():assert sha(ws/row['path'])==row['sha256']
for p in k.glob('*.py'):ast.parse(p.read_text())
r=dict(passed=True,physical_access=False,debugger=False,prior_configuration_sha256=sha(old/'candidate001/package-verification.json'),prior_closure_sha256=sha(old/'candidate001/closure.json'),reused_exact_builds=same,
 no_new_setup_action=True,no_inf_restage=True,no_diagnostic_reset=True,strict_events_unchanged=True,
 limits='Independent subsequent boot from normally shut down179 state; explicit unused-device configuration retained, audio/SMBus remain unsupported.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Subsequent-boot source/providers and exact prior configuration reviewed')
