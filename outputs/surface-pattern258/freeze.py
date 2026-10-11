"""Freeze actual source, explicit parser dependencies and helper pins before launch."""
import ast,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (k/'emulator-frozen.json').exists()
b=read(k/'build002.json');assert b['passed'] and read(k/'build-review002.json')['passed']
for n,h in b['input_pins'].items():assert sha(k/n)==h,n
spec=importlib.util.spec_from_file_location('arena',k/'analyze_arena.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
good=b'ALLOCATED_CPU_ONLY 1 2097152 16384\r\nEXACT_CPU_BYTES 0 16384 0\r\nEXACT_CPU_BYTES 1 16384 0\r\nEXACT_CPU_BYTES 2 16384 0\r\nCPU_COUNTS 3 2 0\r\nCOMPLETE_CPU_ONLY 49152 1 0\r\n'
assert a.analyze(good)['passed'];rejected=0
for raw in [good.replace(b'2097152',b'2097153'),good.replace(b'49152',b'49151'),good.replace(b'CPU_COUNTS 3',b'CPU_COUNTS 2'),good.replace(b'COMPLETE_CPU_ONLY',b'INCOMPLETE'),good+good,good[:-1]]:
 try:a.analyze(raw)
 except (AssertionError,ValueError):rejected+=1
 else:raise AssertionError('Invalid CPU result accepted')
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
r=dict(passed=True,parser_negative_cases=rejected,physical_access=False,guest_launch=False,gpu_reference_tested=False,build_sha256=sha(k/'build002.json'),fixture_sha256=f['fixture_sha256'])
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
pins={}
for p in k.rglob('*'):
 if p.is_file() and not any(v in p.parts for v in ['artifacts','__pycache__']):
  if p.suffix=='.py':ast.parse(p.read_text())
  pins[p.relative_to(ws).as_posix()]=sha(p)
for parent in ['installer-focus250','demo-integration251']:
 for n,h in read(k.parent/parent/'emulator-frozen.json').items():assert sha(ws/n)==h,n;pins[n]=h
for n in ['installer-focus250/diagnostic.py','video-resident-context222/analyze-log.py','video-fifo-retirement224/analyze-retirement.py','video-fifo-retirement224/host-include/ddk/ntddk.h']:
 p=k.parent/n;pins[p.relative_to(ws).as_posix()]=sha(p)
(k/'emulator-frozen.json').write_text(json.dumps(pins,indent=2)+'\n');print('258 freeze PASS',len(pins))
