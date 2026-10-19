"""Independent cold checks: scoped early/late Welcome close, copied assets, media."""
import hashlib,json,re,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn584/pc001');sys.path.insert(0,str(K.parents[1]/'work/python-packages'));from Registry import Registry
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'integration-review001.json';assert not out.exists()
log=(P/'collection001/runner.txt').read_text();cold=json.loads((K/'ntfs-cold1-002.json').read_text());cleanup=json.loads((K/'review001.json').read_text())
show=[]
for phase in [0,1]:
 p=P/f'cold{phase}-002/files/Documents and Settings/Win2K/NTUSER.DAT';data=p.read_bytes();seq=struct.unpack_from('<II',data,4);assert data[:4]==b'regf' and seq[0]==seq[1]
 show.append(Registry.Registry(str(p)).open('Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\tips').value('Show').value())
a=json.loads((K/'asset-integrity001.json').read_text());m=json.loads((P/'cold1-002/manifest.json').read_text());changed=[];missing=[]
for name,row in a.items():
 actual=m.get('xwn582-kit/'+name.lower())
 if actual is None:missing.append(name)
 elif actual['sha256']!=row['sha256']:changed.append(name)
copy=(P/'cold1-002/files/xwn582-kit/copy-verified.txt').read_text();values=dict(re.findall(r'^(\w+)=(\d+)$',copy,re.M))
blockers=[x for x in log.splitlines() if x.startswith('blocker ')]
eject=json.loads((K/'media-ejection001.json').read_text())
checks=dict(cleanup=cleanup['passed'],show_unchanged=show==[1,1],two_close_posts=log.count('welcome_close_posted=1\n')==2,two_process_exits=log.count('welcome_wait=0\n')==2,two_windows_gone=log.count('welcome_window_gone=1\n')==2,two_completed_closes=re.findall(r'^welcome_closed_count=(\d+)$',log,re.M)==['1','2'],one_recorded_injection=len(re.findall(r'^pc_welcome_injected_pid=\d+$',log,re.M))==1,known_blocker_identity=len(blockers)==2 and all('class=_BerksWin2kWelcomeApp_ module=C:\\WINNT\\Welcome.exe title=Getting Started with Windows 2000'.lower() in x.lower() for x in blockers),all_assets_preverified=values.get('verified')=='1' and values.get('files')=='502' and values.get('expected')=='502',all_assets_retained=not missing,only_expected_game_mutations=set(changed)<=set(['game/Data/CSS0.DAT','game/Data/Game.cfg']),both_media_ejected=eject['both_ejected'],game_executable_exact=m['xwn582-kit/game/rct.exe']['sha256']==a['game/RCT.EXE']['sha256'])
r=dict(passed=all(checks.values()),checks=checks,show_before_after=show,changed_game_assets=changed,missing_game_assets=missing,copy_integrity=values,blocker_logs=blockers,disk_sha256=cold['disk_sha256'],physical_access=False,limits='Fresh PC integrated control; no Xbox scrolling, game FPS, sound, save persistence or GPU qualification.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(checks));assert r['passed']
