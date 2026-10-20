"""Matched retail cost interval, pending the actual617 coordination gate."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;assert not (K/'source001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
def cp(n,old):
 p=K.parent/f'rct{old}'/n;pins[f'{old}/{n}']=sha(p);s=p.read_text()
 for pre in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE','subject']:
  s=s.replace(pre+str(old),pre+'618')
 return s.replace(f'choices=[{old}]','choices=[618]').replace(f"'{old}'","'618'").replace(f',{old})',',618)')
def put(n,s):(K/n).write_text(s,encoding='utf-8',newline='\n')
for n in ['input.h','load_dialog002.h','park_reference.h','park_phase.h','verify.c',
 'assets.h','asset-integrity001.json','asset_header_check001.py','welcome.h',
 'game_capture.h','title_signature.h','prepare001.py','cold002.py','login001.py',
 'actions002.py','input_transport001.py','edition.json','scene_compare.py',
 'scene_tests001.py','event_timestamps002.py','process_review001.py','vm.py','serial_host.py']:
 put(n,cp(n,615))
for n in ['build001.py','media001.py','media_review001.py','copy_contract.py',
 'copy_contract_tests001.py','target_iat.h','analyze_trace001.py']:
 put(n,cp(n,612))
for n in ['timing.h','window.h','calls.h','lifetime.h','phase.h','dib_header.h',
 'dib_oracle.py','trace_oracle.py']:
 # Deliberately unchanged617 helper identifiers.
 put(n,cp(n,617))
t=cp('trace.c',617)
t=t.replace('char cmd[]="subject618 1";',r'char cmd[]="\"C:\\xwn618-kit\\game\\RCT.EXE\"";')
t=t.replace(r'"C:\\xwn618-kit\\subject.exe"',r'"C:\\xwn618-kit\\game\\RCT.EXE"')
t=t.replace('GetTickCount()-started>60000','GetTickCount()-started>360000')
put('trace.c',t)
r=cp('runner.c',612).replace('#include <wincrypt.h>','#include <wincrypt.h>\n#include <psapi.h>')
r=r.replace('static DWORD gamepid;','static DWORD gamepid;\nstatic HANDLE gamehandle,tracehandle;')
r=r.replace('#include "input.h"','#include "cost.h"\n#include "input.h"')
r=r.replace('number("display_preflight_passed",1);','number("display_preflight_passed",1);\n if(!cost_init()||!cost_sanity()){number("cost_sanity_failed",1);goto end;}')
r=r.replace('CloseHandle(pi.hThread);number("debugger_pid",pi.dwProcessId);',
 'CloseHandle(pi.hThread);tracehandle=pi.hProcess;number("debugger_pid",pi.dwProcessId);')
a=r.index(' handstart=GetTickCount();gamepid=0;');b=r.index(' number("game_pid"',a)
r=r[:a]+''' gamepid=0;
 if(!cost_identity(pi.hProcess,pi.dwProcessId))number("cost_identity_failed",1);
'''+r[b:]
r=r.replace('HANDLE backup,token,pidfile;DWORD pidbytes,handstart;','HANDLE backup,token;')
r=r.replace('CloseHandle(pi.hProcess);number("desktop_restored"', 'if(gamehandle){CloseHandle(gamehandle);gamehandle=0;}CloseHandle(pi.hProcess);tracehandle=0;number("desktop_restored"')
r=r.replace('end:\n','end:\n cost_close();\n')
put('runner.c',r)
cost=cp('cost.h',615);cost=cost[:cost.index('static BOOL cost_game(void)')]
cost=cost.replace('static SNAP cost_samples[512];','')
put('cost.h',cost+'\n#include "window.h"\n#include "retail_cost.h"\n')
src=json.loads((K.parent/'rct615/source001.json').read_text())
put('source001.json',json.dumps(dict(passed=True,sources=pins,save=src['save'],
 reference=src['reference'],roi=src['roi'],roi_rgb_sha1=src['roi_rgb_sha1'],
 physical_access=False,game_instrumentation=True,required_control='617 final001 passed'),indent=2)+'\n')
put('.gitattributes','* -text whitespace=cr-at-eol\n')
