"""Derive a new unique diagnostic harness without touching any completed attempt."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'hal-dump-path'
names=['probe.c','Build.ps1','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','configuration.py','check-oracle.py','review.py','record-closure.py','verify-evidence.py','atomic_json.py']
for n in names:
    s=(p/n).read_text().replace('hal-dump-path','dump-fsctl-trace').replace('xwnhd01','xwndf01')
    s=s.replace("['control001','candidate001']","['trace001']").replace("['mode0','mode0b','control001','candidate001']","['trace001']")
    s=s.replace("[ValidateSet('control001','candidate001')][string]$Case='control001'","[ValidateSet('trace001')][string]$Case='trace001'")
    s=s.replace("hal_review[case]","hal_review['candidate001']").replace("read(k/'hal-review.json')[case]","read(k/'hal-review.json')['candidate001']")
    if n=='preflight.py':
        start=s.index("if case=='candidate001':");end=s.index("assert sha(k/'build-review.json')",start);s=s[:start]+s[end:]
        start=s.index('paths+=');end=s.index('\nr=dict',start)
        s=s[:start]+"paths+=['hal-review.json','trace.py','review-sites.py','sites.json','modules.json','layouts.json','atomic_json.py','setup-kit.py']"+s[end:]
    if n in ['prepare.py','preflight.py','audit.py']:s=s.replace('debugger=False','debugger=True,ordinary_qualified=False')
    if n=='supervise.py':s=s.replace("assert not report_path.exists()","assert not report_path.exists()\nassert (k/'trace-armed.signal').exists(), 'Arm tracer before the single launch'")
    if n=='audit.py':
        start=s.index("r['limits']=");end=s.index("\nif r.get",start)
        s=s[:start]+"r['limits']='One bounded debugger diagnostic with candidate0102 HAL and unchanged FATX0101/video0093; no debugger result is ordinary or physical qualification. No event gate is waived or real crash-dump write qualified.'"+s[end:]
    target=k/n;assert not target.exists();target.write_text(s)
for n in ['hal-review.json']:(k/n).write_bytes((p/n).read_bytes())
(k/'layouts.json').write_bytes((k.parent/'dump-usage-trace/layouts.json').read_bytes())
