"""Prepare two unique five-sample console trials with explicit functional gates."""
import ast
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-hardware-trial164'
assert not (k/'physical-controller.py').exists()
s=(old/'physical-controller.py').read_text(encoding='utf-8')
s=s.replace('import argparse,datetime,hashlib,importlib.util,json,zipfile','import argparse,datetime,hashlib,importlib.util,json,zipfile,sys')
s=s.replace("k=Path(__file__).resolve().parent;ws=k.parents[1];record=k/'physical.json';art=k/'artifacts/physical'", "k=Path(__file__).resolve().parent;ws=k.parents[1]\ncase=sys.argv[2];assert case in ['control001','candidate001']\nnamespace='xwnvt166a' if case=='control001' else 'xwnvt166b'\nrollback_dir='xwn-display166a' if case=='control001' else 'xwn-display166b'\nrecord=k/case/'physical.json';art=k/case/'artifacts/physical'")
s=s.replace("test_startup=b'@echo off\\r\\nC:\\\\xwnv164\\\\runner.exe\\r\\nexit\\r\\n'", "test_startup=('@echo off\\r\\nC:\\\\'+namespace+'\\\\runner.exe\\r\\nexit\\r\\n').encode('ascii')")
s=s.replace("changes=[('/'+v['target'],ws/v['source'],v['sha256']) for v in sources]", "all_changes=[('/'+v['target'],ws/v['source'],v['sha256']) for v in sources]\nchanges=all_changes if case=='candidate001' else []")
start=s.index('def ready():');end=s.index("if __name__=='__main__':",start)
s=s[:start]+'''def ready():
    fields=['source','event_id','type','strings','data_hex']
    expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
    for name in ['control001','candidate001']:
        r=read(k/name/'audit.json')
        assert r['workload_passed'] and r['integrity_passed'] and not r['strict_qualification_passed']
        assert len(r['warnings_errors'])==len(expected)==1 and all(r['warnings_errors'][0][f]==expected[0][f] for f in fields)
        assert not r['new_events']['application'] and r['normal_shutdown_count']==1
    review=read(k/'build-review.json')
    assert review['passed'] and sha((k/'artifacts/runner.exe').read_bytes())==review['sha256']
    assert sha((k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe').read_bytes())==review['probe_sha256']
    if case=='candidate001':
        r=read(k/'control001/physical-audit.json')
        assert r['workload_passed'] and r['preserved_files_exact'] and r['event_history_preserved']
        assert not r['new_events']['application'] and len(r['warnings_errors'])==1
        assert all(r['warnings_errors'][0][f]==expected[0][f] for f in fields)
        assert read(k/'control001/restored-verification.json')['passed']

''' + s[end:]
s=s.replace("parser.add_argument('--keyboard-unplugged'", "parser.add_argument('case',choices=['control001','candidate001']);parser.add_argument('--keyboard-unplugged'")
s=s.replace("for row in capture['files']:\n                # Config/log/trace freshness is checked too, before any write.", "for row in capture['files']:\n                if row['path'].endswith(('/config/software','/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')):continue\n                # All immutable core, startup and restored SYSTEM must match.")
s=s.replace("assert absence(f,'/F','xwnv164') and absence(f,'/F','xwn-display164')", "assert absence(f,'/F',namespace) and absence(f,'/F',rollback_dir)")
s=s.replace("emulator_audit_sha256=sha((k.parent/'video-helper-runtime165/candidate001/audit.json').read_bytes())", "case=case,namespace=namespace,emulator_audit_sha256=sha((k/case/'audit.json').read_bytes())")
s=s.replace('current-rollback164.zip','current-rollback166.zip')
s=s.replace("'/F/xwn-display164/current-rollback166.zip'", "'/F/'+rollback_dir+'/current-rollback166.zip'").replace("f.mkd('/F/xwn-display164')", "f.mkd('/F/'+rollback_dir)")
s=s.replace("f.mkd('/F/xwnv164')", "f.mkd('/F/'+namespace)")
s=s.replace("'/F/xwnv164/runner.exe'", "'/F/'+namespace+'/runner.exe'").replace("'/F/xwnv164/replay.exe'", "'/F/'+namespace+'/replay.exe'")
s=s.replace("m.put(f,system,proposal.read_bytes())", "if case=='candidate001':m.put(f,system,proposal.read_bytes())")
s=s.replace("('attempt.log','/F/xwnv164/attempt.log'),('gdi-baseline.txt','/F/xwnv164/gdi-baseline.txt'),", "('attempt.log','/F/'+namespace+'/attempt.log'),\n                    *[('sample%d'%i,'/F/'+namespace+'/sample%d/gdi-baseline.txt'%i) for i in range(5)],")
s=s.replace("for p,_,_ in changes]:", "for p,_,_ in all_changes]:")
s=s.replace("optional=name in ['attempt.log','gdi-baseline.txt']", "optional=name=='attempt.log' or name.startswith('sample') or name=='xwnown.dll'")
s=s.replace('def ready():\n', "def ready():\n    packet=read(k/'physical-ready.json')\n    for name,digest in packet['source_pins'].items():assert sha((k/name).read_bytes())==digest,name\n")
s=s.replace("        assert read(k/'control001/restored-verification.json')['passed']", "        assert read(k/'control001/restored-verification.json')['passed']\n        assert read(k/'control001/physical-hive-audit.json')['passed']\n        assert r['actual_caps']==read(k/'control001/audit.json')['actual_caps']\n        assert not any(v['source']=='Application Popup' for v in r['new_events']['system'])")
assert 'xwnv164' not in s and 'xwn-display164' not in s
ast.parse(s);(k/'physical-controller.py').write_bytes(s.encode('utf-8'))

