"""Exact qualified-source reuse and the explicit retail launch adaptations."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'source-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s,old):
 for pre in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE','subject']:
  s=s.replace(pre+str(old),pre+'618')
 return s
for n in ['window.h','timing.h','calls.h','phase.h','lifetime.h','dib_header.h','trace_oracle.py','dib_oracle.py']:
 assert (K/n).read_bytes()==(K.parent/'rct617'/n).read_bytes(),n
for n in ['input.h','load_dialog002.h','park_reference.h','park_phase.h','assets.h',
          'verify.c','welcome.h','game_capture.h','title_signature.h','scene_compare.py']:
 assert (K/n).read_text()==norm((K.parent/'rct615'/n).read_text(),615),n
s=norm((K.parent/'rct617/trace.c').read_text(),617)
s=s.replace('char cmd[]="subject618 1";',r'char cmd[]="\"C:\\xwn618-kit\\game\\RCT.EXE\"";')
s=s.replace(r'"C:\\xwn618-kit\\subject.exe"',r'"C:\\xwn618-kit\\game\\RCT.EXE"')
s=s.replace(r'DEBUG_ONLY_THIS_PROCESS,0,"C:\\xwn618-kit",',r'DEBUG_ONLY_THIS_PROCESS,0,"C:\\xwn618-kit\\game",')
s=s.replace('GetTickCount()-started>60000','GetTickCount()-started>360000')
assert s==(K/'trace.c').read_text()
assert 'GetTickCount()-started>360000||count>10000' in (K.parent/'rct612/trace.c').read_text()
control=json.loads((K.parent/'rct617/final001.json').read_text());assert control['closed'] and control['passed']
out.write_text(json.dumps(dict(passed=True,control617_sha256=sha(K.parent/'rct617/final001.json'),
 unchanged_window_and_timing=True,unchanged615_scene_flow=True,
 recorder_changes=['namespace','retail executable and command line','retail working directory','existing612 360-second deadline'],
 scope='No recorder core, phase, lifetime,32-call cap or10000-event bound change.'),indent=2)+'\n')
