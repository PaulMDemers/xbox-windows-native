"""Cold physical receipts, independent sample bytes, events and hive checks."""

import hashlib,json,os,subprocess,sys

from pathlib import Path

K=Path(__file__).resolve().parent;W=K.parents[1]

sys.path.insert(0,str(W/'tools'));import graphics_texture as g

sys.path.insert(0,str(W/'work/python-packages'))

sys.path.insert(0,str(K.parent/'clean-media404'));from hive_audit004 import audit

def hostpath(s):

 if len(s)>2 and s[1]==':':return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/'))

 return Path(s)

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

out=K/'runtime-review001.json';assert not out.exists()

c=json.loads((K/'physical001-collection.json').read_text());before=json.loads((K/'physical001-stage.json').read_text())

assert c['completed'] and c['hook_removed'] and c['protected_code_exact'] and c['mode']=='720p'

files={n:hostpath(r['path']) for n,r in c['files'].items() if r is not None}

for n,p in files.items():assert sha(p)==c['files'][n]['sha256']

def fields(raw):

 assert 0<len(raw)<=262144

 d={}

 for line in raw.decode('ascii').splitlines():

  key,sep,value=line.partition('=');assert sep and key and value and key not in d;d[key]=value

 return d

runner=fields(files['/E/xwn478/runner.txt'].read_bytes())

expected={'schema','pid','start_tick','completed_cases','end_tick','restart_privilege','restart_request'}|{f'case{i}_{s}' for i in range(2) for s in ['start_tick','pid','wait','exit']}

assert set(runner)==expected and all(v.isdecimal() and 0<=int(v)<=0xffffffff for v in runner.values())

assert runner['schema']=='478' and runner['completed_cases']=='2' and runner['restart_privilege']=='1' and runner['restart_request']=='1'

root=files['/E/xwn478/runner.txt'].parent

assert sha(root/'d3d.exe')=='0cf77cd741d0f066ee5a3fc4ad10508f3e6d8cb962c8a89c90fc19d6ee832f91'

r=dict(scope='Actual installed Xbox Windows sample control; no GPU or game qualification',runner=runner,rows=[],hives={},events={})

for i,(name,backend) in enumerate([('r08d','default'),('r08s','hel')]):

 assert runner[f'case{i}_wait']=='0'

 code=(root/(name+'.exit')).read_text().strip();assert code==runner[f'case{i}_exit']

 f=fields((root/(name+'.txt')).read_bytes());assert [f[n] for n in ['os.major','os.minor','os.build']]==['5','0','2195']

 row=dict(name=name,backend=backend,process_exit=int(code),fields=f)

 try:row['review']=g.validate((root/(name+'.txt')).read_bytes(),(root/(name+'-clear.bin')).read_bytes(),(root/(name+'-draw.bin')).read_bytes(),(root/(name+'-source-before.bin')).read_bytes(),(root/(name+'-source-after.bin')).read_bytes(),backend,int(code))

 except Exception as e:row['review_failure']=str(e)

 r['rows'].append(row)

 for p in root.glob(name+'*'):

  if p.suffix in ['.txt','.exit']:(K/('physical001-'+p.name)).write_bytes(p.read_bytes())

(K/'physical001-runner.txt').write_bytes((root/'runner.txt').read_bytes())

for name in ['system','software','sam','security','default']:

 p='/E/winnt/system32/config/'+name

 r['hives'][name]={'before':audit(hostpath(before['before'][p]['path'])),'after':audit(files[p])}

 assert all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for v in r['hives'][name].values())

for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:

 p='/E/winnt/system32/config/'+name;events={}

 for phase,path in [('before',hostpath(before['before'][p]['path'])),('after',files[p])]:

  dest=path.with_name(label+'-events.json');assert not dest.exists()

  subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)

  events[phase]=json.loads(dest.read_text())['records']

 boundary=max((e['record'] for e in events['before']),default=0)

 new=[{k:e[k] for k in ['record','source','event_id','type','generated_unix']} for e in events['after'] if e['record']>boundary]

 delta=sum(e['source']=='EventLog' and e['event_id']==6006 for e in events['after'])-sum(e['source']=='EventLog' and e['event_id']==6006 for e in events['before'])

 r['events'][label]=dict(new_records=new,normal_shutdown_delta=delta,scope='Validated record scan; active-ring completeness not proved')

r['all_allowed_cases_passed']=all(row.get('review',{}).get('passed') is True for row in r['rows'])

r['normal_restart_supported']=r['events']['system']['normal_shutdown_delta']==1

r['frozen_dependencies']={}

for p,h in json.loads((K/'package001.json').read_text())['dependencies'].items():assert sha(hostpath(p))==h;r['frozen_dependencies'][p]=h

r.update(hardware_acceleration_proved=False,full_allocation_audit=False,visual_qualified=False)

out.write_text(json.dumps(r,indent=2)+'\n')

print(json.dumps({k:r[k] for k in ['all_allowed_cases_passed','normal_restart_supported','hardware_acceleration_proved']}))

