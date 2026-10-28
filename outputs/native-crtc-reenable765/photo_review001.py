"""Map independently decoded765 cells to the frozen13-row contract."""
from pathlib import Path
import json,hashlib,datetime
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k/'photo001.json').read_text());schema=json.loads((k/'optical-schema001.json').read_text())
assert r['passed'] and len(r['rows'])==13 and r['cross_row_verified']==list(range(1,12))
assert r['photo_sha256']==sha(Path('C:/xwn765/photo001.jpg'))
fields=dict(zip(schema['names'],[int(x,16) for x in r['decoded_rows']]))
assert fields['signature']==0x7650000d and fields['return_code']==0x765
masks=['prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','CR01_cleanup_mask','CR02_second_cleanup_mask','CR17_second_cleanup_mask']
assert all(fields[n]==0 for n in masks)
assert [fields[n] for n in ['CR17_second_before','CR17_second_after','CR17_second_restored']]==[0x63,0xe3,0x63]
black=[];white=[]
for row in r['rows']:
 assert len(row['samples'])==32
 assert int(''.join(str(c['bit']) for c in row['samples']),2)==int(row['value_hex'],16)
 for c in row['samples']:
  assert len(c['variants'])==5
  for v in c['variants']:(white if c['bit'] else black).append(v['median_rgb'])
out={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'photo_sha256':r['photo_sha256'],'decoder_sha256':sha(k/'photo_decode001.py'),'decode_sha256':sha(k/'photo001.json'),'schema_sha256':sha(k/'optical-schema001.json'),'reviewer_sha256':sha(Path(__file__)),'fields':fields,'bits':416,'offset_samples_per_bit':5,'thresholds_per_sample':3,'adjacent_row_cross_checks':352,'max_black_channel_median':max(max(v) for v in black),'min_white_mean_median':min(sum(v)/3 for v in white),'user_observation':'Green, holding','physical_proof':'Native CR17 forward enable and own-value recovery checkpoint; photo-only, no native disk result','limits':['CR17 forward 63/e3/63 and eight aggregate zero recovery masks directly decoded','CR03, second CR05 and first CR17 recovery masks and forward status are not displayed raw fields; final765 requires forward success and all eleven recovery masks clear in tested code','Selectors, individual neighbors/prior restorations, H7 and native CPU registers unexposed','No complete mode-switch, Windows boot or normal shutdown proof'],'decode_failures_preserved':[],'decode_method':'Isolated components from visible row geometry; all416 bits agree at five offsets and three thresholds;352 adjacent-row cross-checks. No expected register values substituted.'}
p=k/'photo-review001.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
print(json.dumps({'passed':True,'fields':fields,'black_max':out['max_black_channel_median'],'white_min':out['min_white_mean_median']}))
