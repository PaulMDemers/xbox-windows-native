"""Source-only derive813 photo and collection auditing; no runtime reuse."""
from pathlib import Path
import json,datetime
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-bit811'
def put(n,s):
 with (K/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
s=(A/'photo_review003.py').read_text().replace('811','813').replace('photo002.json','photo001.json').replace('photo_decode002.py','photo_decode001.py').replace('photo-review003.json','photo-review001.json').replace('optical-schema001.json','optical-schema002.json')
s=s.replace("fields['return_code']","fields['final_code']").replace('CR09_linecompare','cl18').replace('[64,64,64]','[255,255,255]').replace('==32 and len(schema','==33 and len(schema').replace('])==24','])==25').replace('twenty-four','twenty-five').replace('40/40/40','FF/FF/FF').replace("decode_failures_preserved=['photo001.json']","decode_failures_preserved=[]")
put('photo_review001.py',s)
s=(A/'audit_collection003.py').read_text().replace('811','813').replace('audit003.json','audit001.json').replace('photo002.json','photo001.json').replace('photo-review003.json','photo-review001.json').replace('photo_decode002.py','photo_decode001.py').replace('optical-schema001.json','optical-schema002.json').replace('==32 and len(schema','==33 and len(schema').replace('])==24','])==25').replace('[64,64,64]','[255,255,255]').replace('CR09_linecompare','CR18_linecompare')
s=s.replace("o['user_observation']=='Green'","o['user_observation']=='Green, Xbox back at dash'")
put('audit_collection001.py',s)
assert json.loads((K/'dashboard002.json').read_text())['authenticated']
put('observation001.json',json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'user_observation':'Green, Xbox back at dash','manual_reset_basis':'standing photo/reset workflow with authenticated dashboard, not a new Ready reply','normal_shutdown':False},indent=2)+'\n')
put('collection-ready001.json',json.dumps({'dashboard_confirmed':True,'manual_power_cycle_reported_by_standing_workflow':True,'explicit_new_reset_reply':False,'basis':'User supplied813 photo and said Green, Xbox back at dash; standing workflow is photo then power off/on; dashboard002 authenticated','normal_windows_shutdown':False},indent=2)+'\n')
print('Prepared fresh813 closure tools; no relaunch')
