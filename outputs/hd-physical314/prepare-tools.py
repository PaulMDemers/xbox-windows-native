from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'demo-physical253'
for name in ['audit.py','typed-state001.py','installed-binding001.py']:
 s=(p/name).read_text().replace('combined001','physical001').replace('before002','before001').replace("remote='xwnd253'","remote='xwnhd314'")
 if name=='typed-state001.py':s='\n'.join(v for v in s.split('\n') if not v.startswith("p['before']['system']="))
 if name=='audit.py':
  s=s.replace("offline_registry_edits='exact two video tokens, audio unchanged'","offline_registry_edits='none; temporary six-file720p chain only'")
  s=s.replace("r['scoped_combined_passed']=all(r[n] for n in fields)","r['mode720p_passed']=all(v.get('identity',[None]*7)[2:7]==[1280,720,5120,32,3686400] for v in r['samples'])\nfields+=['mode720p_passed']\nr['scoped_combined_passed']=all(r[n] for n in fields)")
  s=s.replace('Actual bound drivers retained only if scoped candidate accepted.','All six candidate files restored to incoming baseline after staged-byte capture regardless of scoped outcome.')
 (k/name).write_text(s,newline='\n')
s=(p/'scan001.py').read_text().replace("['baseline001','combined001','playback001','restored001']","['physical001']")
s=s.replace("dict(baseline001='XWND253scanB',combined001='XWND253scanI',playback001='XWND253scanP',restored001='XWND253scanR')[case]","dict(physical001='XWNHD314scan')[case]")
s=s.replace("assert read(k/'capture002.json')['passed'] if case=='baseline001' else read(out/('restoration.json' if case=='restored001' else 'collection.json'))['completed']","assert read(out/'collection.json')['completed'] and read(out/'collection.json')['baseline_restored']")
s=s.replace("check_fixed(f,staged=(case=='combined001'))","check_fixed(f)")
(k/'scan001.py').write_text(s,newline='\n')
