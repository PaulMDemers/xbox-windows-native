import hashlib,importlib,json,sys,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
r=json.loads((k/'ntfs-phase1.json').read_text());assert not r['closed'] and b'xwn-rct579-pc-phase1' in Path(f"/proc/{r['pid']}/cmdline").read_bytes()
m=json.loads((k/'media003.json').read_text());p=Path(m['path'].replace(chr(92),'/').replace('C:/','/mnt/c/'));assert sha(p)==m['sha256'] and json.loads((k/'media-review003.json').read_text())['passed']
out=k/'medium-change001.json';assert not out.exists()
record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_media=str(p),sha256=sha(p),identity=json.loads((k/'identity-observation001.json').read_text()),source_pins={str(k/n):sha(k/n) for n in ['runner004.c','build004.py','runner-build004.json','media003.py','media003.json','media-review003.json','change_medium001.py']},requested=False,completed=False)
with Qmp(Path('/tmp/xwn-rct579-phase1.sock')) as q:
 before=q.call('query-block');cd=next(x for x in before if x['device']=='ide1-cd0');assert cd['inserted']['file']=='/mnt/c/xwn579/helper002.iso' and not cd['locked']
 record['requested']=True;out.write_text(json.dumps(record,indent=2)+'\n')
 q.call('blockdev-change-medium',{'device':'ide1-cd0','filename':str(p),'format':'raw','read-only-mode':'read-only'})
 after=q.call('query-block');cd=next(x for x in after if x['device']=='ide1-cd0');assert cd['inserted']['file']==str(p) and cd['inserted']['ro'];record['completed']=True
out.write_text(json.dumps(record,indent=2)+'\n');print('Observed-identity close helper media inserted, read-only')
