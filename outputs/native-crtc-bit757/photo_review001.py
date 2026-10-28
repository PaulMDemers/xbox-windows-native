"""Validate757 independently decoded photo against frozen optical mapping."""
from pathlib import Path
import json,hashlib,datetime
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k/'photo001.json').read_text());schema=json.loads((k/'optical-schema001.json').read_text())
assert r['passed'] and len(r['rows'])==13 and r['cross_row_verified']==list(range(1,12))
assert r['photo_sha256']==sha(Path('C:/xwn757/photo001.jpg'))
fields=dict(zip(schema['names'],[int(x,16) for x in r['decoded_rows']]))
assert fields['signature']==0x7570000d
black=[];white=[]
for row in r['rows']:
 assert len(row['samples'])==32
 for c in row['samples']:
  assert len(c['variants'])==5
  for v in c['variants']:
   (white if c['bit'] else black).append(v['median_rgb'])
assert fields['return_code']==fields['forward_status']==0x757
mask_names=['prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','CR03_cleanup_mask','CR05_second_cleanup_mask']
assert all(fields[n]==0 for n in mask_names)
assert fields['CR05_second_before']==fields['CR05_second_intermediate_restored']==0x3e
assert fields['CR05_second_after']==0xbe
out={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'photo_sha256':r['photo_sha256'],'decoder_sha256':sha(k/'photo_decode001.py'),'decode_sha256':sha(k/'photo001.json'),'schema_sha256':sha(k/'optical-schema001.json'),'reviewer_sha256':sha(Path(__file__)),'fields':fields,'bits':416,'offset_samples_per_bit':5,'thresholds_per_sample':3,'adjacent_row_cross_checks':352,'max_black_channel_median':max(max(v) for v in black),'min_white_mean_median':min(sum(v)/3 for v in white),'user_observation':'Green, holding','physical_proof':'Native second CR05 bit7 photo-only checkpoint; no native disk result','limits':['Second CR05 before/after/intermediate undo directly decoded3e/be/3e','Original/final CR05=31 covered by aggregate CRTC mask, not separately shown','Selectors, individual neighbors, prior restorations, H7 and native CPU registers unexposed','No complete mode-switch, Windows boot or shutdown proof'],'decode_failures_preserved':[],'decode_method':'Isolated cell components with geometry from visible rows; all416 bits agree at five offsets and three thresholds;352 adjacent-row cross-checks. No expected register values substituted.'}
p=k/'photo-review001.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
print(json.dumps({'passed':True,'fields':fields,'black_max':out['max_black_channel_median'],'white_min':out['min_white_mean_median']}))
