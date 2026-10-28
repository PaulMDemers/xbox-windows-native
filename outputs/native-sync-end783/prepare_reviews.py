"""Prepare fresh783 reviewers before freezing source; no physical access."""
from pathlib import Path
K=Path(__file__).resolve().parent
for n in ['model.py','host_build005.py','audit_collection005.py','review_prepare002.py']:
 p=K/n;s=p.read_text().replace('payload003','payload004');p.write_text(s)
p=K/'review_prepare002.py';s=p.read_text().replace('link-review005','link-review006').replace("'CR13']","'CR13','NVVVALIDSTART']").replace('1480','1600').replace('0x56c8','0x5740').replace("'integration_cases':448","'integration_cases':487").replace('Ten masks omitted raw; final success requires all18','Eleven masks omitted raw; final success requires all19').replace('NVVSYNCSTART diagnostic only','NVVSYNCEND diagnostic only');p.write_text(s)
p=K/'source_review.py';s=p.read_text().replace("'native-valid-start779'","'native-sync-start781'").replace("'vertical-sync-start780'","'vertical-sync-end782'").replace("'780','783'","'782','783'").replace("'779'","'781'")
old='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x55ec,0x5664,0x5650,0x565c,0x5660'
new='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x5664,0x56dc,0x56c8,0x56d4,0x56d8'
a=s.index("old='");b=s.index("for n in ['main.c'",a);s=s[:a]+f"old='{old}'\nnew='{new}'\n"+s[b:]
s=s.replace("'memset(p+0x5000,0,0x650)','memset(p+0x5000,0,0x6c8)'","'memset(p+0x5000,0,0x6c8)','memset(p+0x5000,0,0x740)'")
s=s.replace("assert body.index('R32(0x68080c)","assert body.index('R32(0x680810)=o->se_before')<body.index('R32(0x68080c)")
s=s.replace('0x680(?:810|818)','0x680818').replace('0x780','0x782').replace("['vertical_sync_start']","['vertical_sync_end']").replace('[479,524,479,0,729,719,104,48]','[479,524,479,0,489,719,104,48]')
s=s.replace('==458','==497').replace('==448','==487').replace(',315,345]',',315,345,375]').replace('==370','==400')
# Keep predecessor assertions, with the tail now bounded to its own fields.
s=s.replace('v[340:]==','v[340:370]==')
at=s.index('pages=[]')
extra="""for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='se-'+phase+'-'+str(j))
  assert v[0]==(0x7832d if phase=='undo' else 0x7832c)
  if phase=='undo':assert v[375]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='se-coupling-'+str(j));assert v[0]==0x7832d and v[375]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert v[370:]==[729,492,1,492,729,0,479,479,479,524,524,524,479,479,479,0,0,0,489,489,489,719,719,719,104,104,104,48,48,48]
assert all(v[i]==0 for i in masks)
for name,code in [('se-drop-write',0x7832c),('se-wrong-write',0x7832c),('se-drop-undo',0x7832d),('se-wrong-undo',0x7832d)]:
 c=next(c for c in r['cases'] if c['name']==name);assert c['raw_result'][0]==code
assert all(a==0x680810 and n in [492,729] for c in r['cases'] for a,n in c['vertical_sync_end_writes'])
"""
s=s[:at]+extra+s[at:]
# Do not alter the report-table literal's legitimate address0x56c8.
at=s.index('pages=[]');head=s[:at];tail=s[at:].replace('0x56c8','0x5740').replace('0x68c','0x704').replace('0x938','0x8c0').replace('370*4','400*4')
tail=tail.replace("'vertical_valid_start_cleanup_mask',",'').replace("'vertical_sync_start_cleanup_mask',","'vertical_sync_start_cleanup_mask','vertical_sync_end_cleanup_mask',").replace('NVVSYNCSTART','NVVSYNCEND').replace("'CR13']","'CR13','NVVVALIDSTART']").replace("'total_masks_required_for_success':18","'total_masks_required_for_success':19").replace("'target_NVVSYNCEND':489","'target_NVVSYNCEND':492").replace('Ten masks','Eleven masks').replace('all18clear','all19clear').replace('matches780','matches782').replace('matches779','matches781').replace('1480','1600').replace("'model_cases':458","'model_cases':497").replace("'integration_cases':448","'integration_cases':487")
s=head+tail;p.write_text(s)
print('Prepared783 source/bounds/schema reviewers; no execution or hardware')
