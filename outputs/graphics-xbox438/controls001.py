"""Reject mutations of actual physical Xbox outputs with the unchanged public oracle."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_sample as g
record=json.loads((K/'runtime-review001.json').read_text());assert record['all_allowed_cases_passed']
root=W/'work/graphics438/physical001/after/E/xwn438'
out=K/'controls001.json';assert not out.exists()
checks=[]
def reject(label,fn):
 try:fn()
 except (ValueError,AssertionError):checks.append(label)
 else:raise AssertionError('Accepted mutation: '+label)
for row in record['rows']:
 name=row['name'];raw=(root/(name+'.txt')).read_bytes();fields=g.decode(raw)
 source=(root/(name+'-source.bin')).read_bytes() if fields['rung']!='01' else None
 dest=(root/(name+'-dest.bin')).read_bytes() if fields['rung']!='01' else None
 g.validate(fields,source,dest,0)
 reject(name+':external-exit',lambda:g.validate(fields,source,dest,1))
 for label,bad in [('terminal',raw.replace(b'end=complete',b'end=incomplete')),('missing-terminal',raw[:raw.rfind(b'end=complete')]),('duplicate',raw.replace(b'end=complete',b'exit=0\nend=complete')),('exit',raw.replace(b'exit=0',b'exit=1')),('scope',raw.replace(b'scope=user-mode-sample',b'scope=hardware'))]:
  reject(name+':'+label,lambda bad=bad:g.decode(bad))
 for key,value in fields.items():
  if key.endswith(('.lock','.unlock','.create','.cooperative','.caps','.mode','.blit')) and value=='00000000':
   bad=dict(fields);bad[key]='80004005';reject(name+':'+key,lambda bad=bad:g.validate(bad,source,dest,0))
 if source is not None:
  for label,data,w,h in [('source',source,64,48),('dest',dest,96,80)]:
   for y in [0,3,4,9,10,35,41,47,h-1]:
    for x in [0,3,8,31,50,w-1]:
     bad=bytearray(data);bad[(y*w+x)*4]^=1
     reject(name+':'+label+f':{x},{y}',lambda bad=bytes(bad),label=label:g.validate(fields,bad if label=='source' else source,bad if label=='dest' else dest,0))
for row in json.loads((K/'physical001-collection.json').read_text())['files'].values():
 p=Path('/mnt/'+row['path'][0].lower()+row['path'][2:].replace('\\','/'));assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
out.write_text(json.dumps(dict(passed=True,actual_mutations_rejected=len(checks),checks=checks,originals_unchanged=True,physical_qualification=False),indent=2)+'\n')
print('Actual physical Xbox mutations rejected:',len(checks))
