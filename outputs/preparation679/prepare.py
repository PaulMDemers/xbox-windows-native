"""Prepare a local-only watched test package. No FTP, startup hook or launch."""
import datetime,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn679/prepared001')
out=K/'preparation001.json';assert not P.exists() and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
r=dict(prepared=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,remote_staged=False,launch_requested=False,hook_installed=False,user_direction='Prepare now; watched test in a few hours',local_package=str(P))
try:
 assert shutil.disk_usage('C:/').free-16*1024**2>=20*1024**3
 b=read(W/'outputs/timer678/build001.json');e=read(W/'outputs/timer678/entry001.json');review=read(W/'outputs/timer678/review001.json')
 assert b['passed'] and e['passed'] and len(e['cases'])==25 and review['passed'] and len(review['checks'])==313
 for n,h in b['source_pins'].items():assert sha(W/n)==h
 source=Path('C:/xwn678/build001/default.xbe');expected=b['artifacts']['default.xbe']['sha256'];assert sha(source)==expected
 P.mkdir(parents=True);shutil.copyfile(source,P/'default.xbe');assert sha(P/'default.xbe')==expected
 plan=dict(physical_attempt='679physical001',built_identity=b['attempt'],build_id=b['build_id'],xbe_sha256=expected,target='/E/Applications/XWNTimer679',launch_authorized_now=False,requires_fresh_readiness=True,expected='Held black screen; green/amber entry, then solid green / red-green / red-amber; SMC failure can prevent an indication',recovery='User power-cycle after recording held LED and screen',udp_expected=False,windows_expected=False,startup_hook=False)
 (P/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
 (P/'README.txt').write_text('LOCAL PREPARATION ONLY. Do not launch unattended.\nAwait user readiness and reset availability; refresh hardware lease, current baseline, target free space and exact stage readback before a single bounded SITE request.\nDo not modify ordinary startup or 720p launcher. This deliberately holds and requires manual power-cycle.\n',encoding='utf-8')
 r['files']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in P.iterdir()}
 r['source_receipts']={n:sha(W/'outputs/timer678'/n) for n in ['build001.json','entry001.json','review001.json','closure001.json']}
 r['plan']=plan;r['prepared']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('Prepared locally; no hardware contact or launch:',r['prepared'])
