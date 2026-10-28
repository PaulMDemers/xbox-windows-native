"""Review749 independent photo decode against frozen optical field mapping."""
from pathlib import Path
import json,hashlib,datetime
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k/'photo002.json').read_text());schema=json.loads((k/'optical-schema001.json').read_text())
assert r['passed'] and len(r['rows'])==13 and r['cross_row_verified']==list(range(1,12))
assert r['photo_sha256']==sha(Path('C:/xwn749/photo001.jpg'))
fields=dict(zip(schema['names'],[int(x,16) for x in r['decoded_rows']]))
assert fields['signature']==0x7490000d
black=[];white=[]
for row in r['rows']:
 assert len(row['samples'])==32
 for c in row['samples']:
  assert len(c['variants'])==5
  for v in c['variants']:
   (white if c['bit'] else black).append(v['median_rgb'])
out={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'photo_sha256':r['photo_sha256'],'decoder_sha256':sha(k/'photo_decode002.py'),'decode_sha256':sha(k/'photo002.json'),'schema_sha256':sha(k/'optical-schema001.json'),'fields':fields,'bits':416,'offset_samples_per_bit':5,'thresholds_per_sample':3,'adjacent_row_cross_checks':352,'max_black_channel_median':max(max(v) for v in black),'min_white_mean_median':min(sum(v)/3 for v in white),'observed_second_bar':'green','observed_state':'holding','physical_proof':'Native CR00 photo-only checkpoint; no native disk result','limits':['CR00 target5c comes from frozen source; before/after/restored are photo readings','Native CR3/CR4, CR04after and individual H7 words unexposed','CR04/CR05 restoration covered by aggregate CRTC mask','No complete mode-switch, Windows boot or shutdown proof'],'decode_failures_preserved':['photo001: component threshold65 missed one row11 cell (31/32)'],'reflection_handling':'Revised component cutoff100 globally; every cell independently agrees at five sample offsets and three thresholds; 352 adjacent-row cross-checks pass. No expected register values substituted.'}
assert fields['return_code']==fields['forward_status']==0x749
assert all(fields[n]==0 for n in ['prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask'])
assert fields['CR00_before']==fields['CR00_restored']==0xc8 and fields['CR00_after']==0x5c
assert fields['selectors_restored']==1 and fields['native_CR0']==0x4001003b and fields['CR05_after_CR00']==0x3e
p=k/'photo-review001.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
print(json.dumps({'passed':True,'fields':fields,'black_max':out['max_black_channel_median'],'white_min':out['min_white_mean_median']}))
