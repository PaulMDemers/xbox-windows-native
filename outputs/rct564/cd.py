"""MIT. Replace original game disc with exact owned helper ISO on owned live PID."""
import hashlib,importlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
r=json.loads((K/'ntfs-phase1.json').read_text());assert not r['closed'] and b'xwn-rct564-pc-phase1' in Path('/proc/'+str(r['pid'])+'/cmdline').read_bytes()
h=json.loads((K.parent/'rct565/helper001.json').read_text());p=Path('/mnt/c/xwn565/helper001.iso');assert hashlib.sha256(p.read_bytes()).hexdigest()==h['sha256'];out=K/'disc-change001.json';assert not out.exists()
with Qmp(Path('/tmp/xwn-rct564-phase1.sock')) as q:
 before=q.call('query-block');row=next(x for x in before if x['device']=='ide1-cd0');assert row['inserted']['file'].endswith('RollerCoaster Tycoon Deluxe.iso')
 record=dict(requested=True,before=before,helper_sha256=h['sha256']);out.write_text(json.dumps(record,indent=2)+'\n')
 q.call('blockdev-change-medium',{'device':'ide1-cd0','filename':str(p),'format':'raw','read-only-mode':'read-only'})
 record['after']=q.call('query-block');record['completed']=True;out.write_text(json.dumps(record,indent=2)+'\n');print('Original Deluxe disc replaced by exact helper-only ISO')
