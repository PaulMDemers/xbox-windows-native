"""MIT. Compare bounded guest observations with this run's independent cold files."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent
P=Path('C:/xwn593/pc001')
out=K/'save-review002.json'; assert not out.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
review=json.loads((K/'review001.json').read_text())
cold=json.loads((K/'ntfs-cold1-002.json').read_text())
before=json.loads((P/'cold0-002/manifest.json').read_text())
after=json.loads((P/'cold1-002/manifest.json').read_text())
assert cold['complete'] and sha(P/'cold1-002/manifest.json')==cold['manifest_sha256']
fields=review['runner_fields']
one=lambda key:fields.get(key)==['1']
value=lambda key:int(fields.get(key,['-1'])[0])
name='xwn593-kit/game/saved games/xwn593.sv4'
data=(P/'cold1-002/files'/after[name]['path']).read_bytes() if name in after else b''
digest=hashlib.sha1(data).hexdigest()
observed=fields.get('saved_sha1_byte',[])
observed_digest=bytes(int(v) for v in observed).hex() if len(observed)==20 else None
images=list((P/'collection001').glob('*-park-after-save.bmp'))
image_checks=[]
for p in images:
    b=p.read_bytes()
    image_checks.append(len(b)>=54 and b[:2]==b'BM' and struct.unpack_from('<I',b,2)[0]==len(b) and struct.unpack_from('<IiiHHII',b,14)==(40,640,-480,1,32,0,640*480*4) and struct.unpack_from('<I',b,10)[0]==54 and len(b)==54+640*480*4)
checks=dict(cleanup_review_passed=review['passed'],new_target_absent=one('save_target_absent') and name not in before,
    single_submission=one('save_click_posted'),dialog_closed=one('save_dialog_gone'),
    full_sequence=one('input_sequence_submitted'),file_observed=one('save_phase_file_observed'),
    no_wait_failure=not any(k in fields for k in ['saved_wait_fatal','saved_wait_timeout']),
    stable_observation=value('saved_stable_ms')>=1000 and value('saved_equal_reads')>=3,
    within_deadline=0<=value('saved_wait_elapsed_ms')<30000,
    cold_manifest_agrees=bool(data) and hashlib.sha256(data).hexdigest()==after.get(name,{}).get('sha256'),
    guest_size_agrees=bool(data) and value('saved_file_bytes')==len(data),
    guest_hash_agrees=bool(data) and observed_digest==digest,
    post_save_capture=len(image_checks)==1 and all(image_checks))
r=dict(passed=all(checks.values()),checks=checks,save=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),sha1=digest,guest_sha1=observed_digest),
    timing={k:value(k) for k in ['saved_first_readable_ms','saved_stable_ms','saved_equal_reads','saved_wait_elapsed_ms','saved_wait_polls']},
    private_captures=[str(p) for p in images],physical_access=False,
    limits='Fresh PC NTFS save and normal restart readback only; no reload, FATX, Xbox, game FPS or acceleration qualification.',
    pins={p.name:sha(p) for p in [K/'review001.json',K/'ntfs-cold1-002.json',K/'collection001.json',K/'build002.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
