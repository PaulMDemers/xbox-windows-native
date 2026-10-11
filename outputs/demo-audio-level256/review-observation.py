"""Keep playback, audible observation, cold integrity and failed physical-ID query distinct."""
from common001 import *
pins();out=k/'playback001';dest=out/'observation-review.json';assert not dest.exists()
a=read(out/'audit.json');c=read(out/'collection.json');p=k/'artifacts/playback001/F/xwnd256/audio207.log'
assert sha(p.read_bytes())==c['files']['/F/xwnd256/audio207.log']['sha256']
rows=[line.split() for line in p.read_text().splitlines()]
def once(tag,i,value):return rows.count([tag,str(i),str(value)])==1
checks={}
for i in range(6):
 checks[str(i)]=all(once(tag,i,0) for tag in ['OPEN','PREPARE','WRITE','RESET','UNPREPARE','CLOSE','POSITION_RESULT','DEVICE_ID_RESULT','DEVICE_CAPS_RESULT','VOLUME_RESULT'])
 checks[str(i)] &= all(once(tag,i,val) for tag,val in [('DONE_BEFORE_RESET',1),('DONE_AFTER_RESET',1),('POSITION_TYPE',2),('POSITION_SAMPLES',144000),('PHASE_MASK',i%3+1),('SAMPLE_GAIN',1 if i<3 else 4)])
 elapsed=[int(v[2]) for v in rows if v[:2]==['ELAPSED_MS',str(i)]]
 checks[str(i)] &= len(elapsed)==1 and 2500<=elapsed[0]<=10000
 assert once('DEVICE_ID',i,4294967295)
 assert ['DEVICE_NAME',str(i),'Microsoft','Sound','Mapper'] in rows
 assert once('VOLUME_PACKED',i,0x804d804d)
assert all(checks.values()) and rows[-1]==['CHANNEL001_END','6','0']
visible=[v for v in rows if v[0]=='VISIBLE_RESULT'];assert len(visible)==13 and all(v[2]=='0' for v in visible)
assert not a['workload_passed'] and not a['scoped_runtime_passed'] and not a['strict_qualification_passed']
r=dict(original_audit_preserved_sha256=sha((out/'audit.json').read_bytes()),original_diagnostic_passed=False,
 lifecycle_and_gain_checks=checks,completed_six_buffers=True,visible_writes_succeeded=True,
 physical_output_id_resolved=False,returned_id='WAVE_MAPPER (0xffffffff)',reported_name='Microsoft Sound Mapper',
 mapper_volume_words=[32845,32845],volume_is_acoustic_measurement=False,
 user_observation=read(k/'user-observation001.json'),cold_integrity_passed=a['integrity_passed'],
 joined_children=a['joined_children'],normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
 strict_qualification_passed=False,release_qualified=False,
 limits='No new overall PASS. Original physical-device-ID requirement failed; mapper identity retained. User louder-trio audibility is separate from API completion; speaker routing and cause of quiet trio not isolated.')
save(dest,r);print('Playback and user audibility separated from preserved failed physical-ID diagnostic')
