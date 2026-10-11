"""Read existing closed logs; no recollection/requalification or cause invented."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'baseline-focus-review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=(k.parent/'video-boot-layout219/runner_analysis.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='helper');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual helper219>','exec'),ns)
rows=[]
for phase in [247,248]:
 p=k.parent/f'worker-barrier{phase}/preserve001/artifacts/wizard201.log';raw=p.read_bytes();lines=raw.decode('ascii').splitlines();records=[(f[0],list(map(int,f[1:]))) for f in map(str.split,lines)]
 try:result=ns['helper'](raw,1)
 except AssertionError:result=dict(passed=False)
 rows.append(dict(phase=phase,raw_sha256=sha(p),record_count=len(records),helper=result,active_waits=sum(n=='CANCEL_ACTIVE_WAIT' for n,v in records),install_states=sorted(set(v[0] for n,v in records if n=='INSTALL_STATE')),timeouts=[v for n,v in records if n=='TIMEOUT201'],foreground_owner_during_refusal_recorded=False,whole_case_passed=False))
assert rows[0]['helper']['passed'] and not rows[1]['helper']['passed'] and rows[1]['timeouts']==[[1,0,120210]] and rows[1]['active_waits']>0
p=k.parent/'setup-wizard-automation201/wizard006.c';s=p.read_text();assert 'if(!inspect(h,&w)||!xwn_eligible(&w,CurrentPid)||!welcome(h))return TRUE;' in s
assert 'if(GetForegroundWindow()!=h||!GetGUIThreadInfo(w.tid,&info)||info.hwndActive!=h||info.hwndCapture||info.hwndMenuOwner||info.hwndMoveSize){record("CANCEL_ACTIVE_WAIT"' in s
dest.write_text(json.dumps(dict(review_passed=True,source_sha256=sha(Path(__file__)),helper_source_sha256=sha(p),closed_cases=rows,old248_establishes='Eligible known welcome page, action refused at composite foreground/GUI-state predicate; no exact failed conjunct or foreground producer',physical_access=False,no_old_results_changed=True),indent=2)+'\n');print('Closed247/248 comparison reviewed; original248 cause remains unobserved')
