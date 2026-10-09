"""Host-only lifecycle rejection tests using closed raw logs; mixed inputs are NOT a new runtime result."""
import hashlib,json
from pathlib import Path
from runner_analysis import analyze
k=Path(__file__).resolve().parent;dest=k/'parser-tests.json';assert not dest.exists()
base=k.parent/'video-phase-physical200/control001/artifacts/physical'
log=(base/'after-attempt.log').read_text(encoding='ascii')
wizard=(k.parent/'setup-wizard-automation201/physical001/artifacts/physical/after-wizard201.log').read_bytes()
snapshots=[(base/('after-'+name)).read_bytes() for name in ['setup-before.log','setup-after.log']]
log=log.replace('Close known hardware wizards without disabling devices. Leave this window visible.',
                'Known wizard Cancel helper completed. Unknown dialogs remain manual; no devices disabled.')
time=next(v.split()[1:] for v in log.splitlines() if v.startswith('SETUP_WAIT_START_TIME '))
prelude=['WIZARD_START_TIME '+' '.join(time),'WIZARD_MODE 0','WIZARD_STARTED 908',
         'WIZARD_JOIN_RESULT 0','WIZARD_EXIT 0','WIZARD_END_TIME '+' '.join(time)]
joined='\n'.join([log.splitlines()[0]]+prelude+log.splitlines()[1:])+'\n'
assert analyze(joined,snapshots,wizard,0)['idle_branch_passed'];checks=1
for before,after in [('WIZARD_JOIN_RESULT 0','WIZARD_JOIN_RESULT 258'),
                     ('WIZARD_EXIT 0','WIZARD_EXIT 15'),('WIZARD_MODE 0','WIZARD_MODE 1'),
                     ('WIZARD_STARTED 908','WIZARD_STARTED 0'),
                     ('INSTALL_BEFORE_SAMPLE 0','INSTALL_BEFORE_SAMPLE 258'),
                     ('INSTALL_FINAL_RESULT 0','INSTALL_FINAL_RESULT 258'),
                     ('NORMAL_RESTART_REQUEST 0','NORMAL_RESTART_REQUEST 1'),
                     ('WIZARD_END_TIME '+' '.join(time),'WIZARD_END_TIME 0 0')]:
    assert not analyze(joined.replace(before,after,1),snapshots,wizard,0)['idle_branch_passed'];checks+=1
assert not analyze(joined,snapshots,wizard[:-10],0)['idle_branch_passed'];checks+=1
assert not analyze(joined,[snapshots[0],snapshots[1]+b'x'],wizard,0)['idle_branch_passed'];checks+=1
bad=wizard.replace(b'START201 1 0 120000',b'START201 1 1 120000',1)
assert not analyze(joined,snapshots,bad,0)['idle_branch_passed'];checks+=1
bad=wizard.replace(b'CANCEL_INTENT 776 327832 4',b'CANCEL_INTENT 776 327832 5',1)
assert bad!=wizard and not analyze(joined,snapshots,bad,0)['idle_branch_passed'];checks+=1
assert not analyze(joined,snapshots,wizard+b'TIMEOUT201 1 4 120000\r\n',0)['idle_branch_passed'];checks+=1
assert not analyze(joined,snapshots,wizard.replace(b'GUI_BEFORE_CAPTURE 0 0 0',b'GUI_BEFORE_CAPTURE 1 0 0',1),0)['idle_branch_passed'];checks+=1
assert not analyze(joined.replace('WIZARD_EXIT 0\n','',1),snapshots,wizard,0)['idle_branch_passed'];checks+=1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=True,host_only=True,runtime_qualified=False,checks=checks,source_pins={n:sha(k/n) for n in ['runner_analysis.py','boundary_analysis.py','test-parser.py']},
       limits='Surrogate prelude + separate closed200/201 raw logs, not one boot. Reject unjoined/failed/wrong-mode/truncated/unknown-target/active-capture/changed-bookend/pending final guards. No real launch or synthesized runtime PASS.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Host lifecycle fault cases passed:',checks)
