"""Mode receipt negatives using explicitly synthetic API outcomes."""
import hashlib,json
from pathlib import Path
from mode_receipt import validate_mode
K=Path(__file__).resolve().parent;out=K/'mode-tests001.json';assert not out.exists()
f={}
for prefix,bits in [('mode_original',16),('mode_requested',24),('mode_active',24),('mode_after_restore',16)]:
 for k,v in [('bits',bits),('width',640),('height',480),('hz',60),('flags',0)]:f[prefix+'_'+k]=str(v)
f.update(mode_inventory_complete='1',mode_selected='1',mode_test_status='0',mode_apply_status='0',mode_changed='1',mode_restore_status='0',mode_restored='1',mode_inventory_count='105',mode_selected_index='77')
assert validate_mode(f)['passed'];count=0
def reject(changed):
 global count
 try:validate_mode(changed)
 except ValueError:count+=1;return
 raise AssertionError('Accepted false mode receipt')
for key in f:
 for value in ['?',True,'-1','4294967294']:
  changed=dict(f);changed[key]=value;reject(changed)
 changed=dict(f);del changed[key];reject(changed)
for key,value in [('mode_active_bits','16'),('mode_after_restore_bits','24'),('mode_original_bits','32'),('mode_inventory_count','0'),('mode_inventory_count','4096'),('mode_selected_index','105'),('mode_restore_query_failed','1'),('mode_active_mismatch','1')]:
 changed=dict(f);changed[key]=value;reject(changed)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out.write_text(json.dumps(dict(passed=True,synthetic_rejections=count,actual_mode_switches=0,checker_sha256=sha(K/'mode_receipt.py'),test_sha256=sha(Path(__file__))),indent=2)+'\n',encoding='utf-8')
print(count,'synthetic mode receipt refusals; no actual mode switches')
