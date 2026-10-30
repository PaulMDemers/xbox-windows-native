"""Fresh817 private photo geometry and independent optical reviewer."""
from pathlib import Path
import json,datetime
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-low813';P=Path('C:/xwn817')
def put(n,s):
 with (K/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
source=Path('C:/Users/Paul/.codex/codex-remote-attachments/01a0ff98-aa67-78c0-baa4-279c9bacf1d2/41B2F7A9-087D-401A-A5B3-848D41AF46EB/1-Photo-1.jpg')
with (P/'photo001.jpg').open('xb') as f:f.write(source.read_bytes())
s=(A/'photo_decode001.py').read_text().replace('813','817').replace('range(145,725)','range(190,765)').replace('range(80,1210)','range(70,1200)')
s=s.replace('top=165+11*(x-100)/1090;bottom=702-11*(x-100)/1090','top=209+12*(x-90)/1090;bottom=752-17*(x-90)/1090')
s=s.replace('fresh ROI25..1230,140..750','fresh ROI70..1200,190..765')
put('photo_decode001.py',s)
s=(A/'photo_review001.py').read_text().replace('813','817').replace('optical-schema002','optical-schema001')
s=s.replace("['cl18_before','cl18_after','cl18_restored']]==[255,255,255]","['CR1A_before','CR1A_after','CR1A_after_CR2D_undo_before_own_undo']]==[56,60,60]")
s=s.replace("==33 and len(schema['omitted_aggregate_masks'])==25","==34 and len(schema['omitted_aggregate_masks'])==27")
s=s.replace('Native CR09 line-compare FF/FF/FF and own-value recovery; photo-only result','Native preserving CR1A38/3C/3C interim result; final restoration aggregate-only')
s=s.replace('Eight displayed recovery masks zero; twenty-five omitted masks aggregate-only via final817; same-value dropped writes indistinguishable','Seven displayed cleanup masks plus one forward mask zero;27 omitted cleanup masks aggregate-only; last byte is interim after CR2D undo before own CR1A undo; same-value controls remain limited')
put('photo_review001.py',s)
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),user_observation='Green, ready',manual_reset_basis='standing photo/reset workflow plus Ready and authenticated dashboard002',photo_private='C:/xwn817/photo001.jpg',normal_Windows_shutdown=False)
put('observation001.json',json.dumps(r,indent=2)+'\n')
assert json.loads((K/'dashboard002.json').read_text())['authenticated']
put('collection-ready001.json',json.dumps(dict(dashboard_confirmed=True,manual_power_cycle_reported_by_standing_workflow=True,explicit_new_reset_reply=True,basis='User Green, ready after standing photograph then power-off/on workflow; dashboard002 independently authenticated'),indent=2)+'\n')
