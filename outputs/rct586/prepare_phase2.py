"""MIT. Prepare the planned second phase of OPEN586; never reopen phase1."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
P=Path('C:/xwn586/pc001')
cold=json.loads((K/'ntfs-cold1-002.json').read_text())
state=json.loads((K/'ntfs-phase1.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state.get('host_quit')
assert cold['complete'] and cold['normal_shutdown_delta']==1
assert sha(P/'disk.qcow2')==cold['disk_sha256']==state['disk_sha256']
manifest=json.loads((P/'cold1-002/manifest.json').read_text())
name='xwn586-kit/game/saved games/xwn586.sv4'
item=manifest[name]; saved=P/'cold1-002/files'/item['path']
assert saved.stat().st_size==item['bytes']==290242 and sha(saved)==item['sha256']
assert name not in json.loads((P/'cold0-002/manifest.json').read_text())
runner=(P/'collection001/runner.txt').read_text()
for token in ['save_phase_file_observed=1','game_exit=0','registry_restored=1','restart_requested=1']:
 assert token in runner,token
report=dict(passed=True,save=item,private_copy=str(saved),normal_shutdown_delta=1,
 disk_sha256=cold['disk_sha256'],phase1_closed=True,overall_experiment='OPEN: planned second boot pending')
out=K/'save-readback001.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n')
src=(K/'vm.py').read_text()
src=src.replace("F=P/'phase1'","F=P/'phase2'").replace('-phase1','-phase2').replace('phase=1','phase=2')
start=src.index("prep=json.loads((T/'ntfs-preparation001.json')")
end=src.index('space=require_space',start)
src=src[:start]+'''prep=json.loads((T/'ntfs-preparation001.json').read_text());cold=json.loads((T/'ntfs-cold1-002.json').read_text())
saved=json.loads((T/'save-readback001.json').read_text());media=json.loads((T/'phase2-source/media001.json').read_text())
assert saved['passed'] and cold['complete'] and cold['normal_shutdown_delta']==1
assert sha(P/'disk.qcow2')==saved['disk_sha256']==cold['disk_sha256']
assert not (T/'CLOSED.json').exists()
assert sha(prep['source'])==prep['source_sha256']
for n,h in prep['runtime_pins'].items():assert sha(n)==h,n
prep['helper_media']='/mnt/c/xwn586/phase2-helper001.iso';prep['helper_sha256']=media['sha256']
assert media['passed'] and sha(prep['helper_media'])==prep['helper_sha256']
assert sha('/mnt/c/xwn586/phase2-build001/load586.exe')==media['exe_sha256']
''' + src[end:]
src=src.replace(",'-drive',f\"file={prep['retail_media']},media=cdrom,readonly=on,if=ide,index=3\"",'')
dest=K/'vm_phase2.py';assert not dest.exists();dest.write_text(src)
login=(K/'login001.py').read_text().replace('choices=[1]','choices=[2]')
(K/'login002.py').write_text(login)
audit=(K/'cold002.py').read_text().replace('choices=[0,1]','choices=[2]')
audit=audit.replace("lower.startswith('xwn586/')", "lower.startswith(('xwn586/','xwn586p2/'))")
(K/'cold_phase2.py').write_text(audit)
print(json.dumps(report,indent=2))
