"""Strict counted242 parser: reject missing/duplicate/extra fields and hidden slots."""
import re
def parse(text):
 items=re.findall(r'(?<![a-z0-9_])([a-z][a-z0-9_]*)=(\d+)',text)
 assert len(items)==len(dict(items))
 d={k:int(v) for k,v in items};keys={'version','state','published','cpu_callbacks_observed','gl_bindings_observed','retired','native_grant'}
 assert all(k in d for k in keys) and d['version']==242
 assert 0<=d['state']<=7 and d['published']==int(d['state'] in [3,4,6])
 assert not any(d[k] for k in ['cpu_callbacks_observed','gl_bindings_observed','retired','native_grant'])
 slots=[]
 if d['published']:
  for j in range(2):
   key=f'slot{j}_valid';keys.add(key);assert d[key] in [0,1]
   if not d[key]:slots.append({'valid':False});continue
   names=[f'slot{j}_{v}' for v in ['when','fifo_when','surfaces','textures']];keys.update(names)
   n=d[names[2]];m=d[names[3]];assert 0<=n<=128 and 0<=m<=512
   for prefix,width in [('f',14),('c',20),('r',48)]:keys.update(f'{prefix}{j}_{i}' for i in range(width))
   for prefix,count,width in [('s',n,12),('t',m,10),('b',4,4)]:keys.update(f'{prefix}{j}_{i}_{x}' for i in range(count) for x in range(width))
   def row(prefix,width):return [d[f'{prefix}{j}_{i}'] for i in range(width)]
   def rows(prefix,count,width):return [[d[f'{prefix}{j}_{i}_{x}'] for x in range(width)] for i in range(count)]
   slots.append(dict(valid=True,when=d[names[0]],fifo_when=d[names[1]],surfaces=rows('s',n,12),textures=rows('t',m,10),bindings=rows('b',4,4),fifo=row('f',14),context=row('c',20),stats=row('r',48)))
 assert set(d)==keys and all(0<=v<2**64 for v in d.values())
 return dict(version=d['version'],state=d['state'],published=d['published'],slots=slots,cpu_callbacks_observed=False,gl_bindings_observed=False,retired=False,native_grant=False)

def qualify(v,pre):
 assert v['state']==3 and len(v['slots'])==2 and all(s['valid'] for s in v['slots'])
 a,b=v['slots'];assert a['fifo_when']<=a['when']<=b['when']<=b['fifo_when']
 for s in [a,b]:
  assert s['fifo'][0]==s['stats'][0]==1
  assert s['fifo'][4:14]==pre['current_fifo'][4:14]
  assert not s['fifo'][2] and not any(s['stats'][1:7])
  assert s['context']==pre['context']
  assert s['stats'][37]==512 and s['stats'][42]==s['stats'][44]==s['stats'][47]==51200
  assert len(s['textures'])==s['stats'][13] and s['stats'][38]==s['stats'][15] and s['stats'][43]==s['stats'][17] and s['stats'][45]==s['stats'][19]
  assert all(s['stats'][i]+s['stats'][i+1]==cap for i,cap in [(13,512),(15,51200),(17,51200),(19,51200)])
 assert a['surfaces']==pre['surfaces']
 assert len(b['surfaces'])==len(a['surfaces'])==3
 for old,new in zip(a['surfaces'],b['surfaces']):
  assert old[:5]==new[:5] and old[6:]==new[6:]
  assert old[5]&3 and not new[5]&3 and old[5]&~3==new[5]&~3
 assert a['textures']==b['textures'] and a['bindings']==b['bindings']
 assert a['stats']==b['stats']
 return dict(passed=True,slots=2,dirty_before=3,dirty_after=0,callbacks_retained=sum(s[6] for s in b['surfaces']),producer_halted_during_samples=True,references_retired=False,native_ownership=False)
