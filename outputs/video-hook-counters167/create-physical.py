"""New candidate-only physical counter diagnostic; no FTP or launch here."""
import ast
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-paired-timing166'
assert not (k/'physical-controller.py').exists()
for name in ['physical-controller.py','audit-physical.py','audit-physical-hives.py','verify-restored.py','watch-physical.py']:
    s=(old/name).read_text(encoding='utf-8').replace("['control001','candidate001']","['candidate001']")
    s=s.replace('current-rollback166.zip','current-rollback167.zip')
    if name=='physical-controller.py':
        s=s.replace("namespace='xwnvt166a' if case=='control001' else 'xwnvt166b'","namespace='xwnvh167'")
        s=s.replace("rollback_dir='xwn-display166a' if case=='control001' else 'xwn-display166b'","rollback_dir='xwn-display167'")
        s=s.replace("k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe'","k/'artifacts/gdi-probe.exe'")
        s=s.replace("==review['sha256']","==review['binaries']['runner.exe']['sha256']")
        s=s.replace("==review['probe_sha256']","==review['binaries']['gdi-probe.exe']['sha256']")
        s=s.replace("k/'control001/physical-audit.json'","k.parent/'video-paired-timing166/control001/physical-audit.json'")
        s=s.replace("k/'control001/restored-verification.json'","k.parent/'video-paired-timing166/control001/restored-verification.json'")
        s=s.replace("k/'control001/physical-hive-audit.json'","k.parent/'video-paired-timing166/control001/physical-hive-audit.json'")
        s=s.replace("k/'control001/audit.json'","k.parent/'video-paired-timing166/control001/audit.json'")
        s=s.replace("        assert r['workload_passed'] and r['integrity_passed'] and not r['strict_qualification_passed']", "        assert r['workload_passed'] and r['integrity_passed'] and not r['strict_qualification_passed']\n        assert all(v['counters_passed'] for v in r['samples'])\n        assert read(k/'emulator-counters.json')['counter_coverage_passed']")
    ast.parse(s);(k/name).write_bytes(s.encode('utf-8'))
print('Fresh physical diagnostic controller; emulator evidence required before eligibility')
