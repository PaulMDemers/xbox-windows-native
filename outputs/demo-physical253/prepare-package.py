"""Freeze exact previously exercised binaries; never build a new driver for this integration."""
from common001 import *
import ast
dest=k/'package.json';assert not dest.exists()
assert read(canonical/'outputs/demo-integration251/emu001/combined-review.json')['scoped_combined_passed']
assert read(canonical/'outputs/demo-physical252/install001/audit.json')['scoped_installation_passed']
assert read(k/'binding-edit.json')['passed']
video=read(canonical/'outputs/video-text-oracle206/package-review.json')['cases']['candidate001']
root=k/'artifacts/payload';root.mkdir(exist_ok=False)
sources={
 'runner.exe':canonical/'outputs/demo-integration251/artifacts/build001/runner.exe',
 'wizard.exe':canonical/'outputs/setup-wizard-automation201/artifacts/build006/wizard.exe',
 'replay.exe':canonical/'outputs/video-text-oracle206/artifacts/replay.exe',
 'state.exe':canonical/'outputs/demo-physical252/artifacts/payload/verify/state.exe',
 'probe.exe':canonical/'outputs/demo-physical252/artifacts/payload/verify/probe.exe'}
expected=read(canonical/'outputs/demo-integration251/emu001/fixture.json')['helpers']
helpers=[]
for name,p in sources.items():
    data=p.read_bytes();assert sha(data)==expected[name];(root/name).write_bytes(data)
    helpers.append(dict(name=name,source=str(p),sha256=sha(data),bytes=len(data)))
rows=[]
for row in video:
    p=canonical/row['source'];data=p.read_bytes();assert sha(data)==row['sha256'];(root/p.name).write_bytes(data)
    rows.append(dict(path='/'+row['target'],name=p.name,sha256=sha(data),bytes=len(data),source=row['source']))
proposal=(k/'artifacts/proposed-system').read_bytes();assert sha(proposal)==read(k/'binding-edit.json')['after_sha256']
save(dest,dict(video=rows,helpers=helpers,proposed_system_sha256=sha(proposal),physical_qualified=False,strict_qualification_passed=False))
frozen={}
dependencies=[canonical/'outputs/video-text-oracle206'/name for name in ['runner_analysis.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py']]
dependencies += [canonical/'outputs/native-windows-fatx-preflight'/name for name in ['analyze.py','artifacts/default.xbe']]
dependencies += [canonical/'outputs/native-windows-physical-f/decode-legacy-events.py',canonical/'outputs/native-windows-nt5-kernel/nt5_hive_indexes.py']
for p in [*k.glob('*.py'),k/'PLAN.md',k/'package.json',k/'capture002.json',k/'providers001.json',k/'before-audit002.json',k/'binding-edit.json',k/'artifacts/proposed-system',*root.iterdir(),*dependencies,canonical/'outputs/demo-integration251/emu001/combined-review.json',canonical/'outputs/demo-physical252/install001/audit.json']:
    if p.suffix=='.py':ast.parse(p.read_text())
    frozen[str(p)]=sha(p.read_bytes())
save(k/'frozen001.json',frozen)
print('Combined physical payload and fresh audio-preserving binding pinned')
