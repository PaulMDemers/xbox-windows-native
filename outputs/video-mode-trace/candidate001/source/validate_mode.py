"""Verify bounded runtime callback pairs and report only observed transitions."""
import struct
from mode_observer import FUNCTIONS

def validate(trace):
 stages=trace.get('mode_stages',[]);calls=trace.get('mode_calls',[])
 r=dict(passed=False,assert_cycle=False,surface_replacement=False,calls=len(calls),unobserved=[])
 try:
  assert trace.get('mode_interval_complete') and len(stages)==3 and len(calls)<=64
  for i,s in enumerate(stages):
   assert s['args'][0]==i and not s['args'][2] and not s['pending']
   assert s['owner']==trace['probe_entry']['owner']
   assert s['module']==stages[0]['module']
  assert stages[0]['call_count']==0 and stages[1]['call_count']==stages[2]['call_count']==len(calls)
  assert not stages[0]['args'][3] and not stages[1]['args'][3] and stages[2]['args'][3]
  for i,c in enumerate(calls):
   assert c['index']==i and c['name'] in FUNCTIONS
   argc,stdcall=FUNCTIONS[c['name']];assert c['argc']==argc and c['stdcall']==stdcall and len(c['args'])==argc+1
   ret=c['return'];assert ret['owner']==c['owner']
   assert ret['registers']['EIP']==c['args'][0]
   assert ret['registers']['ESP']==c['entry_registers']['ESP']+4+(4*argc if stdcall else 0)
   assert c['module']==stages[0]['module']
   for key in ['before','after']:
    v=c.get(key)
    if v is None:continue
    assert list(v['fields'].values())==list(struct.unpack('<7I',bytes.fromhex(v['raw']))) and v['fields']['active'] in [0,1]
   name=c['name'];eax=ret['registers']['EAX'];before=c.get('before');after=c.get('after')
   if name not in ['DrvEnablePDEV','XwnOwnershipDisable']:assert before['address']==c['args'][1]
   if name not in ['DrvDisablePDEV','DrvEnablePDEV','XwnOwnershipDisable']:assert after['address']==c['args'][1]
   if name=='DrvEnablePDEV':assert eax and after['address']==eax
   if name=='DrvCompletePDEV':assert after['fields']['hdev']==c['args'][2]
   if name=='DrvAssertMode':
    assert eax==1 and c['args'][2] in [0,1] and after['fields']['active']==c['args'][2]
   if name=='DrvEnableSurface':
    assert eax and after['fields']['primary']==eax and after['fields']['active']==1
    assert all(after['fields'][n] for n in ['shadow_surface','shadow_object','shadow_bits'])
   if name=='DrvDisableSurface':assert all(after['fields'][n]==0 for n in ['primary','shadow_surface','shadow_object','shadow_bits','active'])
   if name=='XwnRegisterPrimary':assert eax==1
  asserts=[c for c in calls if c['name']=='DrvAssertMode']
  cycles=[(a,b) for a in asserts for b in asserts if a['index']<b['index'] and a['args'][1]==b['args'][1] and a['args'][2]==0 and b['args'][2]==1 and a['before']['fields']['active']==1]
  enables=[c for c in calls if c['name']=='DrvEnableSurface'];disables=[c for c in calls if c['name']=='DrvDisableSurface']
  replacements=[(a,b) for a in enables for b in disables if a['args'][1]!=b['args'][1] and a['after']['fields']['primary']!=b['before']['fields']['primary'] and
   any(v['name']=='DrvEnablePDEV' and v['return']['registers']['EAX']==a['args'][1] for v in calls) and
   any(v['name']=='DrvDisablePDEV' and v['args'][1]==b['args'][1] for v in calls) and
   any(v['name']=='XwnRegisterPrimary' and v['args'][1]==a['args'][1] for v in calls) and
   any(v['name']=='XwnUnregisterPrimary' and v['args'][1]==b['args'][1] for v in calls)]
  r.update(passed=bool(cycles or replacements),assert_cycle=bool(cycles),surface_replacement=bool(replacements),
   observed=[c['name'] for c in calls],unobserved=[n for n in FUNCTIONS if not any(c['name']==n for c in calls)],
   assert_cycle_pairs=[[a['index'],b['index']] for a,b in cycles],replacement_pairs=[[a['index'],b['index']] for a,b in replacements])
 except (AssertionError,KeyError,IndexError,ValueError,TypeError) as exc:r['error']=repr(exc)
 return r