s=(old/'audit-physical.py').read_text(encoding='utf-8')
s=s.replace("ws = k.parents[1]\nart", "ws = k.parents[1]\ncase=sys.argv[1];assert case in ['control001','candidate001'];k=k/case\nart")
start=s.index("log = ''");end=s.index("result['normal_shutdown_count']",start)
s=s[:start]+'''sys.path.insert(0,str(k.parent));from sample_analysis import analyze
samples=[analyze(None if r['after']['sample%d'%i] is None else (art/('after-sample%d'%i)).read_bytes().decode('ascii')) for i in range(5)]
attempt='' if r['after']['attempt.log'] is None else (art/'after-attempt.log').read_bytes().decode('ascii')
result['samples']=samples;result['runner_log']=attempt
result['probe_passed']=all(v['probe_passed'] for v in samples)
result['pixel_checks_passed']=all(v['copy_checks_passed'] for v in samples)
result['loop_coverage']=all(v['loop_coverage'] for v in samples)
result['actual_caps']=samples[0]['actual_caps'];result['actual_modes']=samples[0]['actual_modes']
result['caps_consistent']=all(v['actual_caps']==result['actual_caps'] and v['actual_modes']==result['actual_modes'] for v in samples)
result['normal_restart_requested']=attempt.splitlines()==['ATTEMPT_ONCE']+['SAMPLE_EXIT_ZERO %d'%i for i in range(5)]+['NORMAL_RESTART_REQUEST']
''' + s[end:]
s=s.replace("result['deployed_payloads_exact'] =", "result['deployed_payloads_exact'] = case=='control001' or")
s=s.replace("result['probe_passed'] and result['pixel_checks_passed']", "result['caps_consistent'] and result['probe_passed'] and result['pixel_checks_passed']")
ast.parse(s);(k/'audit-physical.py').write_bytes(s.encode('utf-8'))

s=(old/'audit-physical-hives.py').read_text(encoding='utf-8').replace("art = k/'artifacts/physical'", "base=k;case=sys.argv[1];assert case in ['control001','candidate001'];k=k/case\nart = k/'artifacts/physical'")
s=s.replace("k.parent/'video-physical-review159", "base.parent/'video-physical-review159")
s=s.replace("expected['after_hex']", "expected['after_hex' if case=='candidate001' else 'before_hex']")
ast.parse(s);(k/'audit-physical-hives.py').write_bytes(s.encode('utf-8'))

s=(old/'verify-restored.py').read_text(encoding='utf-8').replace('import json','import json,sys')
s=s.replace("k = Path(__file__).resolve().parent", "base=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];k=base/case")
s=s.replace("k/'physical-controller.py'", "base/'physical-controller.py'")
s=s.replace("spec.loader.exec_module(c)", "sys.argv=['physical-controller.py','inspect',case];spec.loader.exec_module(c)")
s=s.replace("introduced_absent = c.absence(f, '/F/winnt/system32', 'xwnown.dll') if r['before_payloads'][c.xwnown] is None else False", "introduced_absent = c.absence(f, '/F/winnt/system32', 'xwnown.dll')")
s=s.replace("'/F/xwn-display164/current-rollback164.zip'", "'/F/'+c.rollback_dir+'/current-rollback166.zip'")
ast.parse(s);(k/'verify-restored.py').write_bytes(s.encode('utf-8'))

s=(old/'watch-physical.py').read_text(encoding='utf-8').replace('import time','import time,sys')
s=s.replace("k = Path(__file__).resolve().parent", "base=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];k=base/case")
s=s.replace("k / 'physical-controller.py'", "base / 'physical-controller.py'")
s=s.replace("spec.loader.exec_module(c)", "sys.argv=['physical-controller.py','inspect',case];spec.loader.exec_module(c)")
ast.parse(s);(k/'watch-physical.py').write_bytes(s.encode('utf-8'))
print('Two unique one-shot hardware controllers prepared; no console access')
