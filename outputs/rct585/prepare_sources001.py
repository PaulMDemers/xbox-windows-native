"""Prepare first phase of a planned two-boot persistence experiment; no launch."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent
out=K/'source-preparation001.json';assert not out.exists()
sources={}
def copy(src,name,old='582'):
 p=O/src;data=p.read_text();sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 target=K/name;assert not target.exists();target.write_text(data.replace(old,'585'))
for n in ['runner.c','welcome.h','title_signature.h','game_capture.h','verify.c','assets.h','assets001.py','build001.py','media001.py','media_review001.py']:
 copy('rct582/'+n,n)
copy('rct578/input.h','input.h','578')
p=K/'input.h';s=p.read_text();s=s.replace('static BOOL runinputs(void){','#include "save_dialog.h"\nstatic BOOL runinputs(void){')
begin=s.index(' Sleep(5000);number("save_dialog_inspection_tick"')
s=s[:begin]+' Sleep(1500);return save_owned_park();\n}\n'
begin=s.index('static BOOL CALLBACK inspect_child(');end=s.index('#include "save_dialog.h"',begin)
s=s[:begin]+s[end:]
# Exact qualified prelaunch Welcome close is in runner; late popup handling uses582 state.
base=(O/'rct582/input.h').read_text();a=base.index('static BOOL state(');b=base.index('\nstatic ',a+1)
a2=s.index('static BOOL state(');b2=s.index('\nstatic ',a2+1)
s=s[:a2]+base[a:b]+s[b2:]
marker=' number("title_ready",1);'
wait='\n start=GetTickCount();\n while(!(state("title_exposure_wait")&&exposed(5,5)&&exposed(635,5)&&exposed(5,475)&&exposed(635,475)&&exposed(320,240))){if(GetTickCount()-start>=90000){number("title_exposure_timeout",1);return FALSE;}Sleep(1000);}\n'
s=s.replace(marker,marker+wait);p.write_text(s)
p=K/'media001.py';s=p.read_text();s=s.replace("'echo PC-ONLY> C:\\\\xwn585-kit\\\\inject-late-welcome.flag',",'');p.write_text(s)
p=K/'build001.py';s=p.read_text().replace("'assets.h'","'assets.h','save_dialog.h'");p.write_text(s)
out.write_text(json.dumps(dict(source_pins=sources,phase=1,planned_phases=2,overall_closed=False,physical_access=False),indent=2)+'\n')
