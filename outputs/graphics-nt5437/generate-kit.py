"""Adapt the retained 423 read-only fixture tooling into a new one-boot kit."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'crypto-persistence423'
def source(name):return (old/name).read_text()
def save(name,s):
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
s=source('prepare-ntfs001.py').replace('from ntfs_read import sha','from ntfs_read002 import sha').replace('crypto423-ntfs001','graphics437-pc001').replace('XWN423','XWN437').replace("K/'preflight002.json'","K.parent/'crypto-persistence423/preflight002.json'").replace("for name,h in review['package_files'].items():assert sha(Path('/mnt/e/xwn423/ntfs-python001')/name)==h","for name,h in review['package_files'].items():assert sha(Path('/mnt/e/xwn423/ntfs-python001')/name)==h")
s=s.replace("assert all(r['exit_code']==0 for r in build['rows'])","assert build['exit_code']==0").replace("pins['probe.c']=sha(K/'probe.c')","pins['runner.c']=sha(K/'runner.c')")
s=s.replace("sys.path.insert(0,str(W/'tools'));from build_space import require_space","sys.path.insert(0,str(W/'tools'));from build_space import require_space")
s=s.replace('from ntfs_read002 import sha',"import sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'crypto-persistence423'))\nfrom ntfs_read002 import sha")
save('prepare001.py',s)
s=source('ntfs-run002.py').replace('crypto423-ntfs001','graphics437-pc001').replace('xwn-crypto423-ntfs-phase','xwn-graphics437-pc-phase').replace('choices=[1,2]','choices=[1]').replace('ntfs-preparation002.json','ntfs-preparation001.json').replace('time.monotonic()+420','time.monotonic()+600')
s=s.replace('from ntfs_read002 import sha',"sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'crypto-persistence423'))\nfrom ntfs_read002 import sha")
s=s.replace('"""Two distinct bounded boots of one new persistence fixture; never repeat a phase."""','"""One bounded owned PC boot; no driver or mode change. Never repeat phase1."""')
save('run001.py',s)
s=source('ntfs-cold002.py').replace('crypto423-ntfs001','graphics437-pc001').replace('choices=[0,1,2]','choices=[0,1]').replace('xwn423/','xwn437/').replace('ntfs-preparation002.json','ntfs-preparation001.json')
s=s.replace('from ntfs_read002 import Reader,sha',"sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'crypto-persistence423'))\nfrom ntfs_read002 import Reader,sha").replace('from results import decode','')
s=s.replace(" path=saved.get('xwn437/'+('create.log' if a.phase==1 else 'reopen.log'))\n if path:report['probe']=decode(path.read_bytes(),a.phase);report['complete']=report['probe']['complete']\n else:report['probe']={'missing':True}"," report['runner_present']='xwn437/runner.txt' in saved")
s=s.replace("assert report['source_unchanged'] and report['audit_unchanged']","report['complete']=True\nassert report['source_unchanged'] and report['audit_unchanged']")
save('cold001.py',s)
s=source('login.py').replace('crypto423-ntfs001','graphics437-pc001').replace('xwn-crypto423-ntfs-phase','xwn-graphics437-pc-phase').replace('choices=[1,2]','choices=[1]')
save('login001.py',s)
print('Fresh kit generated; prior sources not modified.')
