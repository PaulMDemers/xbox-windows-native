"""Read-only verification of the existing physical demo; never launches it."""
import importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
spec=importlib.util.spec_from_file_location('media407',W/'outputs/media-physical407/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=K/'verification001.json';assert not out.exists();m.ticket()
r=dict(completed=False,utc=m.utc(),physical_writes=False,launch_requested=False,console_C_accessed=False,verified={})
m.write_json(out,r)
expected=m.installed()
for p,v in m.read(W/'outputs/media-physical407/stage002.json')['verified'].items():expected[p]=v['sha256']
expected[m.PLAYER]=m.read(W/'outputs/media-physical407/before.json')['files'][m.PLAYER]['sha256']
with m.connect() as f:
    for p,h in expected.items():
        data=m.get(f,p);actual=m.sha(data)
        r['verified'][p]=dict(bytes=len(data),sha256=actual,exact=actual==h)
        assert actual==h,p
r.update(completed=True,completed_utc=m.utc(),all_exact=True,boot_path='E:/Applications/XWNEBoot/default.xbe',windows_video_path='C:/xwndemo407/play.cmd',prior_user_confirmed_windowed_video_and_audio=True,full_screen_frame_drops_retained=True)
m.write_json(out,r)
print(json.dumps({k:r[k] for k in ['completed','all_exact','boot_path','windows_video_path']}))
print('Verified files:',len(r['verified']))
