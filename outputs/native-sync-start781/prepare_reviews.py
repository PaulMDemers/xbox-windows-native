"""Prepare fresh781 reviewers from retained779 sources, never closed runtime."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;O=K.parent/'native-valid-start779'
def ns(s):return re.sub(r'(?<![0-9])779(?![0-9])','781',re.sub(r'0x779(?=[0-9a-f]*\b)','0x781',s))
p=K/'integration005.py';s=p.read_text().replace('(0x680824,781)','(0x680824,779)');p.write_text(s,newline='\n')
p=K/'audit_collection004.py';s=p.read_text().replace('Audit781 preparation and NVVVALIDSTART','Audit781 preparation and NVVSYNCSTART').replace('native_NVVVALIDSTART_raw_values_exposed=True','native_NVVSYNCSTART_raw_values_exposed=True').replace('native_seven_displayed','native_eight_displayed');p.write_text(s,newline='\n')
s=ns((O/'source_review.py').read_text()).replace("'native-vertical-crtc777'","'native-valid-start779'").replace("'vertical-valid-start778'","'vertical-sync-start780'")
s=s.replace("'778','781'","'780','781'").replace("'777','781'","'779','781'").replace("n.replace('781','777')","n.replace('781','779')")
s=s.replace("old='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x54b4,0x5514,0x5574,0x5560,0x556c,0x5570'", "old='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x55ec,0x55dc,0x55d8,0x55e4,0x55e8'")
s=s.replace("new='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x55ec,0x55dc,0x55d8,0x55e4,0x55e8'", "new='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x55ec,0x5664,0x5650,0x565c,0x5660'")
s=s.replace("'memset(p+0x5000,0,0x5d8)','memset(p+0x5000,0,0x650)'","'memset(p+0x5000,0,0x650)','memset(p+0x5000,0,0x6c8)'")
s=s.replace("body.index('R32(0x680814)=o->vs_before')", "body.index('R32(0x68080c)=o->sy_before')<body.index('R32(0x680814)=o->vs_before')")
s=s.replace('(?:80c|810|818)','(?:810|818)').replace('audit002.json','audit001.json').replace('0x778','0x780')
s=s.replace("['vertical_valid_start']","['vertical_sync_start']").replace('[479,524,479,724,729,719,104,48]','[479,524,479,0,729,719,104,48]')
s=s.replace('419','458').replace('409','448').replace('==340','==370').replace('261,285,315]','261,285,315,345]')
s=s.replace("'vs-'+phase", "'sy-'+phase").replace("'vs-coupling-'", "'sy-coupling-'").replace('0x78129','0x7812b').replace('0x78128','0x7812a').replace('v[315]','v[345]')
start=s.index('assert v[310:]');end=s.index('pages=[]',start)
s=s[:start]+'''assert v[340:]==[724,489,1,489,724,0,479,479,479,524,524,524,479,479,479,0,0,0,729,729,729,719,719,719,104,104,104,48,48,48]
assert all(v[i]==0 for i in masks)
for name,code in [('sy-drop-write',0x7812a),('sy-wrong-write',0x7812a),('sy-drop-undo',0x7812b),('sy-wrong-undo',0x7812b)]:
 c=next(c for c in r['cases'] if c['name']==name);assert c['raw_result'][0]==code
assert all(a==0x68080c and n in [489,724] for c in r['cases'] for a,n in c['vertical_sync_start_writes'])
assert all(a==0x680814 and n==0 for c in r['cases'] for a,n in c['vertical_valid_start_writes'])
'''+s[end:]
s=s.replace('0x5650','0x56c8').replace('0x614','0x68c').replace('0x9b0','0x938').replace('340*4','370*4').replace('1360','1480')
# The row for sy_before remains 5650; do not replace that optical offset.
s=s.replace('0x5664,0x56c8,0x565c','0x5664,0x5650,0x565c')
s=s.replace("'NVVVALIDSTART_target','NVVVALIDSTART_before','NVVVALIDSTART_after','NVVVALIDSTART_restored'", "'vertical_sync_start_cleanup_mask','NVVSYNCSTART_before','NVVSYNCSTART_after','NVVSYNCSTART_restored'")
s=s.replace("'total_masks_required_for_success':17,'target_NVVVALIDSTART':0", "'total_masks_required_for_success':18,'target_NVVSYNCSTART':489")
s=s.replace('all17clear','all18clear').replace('matches778','matches780').replace('matches777','matches779')
(K/'source_review.py').write_text(s,newline='\n')
s=ns((O/'review_prepare.py').read_text()).replace('1360','1480').replace('0x5650','0x56c8').replace("'integration_cases':409","'integration_cases':448").replace('all17','all18').replace('NVVVALIDSTART diagnostic only','NVVSYNCSTART diagnostic only').replace("'extend_integration.py']","'extend_integration.py','prepare_reviews.py']")
(K/'review_prepare.py').write_text(s,newline='\n')
print('Prepared781 reviewers and corrected source-only namespace collision in horizontal target779')
