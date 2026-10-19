"""MIT. Remove only the exact owned, now-unmounted temporary helper ISO."""
import hashlib,json,datetime
from pathlib import Path
K=Path(__file__).resolve().parent
r=json.loads((K/'ntfs-phase1.json').read_text());assert r['closed']
media=json.loads((K/'media001.json').read_text());p=Path(media['path']).resolve();root=Path('C:/xwn566').resolve()
assert p.is_relative_to(root) and p.name=='helper-media001.iso' and p.is_file()
assert hashlib.sha256(p.read_bytes()).hexdigest()==media['sha256']
out=K/'transport-cleanup001.json';assert not out.exists()
record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(p),sha256=media['sha256'],bytes=p.stat().st_size,vm_closed=True,original_game_iso_removed=False,payload_sources_preserved=True,removed=False)
out.write_text(json.dumps(record,indent=2)+'\n');p.unlink();assert not p.exists();record['removed']=True;out.write_text(json.dumps(record,indent=2)+'\n');print('Removed exact owned temporary helper transport; original media/config/runner retained')
