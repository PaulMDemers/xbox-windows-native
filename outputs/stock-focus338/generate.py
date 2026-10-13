"""New activation precondition for the observed inactive known dialog; old Cancel unchanged."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;old=K.parent/'hd-ui313'
for n in ['wizard313.c','policy.h','activation.inc']:
    assert not (K/n).exists();(K/n).write_bytes((old/n).read_bytes())
t=(old/'activation.h').read_text()
t=t.replace('x313_gui_clear(s->target,s->hwnd)', '(s->target.ok==1 && (s->target.active==0 || s->target.active==s->hwnd) && !(s->target.flags&~1u) && !s->target.capture && !s->target.menu && !s->target.move)')
t=t.replace('a->hwnd==b->hwnd&&a->tid==b->tid&&a->fg==b->fg', 'a->target.active==b->target.active&&a->target.flags==b->target.flags&&a->foreground.flags==b->foreground.flags&&a->hwnd==b->hwnd&&a->tid==b->tid&&a->fg==b->fg')
(K/'activation.h').write_text(t,newline='\n')
t=(old/'test-adapter.c').read_text().replace('static DWORD calls,deny', 'static DWORD inactive,alien,transition;\nstatic DWORD calls,deny')
t=t.replace('g->hwndActive=t==11?20:30;', 'g->hwndActive=t==11?(alien?40:(inactive?0:20)):30;')
t=t.replace('if(stale&&!strcmp(l,"ACTIVATE_INTENT313"))identity=0;', 'if(stale&&!strcmp(l,"ACTIVATE_INTENT313"))identity=0;if(transition&&!strcmp(l,"ACTIVATE_INTENT313"))inactive=!inactive;')
t=t.replace('if(!deny)foreground=h;', 'if(!deny){foreground=h;inactive=0;}')
t=t.replace('ActivationLastState=0;foreground=30;', 'ActivationLastState=0;inactive=alien=transition=0;foreground=30;')
t=t.replace('    check(x313_same(&a,&a));', '''    reset();inactive=1;activate313(20,11);check(calls==1&&foreground==20&&!inactive&&ActivationBudget.count==1);
    reset();alien=1;activate313(20,11);check(calls==0&&ActivationBudget.count==0);
    reset();inactive=deny=1;for(i=0;i<10000;i++)activate313(20,11);check(calls==1&&inactive&&ActivationBudget.count==1);
    reset();inactive=transition=1;if(!setjmp(trap))activate313(20,11);check(exits==103&&calls==0&&ActivationBudget.count==1);
    reset();inactive=1;Mode=0;activate313(20,11);check(calls==0);
    reset();inactive=1;Emulator=0;activate313(20,11);check(calls==0);
    check(x313_same(&a,&a));''')
(K/'test-adapter.c').write_text(t,newline='\n')
t=(old/'Build.ps1').read_text().replace('D:/xwn313','E:/xwn338').replace('Get-PSDrive D','Get-PSDrive E').replace('cd /mnt/d/xwn313','cd /mnt/e/xwn338')
(K/'Build.ps1').write_text(t,newline='\n')
t=(old/'review-build.py').read_text().replace('D:/xwn313','E:/xwn338')
t=t.replace("base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')", "base=Path('E:/xwn337/capture001/F/winnt/system32')")
(K/'review-build.py').write_text(t,newline='\n')
t=(old/'activation_analysis.py').read_text().replace("g[0]&~1==0 and g[1]==h", "g[0]&~1==0 and (g[1] in [0,h] if phase=='BEFORE' else g[1]==h)")
t=t.replace('assert attempts,\'No actual activation coverage\'', "assert attempts,'No actual activation coverage'\n    assert any(tag=='GUI_ACTIVATE_BEFORE313_ACTIVE' and v[1]==0 for tag,v in rows),'Missing actual initially inactive target'")
(K/'activation_analysis.py').write_text(t,newline='\n')
(K/'DESIGN.md').write_text('336 reached Windows but the known wizard thread reported hwndActive=0 throughout.313 required hwndActive to equal the target before trying normal SetForegroundWindow, so it made zero calls.338 permits only zero OR that same target as the pre-activation active window, and rejects another active dialog. It additionally requires that activation state stay identical across durable logging. Original process identity, command, welcome-page checks, one-call budget, foreground checks, post-activation Cancel checks, setup-idle gates and physical-mode exclusion remain. No device/registry changes. Host tests model Win32 calls; a fresh runtime must demonstrate real inactive-to-active transition and verified Cancel closure. Historical336 remains failed.\n',encoding='utf-8')
(K/'source-review.json').write_text(json.dumps(dict(original_cancel_byte_identical=(K/'wizard313.c').read_bytes()==(old/'wizard313.c').read_bytes(),policy_byte_identical=(K/'policy.h').read_bytes()==(old/'policy.h').read_bytes(),adapter_byte_identical=(K/'activation.inc').read_bytes()==(old/'activation.inc').read_bytes(),physical_activation=False,driver_change=False),indent=2)+'\n')
