"""MIT. Close the observed exploratory game session without claiming Xbox support."""
import datetime,hashlib,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;num=int(sys.argv[1]);assert num in (561,562,563)
T=K.parent/f'rct{num}';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def host(n):return Path(n.replace('/mnt/c/','C:/')) if sys.platform=='win32' else Path(n)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prep=read(T/'ntfs-preparation001.json');P=host(prep['path']);state=read(T/'ntfs-phase1.json');cold=read(T/'ntfs-cold1-002.json');installed=read(T/'installed001.json')
assert state['closed'] and state['exit_code']==0 and not state['deadline'] and not any(state.get(n) for n in ['host_quit','host_terminate','host_kill','space_stop'])
assert cold['complete'] and cold['source_unchanged'] and cold['audit_unchanged'] and installed['hives_clean']
assert state['source_unchanged'] and state['iso_unchanged'] and cold['normal_shutdown_delta']==1
assert sha(P/'disk.qcow2')==cold['disk_sha256']==state['disk_sha256']
out=T/'final001.json';assert not out.exists();archive=P.parent/'frozen001';assert not archive.exists()
archive.mkdir();archived=[]
for i,(n,h) in enumerate(prep['inputs'].items()):
 p=host(n);assert sha(p)==h,n;dest=archive/f'{i:03d}-{p.name}';shutil.copyfile(p,dest);assert sha(dest)==h
 archived.append(dict(original=n,path=str(dest),sha256=h))
screens=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((P/'phase1').glob('*.png'))]
record=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),normal_restart_supported=True,
 installed_files=installed['files'],hives_clean=True,host_process_closed=True,proprietary_files_private=True,
 screenshots=screens,archived_inputs=archived,physical_console_access=False,xbox_qualified=False,audio_qualified=False,
 performance_qualified=False,extended_gameplay_qualified=False,across_reboot_reload_qualified=False,
 scope='Exploratory PC installation, observed startup/rendering and any recorded in-session save/load. Read observations, not closure alone, for outcome.')
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('Closed',num,'screens',len(screens),'inputs',len(archived))
