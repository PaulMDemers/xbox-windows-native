"""Mutate actual host evidence in memory; exercise the actual batch wrapper privately."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
W=Path(__file__).resolve().parents[2]; K=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'tools'))
import graphics_sample as g
P=Path('E:/xwn436/controls001'); H=Path('E:/xwn436/host002'); B=Path('E:/xwn436/build004')
assert not P.exists() and not (K/'controls001.json').exists()
P.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
count=0
def rejected(fn):
    global count
    try: fn()
    except (ValueError,UnicodeError): count+=1; return
    raise AssertionError('Negative was accepted')
raw=(H/'02-hel.txt').read_bytes(); f=g.decode(raw)
source=(H/'02-hel-source.bin').read_bytes(); dest=(H/'02-hel-dest.bin').read_bytes()
g.validate(f,source,dest,0)
for key in ('surface.source.create','surface.dest.create','surface.blit','source.write.lock',
            'source.write.unlock','dest.read.lock','dest.read.unlock','ddraw.create','ddraw.caps'):
    for mutation in ('absent','88760005'):
        v=dict(f)
        if mutation=='absent': del v[key]
        else: v[key]=mutation
        rejected(lambda:g.validate(v,source,dest,0))
for code in (1,2,3,4,5,3221225477): rejected(lambda:g.validate(f,source,dest,code))
for b in (raw[:-18],raw+b'exit=0\r\n',raw+b'late=1\r\n',raw.replace(b'end=complete',b'end=pending')):
    rejected(lambda:g.decode(b))
for payload in (source,dest):
    for i in range(128):
        x=bytearray(payload); x[(i*7919)%len(x)]^=1
        if payload is source: rejected(lambda:g.validate(f,bytes(x),dest,0))
        else: rejected(lambda:g.validate(f,source,bytes(x),0))
rejected(lambda:g.validate(f,source[:-4],dest,0))
rejected(lambda:g.validate(f,source,dest+b'\0\0\0\0',0))
# The historical hardware-only crash remains rejected by its original oracle.
import importlib.util
spec=importlib.util.spec_from_file_location('oracle001',K/'oracle001.py')
old=importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
historical=Path('E:/xwn436/host001/02-hal.txt').read_bytes()
rejected(lambda:old.decode(historical))
prefix=P/'wrapper'
cmd=[os.environ['COMSPEC'],'/d','/c',str(B/'run.cmd'),'00','default',str(prefix),'quiet']
run=subprocess.run(cmd,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
assert run.returncode==0,run.stdout
review=g.review(prefix,Path(str(prefix)+'.exit'))
before={p.name:sha(p.read_bytes()) for p in P.glob('wrapper*')}
refusal=subprocess.run(cmd,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
assert refusal.returncode==2
assert before=={p.name:sha(p.read_bytes()) for p in P.glob('wrapper*')}
host=json.loads((K/'host002.json').read_text())
assert all(r['exit_code']==0 and 'review' in r for r in host['rows'][:-1])
assert host['rows'][-1]['exit_code']==2 and not (H/'02-hal.txt').exists()
result=dict(passed=True,actual_evidence_mutations_rejected=count,wrapper_review=review,
            wrapper_exit=run.returncode,existing_prefix_refusal_exit=refusal.returncode,
            existing_result_files_unchanged=True,hardware_only_copy_refused_before_report=True,
            original_failure_still_rejected=True,source_sha256=sha(Path(__file__).read_bytes()),
            oracle_sha256=sha((W/'tools/graphics_sample.py').read_bytes()),
            files={p.name:sha(p.read_bytes()) for p in P.iterdir()},
            scope='Modern host sample and evidence checks only; no NT5/Xbox runtime')
(K/'controls001.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
