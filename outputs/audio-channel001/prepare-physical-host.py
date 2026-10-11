"""Prepare isolated successor controllers and payloads; never claim or contact hardware."""
import ast,hashlib,json,pathlib,shutil
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
old=k.parent/'audio-listen001';dest=k.parent/'audio-channel-physical001'
dest.mkdir(exist_ok=False)
names=['common001.py','capture002.py','audit-before002.py','providers001.py','trial002.py','scan001.py','audit001.py','typed-state001.py','installed-binding001.py','restore001.py','confirm-restored001.py','freeze001.py','claim.py']
origin={}
for name in names:
 p=old/name;origin[name]=hashlib.sha256(p.read_bytes()).hexdigest();s=p.read_text()
 s=s.replace('audio-listen001','audio-channel001').replace('xwnaL01','xwnaC01').replace('XWNAL01','XWNAC01')
 if name=='common001.py':
  s=s.replace("root=repo/'outputs/audio207/artifacts/hardware-package001/payload'","root=k/'artifacts/payload'\n    assert read(repo/'outputs/audio-channel001/emu001/audit.json')['scoped_audio_passed']")
 if name=='claim.py':
  s=s.replace("for p in state.glob('*-claimed.json'):","assert json.loads((k.parent/'audio-channel001/emu001/audit.json').read_text())['scoped_audio_passed'],'Emulator channel qualification required'\nassert json.loads((k.parent/'audio-channel001/emu001/closure.json').read_text())['closed']\nfor p in state.glob('*-claimed.json'):")
  s=s.replace('unchanged build004, bounded installation/playback','unchanged build004 with qualified channel helper, bounded installation/playback')
 if name=='audit001.py':
  s=s.replace("['AUDIO207_END','12','0']","['CHANNEL001_END','6','0']").replace("['AUDIO207_BEGIN','1','1']","['CHANNEL001_BEGIN','1','1']").replace('range(12)','range(6)').replace('if i%3!=1:','if True:').replace("('POSITION_SAMPLES','96000')","('POSITION_SAMPLES','144000')")
  s=s.replace("        r['workload_passed'] &= rows.count(['DONE_AFTER_RESET',str(i),'1'])==1","        r['workload_passed'] &= rows.count(['DONE_AFTER_RESET',str(i),'1'])==1\n        r['workload_passed'] &= rows.count(['PHASE_MASK',str(i),str(i%3+1)])==1 and rows.count(['CYCLE',str(i),'0'])==1")
 ast.parse(s);(dest/name).write_text(s)
source=repo/'outputs/audio207/artifacts/hardware-package001/payload'
payload=dest/'artifacts/payload';payload.mkdir(parents=True)
for folder in ['install','verify']:shutil.copytree(source/folder,payload/folder)
shutil.copyfile(k/'artifacts/build002/probe.exe',payload/'verify/probe.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={p.relative_to(payload).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in payload.rglob('*') if p.is_file()}
assert files['install/xwnaci207.sys']['sha256']=='c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75'
assert files['verify/probe.exe']['sha256']==json.loads((k/'helper-review001.json').read_text())['binary_sha256']
(payload/'MANIFEST.json').write_text(json.dumps({'files':files,'driver_changed':False,'new_helper':'audio-channel001/build002','physical_qualified':False},indent=2)+'\n')
(dest/'controller-origin.json').write_text(json.dumps({'source_directory':str(old),'source_sha256':origin,'changes':['New ticket and paths','Require passed closed emulator channel case before claim','Replace probe only','Six complete 144000-frame phases with masks 1,2,3,1,2,3']},indent=2)+'\n')
(dest/'PLAN.md').write_text('''# Physical channel identification follow-up

User authorized proceeding to dedicated tone/channel verification. No physical
access until audio-channel001/emu001 passes actual capture, runtime and cold gates
and closes. Claim a new audio-channel001 successor ticket only after every prior
owner has restored and closed. Preserve all original tickets and trial evidence.

Capture the current physical baseline and providers; validate five complete hives,
exact candidate/helper inputs and a read-only baseline allocation scan. Use the
same reviewed genuine installation route, then a subsequent channel-helper boot.
Play left 400 Hz, right 600 Hz, both, and repeat once. Each phase contains two
seconds of low-level tones, one second of silence, then a 350 ms inter-cycle pause.
Announce playback before launch and collect the user's channel observation.

Use exact new xwnaC01i/xwnaC01p and XWNAC01scanB/I/P/R namespaces. Do not change
the driver, HAL, kernel, video, other devices or device policy. Require joined
helpers, normal restart, preserved history, full cold hives and allocation checks.
Restore and read back the freshly captured incoming startup, hives, INF and audio
files; retain event/setup history and inactive evidence directories. Confirm final
allocation/dashboard ownership before closing. Ftdisk49 stays a strict failure.
''')
print('Physical scripts/payload prepared locally; no ticket or console access')
