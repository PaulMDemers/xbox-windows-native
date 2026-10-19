"""MIT. Close the audited fixture without reopening or rerunning its disk."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn566')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda n:Path(n.replace('/mnt/c/','C:/'))
out=K/'final001.json';assert not out.exists()
run=read(K/'ntfs-phase1.json');cold=read(K/'ntfs-cold1-002.json');t=read(K/'transfer001.json')
assert run['closed'] and run['exit_code']==0 and not run['deadline']
assert cold['complete'] and cold['normal_shutdown_delta']==1 and cold['disk_sha256']==run['disk_sha256']
assert t['passed'] and t['source_disk_sha256']==cold['disk_sha256']
assert read(K/'observations003.json')['windowed_park_rendered_without_original_disc']
assert read(K/'transport-cleanup001.json')['removed']
frozen=P/'frozen001';assert not frozen.exists();frozen.mkdir();archived=[]
for i,(name,h) in enumerate(read(K/'ntfs-preparation001.json')['inputs'].items()):
 p=host(name);assert sha(p)==h;target=frozen/(str(i)+'-'+p.name);target.write_bytes(p.read_bytes());assert sha(target)==h
 archived.append(dict(original=name,path=str(target),sha256=h))
screens=[dict(path=str(p),sha256=sha(p)) for p in sorted((P/'pc001/phase1').glob('*.png'))]
for row in t['files'].values():assert sha(host(row['path']))==row['sha256']
record=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),normal_restart=True,
 game_without_disc_passed=True,windowed_park_observed=True,game_forced_termination=False,
 registry_values_restored=t['restored_registry'],private_transfer_bytes=t['total_bytes'],
 transfer_files=len(t['files']),transfer_sha256=sha(K/'transfer001.json'),archived_inputs=archived,screens=screens,
 physical_access=False,xbox_qualified=False,audio_qualified=False,
 evidence_note='cold002 inherited runner_present checks xwn566, while the actual helper writes xwn565. transfer001 independently contains the verified runner log and registry backup.',
 failures_preserved=['export-failure001.json'],no_rerun_or_recollection=True)
out.write_text(json.dumps(record,indent=2)+'\n');print('Closed566: private export complete, normal restart, no owned VM remains')
