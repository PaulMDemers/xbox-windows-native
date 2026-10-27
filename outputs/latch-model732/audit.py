"""Offline differential review; does not execute or reopen either closed model."""
import ast,datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'cases':[]}
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for n,h in read(K/'sources001.json').items():assert sha(K/n)==h
 for n,h in read(K/'source-reuse001.json')['inputs'].items():assert sha(K.parents[1]/n)==h
 original=(K.parent/'xcal-transaction704/transaction003.c').read_text()
 changed=(K/'transaction732.c').read_text()
 start=original.index('static int check_setup(')
 end=original.index('static int check_geometry',start)
 assert (K/'predicate-original.txt').read_text()==original[start:end]
 assert changed.startswith(original[:start]) and changed.endswith(original[end:])
 added=changed[start:len(changed)-len(original[end:])]
 for forbidden in ['cw(', 'sw(', 'w32(', 'out8(', '__asm__', 'indexed(', 'put(']:assert forbidden not in added
 assert added.count('r32(g,setup[i][0])')==1 and added.count('cr(g,cs[i][0])')==1
 assert 'if(value!=setup[i][1])' in added and 'if(value!=expected)' in added
 assert 'after_geometry&&cs[i][0]==0x19?0x30:cs[i][1]' in added
 for n in ['build001.json','build002.json']:
  b=read(K/n);assert b['passed']
  root=Path('C:/xwn732')/n.replace('.json','')
  for name,h in b['files'].items():assert sha(root/name)==h
 assert read(K/'build001.json')['same_binary_as704_build004']
 assert not read(K/'build002.json')['same_binary_as704_build004']
 a=read(K/'model001.json');b=read(K/'model002.json')
 assert a['passed'] and b['passed'] and a['case_count']==b['case_count']==48
 compared=['name','phase4_accepted','stopped_before_geometry','result_prefix','register_data_writes','reads','ports','failure_selectors_restored','initial_GR04','final_GR04','CR22_write_policy_counterfactual','initial_latches','final_latches']
 setup=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
 cs=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,5),(0x22,255),(0x33,0x11)]
 names=set()
 for x,y in zip(a['cases'],b['cases']):
  assert all(x[key]==y[key] for key in compared),x['name']
  name=x['name'];assert name not in names;names.add(name)
  if '-early-MMIO' in name:first,observed=0,0xdeadbeef
  elif '-early-CR1b85' in name:first,observed=14,0x85
  elif x['CR22_write_policy_counterfactual']=='ignored' and x['initial_GR04']!=3:
   first,observed=15,[0xfe,0xe7,0x5a,0xff][x['initial_GR04']]
  elif name.endswith('-CR33-zero'):first,observed=16,0
  else:first,observed=None,None
  count=17 if first is None else first+1
  assert x['phase4_accepted']==(first is None)
  cap=y['capture'];assert cap[:4]==[0x732,0,count,0xffffffff if first is None else first]
  entries=[[o,0xffffffff,v,v] for o,v in setup]+[[0x6013d5,i,v,v] for i,v in cs]
  if first is not None:entries[first][3]=observed
  assert cap[4:4+count*4]==[v for row in entries[:count] for v in row]
  assert all(v==0 for v in cap[4+count*4:])
  r['cases'].append({'name':name,'first_mismatch':first,'observed':observed,'count':count,'same_register_and_port_trace':True,'same_result':True})
 r['accepted_count']=sum(v['phase4_accepted'] for v in a['cases'])
 r['rejected_count']=48-r['accepted_count']
 r['instrumentation_only_changes_RAM_and_instruction_timing']=True
 r['physical_write_semantics_proved']=False
 r['limits']=['Only phase4/after_geometry=0 executed; later checks are source-reviewed only.','Inherited hardware GR04 and latch contents in708/709 remain unknown.','All CR22 write policies here are hypothetical.','RAM trace is not yet a physical reporting mechanism; no new hardware admission.']
 r['inputs']={n:sha(K/n) for n in ['model001.json','model002.json','build001.json','build002.json','transaction732.c','model.py','instrumented_model.py']}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS48 differential cases: same I/O and outcomes, independently checked first mismatch')
