"""Prepare a separately pinned, bounded observation helper for planned boot two."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;D=K/'phase2-source'
assert not D.exists();D.mkdir()
# Retain the original phase-one source and frozen build unchanged.
for name in ['runner.c','input.h','welcome.h','game_capture.h','title_signature.h']:
    s=(K/name).read_text()
    # Only the evidence directory changes; game assets stay in the original kit.
    s=s.replace('xwn585\\\\','xwn585p2\\\\').replace('"C:\\\\xwn585"','"C:\\\\xwn585p2"')
    if name=='input.h':
        s=s.replace('#include "save_dialog.h"','')
        a=s.index(' if(!capture("park-before-save")')
        s=s[:a]+''' if(!capture("park-before-manual-load"))return FALSE;
 number("manual_observation_started",1);
 /* Host observes actual owned UI. This interval is not a behavioral PASS. */
 start=GetTickCount();
 while(GetTickCount()-start<240000){
  Sleep(15000);
  gamewindow=0;gamewindowcount=0;EnumWindows(findgame,0);
  if(gamewindowcount==1&&state("manual-observation"))capture("manual-observation");
 }
 number("manual_observation_finished",1);
 return FALSE; /* No automatic load-success claim from elapsed time/input. */
}
'''
    (D/name).write_bytes(s.replace('\r\n','\n').replace('\n','\r\n').encode())
(D/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
s=(K/'build002.py').read_text().replace("K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn585/build002')","K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn585/phase2-build001')")
s=s.replace("for src,exe in [('runner.c','run585.exe'),('verify.c','verify585.exe')]:","for src,exe in [('runner.c','load585.exe')]:")
# Build receipt is local to this new source folder, separate from phase one.
(D/'build002.py').write_text(s)
r={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.is_file()}
(K/'phase2-source-preparation001.json').write_text(json.dumps(dict(files=r,admitted=False,physical_access=False,limits='Prepared helper only; requires phase-one save/normal shutdown review and separate media/runtime admission.'),indent=2)+'\n')
