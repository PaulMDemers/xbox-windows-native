"""Prepare the uninstrumented saved-scene cost fixture; never reuse a runtime."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'source001.json').exists()
sources={}
def copy(n,old=612):
 p=K.parent/f'rct{old}'/n
 s=p.read_text(encoding='utf-8')
 for pre in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE']:
  s=s.replace(pre+str(old),pre+'615')
 s=s.replace(f'choices=[{old}]','choices=[615]').replace("'"+str(old)+"'","'615'")
 if n in ['media_review001.py','copy_contract_tests001.py']:s=s.replace(f',{old})',',615)')
 sources[n]=dict(source=str(p),sha256=sha(p))
 return s
def write(n,s):(K/n).write_text(s,encoding='utf-8',newline='\n')
for n in ['input.h','load_dialog002.h','park_reference.h','verify.c','assets.h',
          'asset-integrity001.json','asset_header_check001.py','welcome.h',
          'game_capture.h','title_signature.h','media001.py','media_review001.py',
          'copy_contract_tests001.py','copy_contract.py','prepare001.py','cold002.py',
          'login001.py','actions002.py','input_transport001.py','edition.json',
          'scene_compare.py','scene_tests001.py','event_timestamps002.py',
          'process_review001.py']:
 write(n,copy(n))
write('.gitattributes','* -text whitespace=cr-at-eol\n')
runner=copy('runner.c',603)
runner=runner.replace('#include <wincrypt.h>','#include <wincrypt.h>\n#include <psapi.h>')
runner=runner.replace('static DWORD gamepid;','static DWORD gamepid;\nstatic HANDLE gamehandle;')
runner=runner.replace('#include "input.h"','#include "cost.h"\n#include "input.h"')
runner=runner.replace('number("display_preflight_passed",1);','number("display_preflight_passed",1);\n if(!cost_init()||!cost_sanity()){number("cost_sanity_failed",1);goto end;}')
runner=runner.replace('gamepid=pi.dwProcessId;','gamepid=pi.dwProcessId;gamehandle=pi.hProcess;')
runner=runner.replace('end:\n','end:\n cost_close();\n')
write('runner.c',runner)
park=copy('park_phase.h')
write('park_phase.h',park[:park.index('static BOOL parkphase606')])
inp=(K/'input.h').read_text()
inp=inp.replace('if(!point(5,5)||!capture("park-loaded"))return FALSE;',
 '''if(!point(5,5))return FALSE;
 Sleep(5000);
 if(!capture("park-loaded"))return FALSE;''')
inp=inp.replace('if(!parkphase606())return FALSE;\n Sleep(10000);',
 '''if(!park_verified||!state("cost-before"))return FALSE;
 if(!cost_game())return FALSE;
 if(!state("cost-after"))return FALSE;''')
write('input.h',inp)
sam=(K.parent/'rct614/sampler.c').read_text()
def part(start,end):return sam[sam.index(start):sam.index(end)]
header='/* MIT. Counter and bounded COM1 primitives inherited exactly from614. */\n'
header+=part('typedef BOOL','static HANDLE logh;')
header+='static HANDLE costlog=INVALID_HANDLE_VALUE;\n'
header+=part('static ULONGLONG ft','static BOOL text(')
header+=part('static BOOL text(','#ifdef WORKER').replace('logh','costlog').replace('static BOOL init(', 'static BOOL cost_init_path(')
header+=part('static HANDLE serialh;','void WINAPI mainCRTStartup(void)').replace('static HANDLE serialh;','static HANDLE serialh=INVALID_HANDLE_VALUE;')
header+='''
static SNAP cost_samples[512];
static BOOL cost_init(void){return cost_init_path("C:\\\\xwn615\\\\cost.txt")&&serial_open();}
static void cost_close(void){
 if(serialh!=INVALID_HANDLE_VALUE){CloseHandle(serialh);serialh=INVALID_HANDLE_VALUE;}
 if(costlog!=INVALID_HANDLE_VALUE){CloseHandle(costlog);costlog=INVALID_HANDLE_VALUE;}
}
static BOOL cost_sanity(void){
 SNAP a,b;
 if(!snap(GetCurrentProcess(),&a,TRUE)||!mark("START",0,&a))return FALSE;
 Sleep(5000);
 if(!snap(GetCurrentProcess(),&b,TRUE)||!mark("END",0,&b))return FALSE;
 return row("SLEEP_START",0,0,&a)&&row("SLEEP_END",0,0,&b)&&text("SLEEP_DONE\\r\\n");
}
static BOOL cost_game(void){
 SNAP a,b,oa,ob;DWORD n=0,j,wait;char line[100];
 if(!gamehandle||WaitForSingleObject(gamehandle,0)!=WAIT_TIMEOUT)return FALSE;
 if(!snap(GetCurrentProcess(),&oa,TRUE)||!snap(gamehandle,&a,TRUE)||!mark("START",1,&a))return FALSE;
 /* No file writes, screenshots, input, or window calls inside this interval.
  * Samples are bounded memory only; normal polling preserves process identity. */
 do{
  wait=WaitForSingleObject(gamehandle,100);
  if(wait!=WAIT_TIMEOUT||n>=512||!snap(gamehandle,&cost_samples[n],TRUE))return FALSE;
  n++;
 }while((DWORD)(cost_samples[n-1].tick-a.tick)<20000);
 if(!snap(gamehandle,&b,TRUE)||!snap(GetCurrentProcess(),&ob,TRUE)||!mark("END",1,&b))return FALSE;
 if(!row("GAME_START",1,0,&a)||!row("GAME_END",1,0,&b)||
    !row("OBSERVER_START",1,0,&oa)||!row("OBSERVER_END",1,0,&ob))return FALSE;
 for(j=0;j<n;j++)if(!row("SAMPLE",1,j,&cost_samples[j]))return FALSE;
 wsprintfA(line,"SAMPLES %lu\\r\\n",n);
 return text(line)&&text("COST_DONE\\r\\n");
}
'''
write('cost.h',header)
write('serial_host.py',copy('serial_host.py',614))
vm=copy('vm.py',614)
vm=vm.replace("'-usb','-device'", """'-drive',f"file={prep['retail_media']},media=cdrom,readonly=on,if=ide,index=3",'-usb','-device'""")
vm=vm.replace("if time.monotonic()>=capture:","if time.monotonic()>=capture and not serial.lines.rows:")
write('vm.py',vm)
build=copy('build001.py')
build=build.replace(",('trace615.exe'",",('trace615.exe'") # no effect; explicit tuple removal below
build=build.replace(",('trace.c','trace615.exe')",'')
write('build001.py',build)
media=(K/'media001.py').read_text()
media=media.replace("'copy D:\\\\TRACE615.EXE C:\\\\xwn615-kit\\\\TRACE615.EXE','if errorlevel 1 goto fail',",'')
write('media001.py',media)
contract=(K/'copy_contract.py').read_text().replace("['RUN','TRACE','VERIFY']","['RUN','VERIFY']").replace(",f'TRACE{number}.EXE'",'')
write('copy_contract.py',contract)
tests=(K/'copy_contract_tests001.py').read_text().replace('TRACE615','RUN615').replace('TRACE606','RUN606').replace('TRACE608','RUN608')
write('copy_contract_tests001.py',tests)
src=json.loads((K.parent/'rct612/source001.json').read_text())
for n in ['save','reference']:assert sha(Path(src[n]['path']))==src[n]['sha256']
write('source001.json',json.dumps(dict(passed=True,sources=sources,save=src['save'],
 reference=src['reference'],roi=src['roi'],roi_rgb_sha1=src['roi_rgb_sha1'],
 game_instrumentation=False,physical_access=False,
 counter_source_sha256=sha(K.parent/'rct614/sampler.c')),indent=2)+'\n')
