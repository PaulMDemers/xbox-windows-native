"""MIT. Close the fresh save-only PC control without reopening its runtime."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn593/pc001')
read=lambda n:json.loads((K/n).read_text())
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'final001.json';assert not out.exists()
state=read('ntfs-phase1.json');audit=read('ntfs-cold1-002.json')
assert state['closed'] and state['exit_code']==0 and not state['deadline']
assert not any(state.get(k) for k in ['host_quit','host_terminate','host_kill','space_stop'])
assert sha(P/'disk.qcow2')==state['disk_sha256']==audit['disk_sha256']
checks={n:read(n)['passed'] for n in ['host-tests001.json','binary-review001.json','media-review001.json','review001.json','save-review002.json']}
assert all(checks.values())
assert not read('save-review001.json')['passed']
images=['04-park-before-save.bmp','06-park-after-save.bmp']
visual=dict(passed=True,method='Assistant inspected decoded private BMPs at native640x480; both show the same Forest Frontiers entrance, paused game, March Year1,0guests and10000cash; post-save has no dialog/error. Cursor difference is not game-state change.',images={n:sha(P/'collection001'/n) for n in images},limits='Save-stage visual observation, not successful reload.')
(K/'visual-review001.json').write_text(json.dumps(visual,indent=2)+'\n')
failure=dict(preserved_review='save-review001.json',reason='Reviewer expected positive BMP height; actual frozen capture code emits top-down biHeight=-480.',header=dict(size=1228854,offset=54,dib=40,width=640,height=-480,planes=1,bpp=32,compression=0,imagebytes=1228800),correction='save_review002.py verifies exact emitted header, pixel bytes and total length. Original failed review retained; no runtime rerun or recollection.',post_close_screen_request='One screen request raced normal VM exit; ownership guard refused. No input sent or runtime reopened.')
(K/'review-correction001.json').write_text(json.dumps(failure,indent=2)+'\n')
r=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,visual_save_stage=True,save_only=True,reload_tested=False,physical_access=False,owned_vm_closed=True,console_state='Untouched; last592 dashboard with no hook',limits='PC helper qualification and one NTFS save surviving normal restart. No Xbox/FATX/reload/performance qualification.',pins={n:sha(K/n) for n in ['ntfs-phase1.json','ntfs-cold1-002.json','save-review002.json','visual-review001.json','review-correction001.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print('PC593 closed: save helper qualified; reload not tested')
