"""Analyze retained734 evidence only. No execution, physical access or recollection."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'analysis001.json';assert not out.exists()
a=read(K/'audit001.json');assert a['passed'];r=a['result'];v=a['raw_result']
assert r['direct']==[5]*8+[0x85]*8 and r['indexed']==[0x85]*16
assert r['sample630']==[2,2] and r['sample_counts']==[16,16]
assert r['first_mismatch']==14 and r['expected']==5 and r['observed']==0x85
assert r['cleanup_ok'] and r['cleanup_mask']==0 and r['selectors_restored']
previous=read(K.parent/'batch-prefix733/audit001.json');assert previous['passed']
p=previous['raw_result']
assert v[2:8]==p[2:8] and v[8:76]==p[8:76]
pins=read(K/'sources001.json')
for n,h in pins.items():assert sha(K/n)==h
model=read(K/'model001.json');assert model['passed']
case=model['cases'][0];reads=case['reads']
# The model's source-derived trace, not a physical bus trace: all32 observations
# happen before forward checking and before recovery. Direct block has no other
# device read; dynamic model asserts no selector writes during its16 accesses.
observations=[x for x in reads if x[3]==0x7344 and not x[4]]
# CR11 and CR22 unlock checks precede the sample interval in this phase.
samples=observations[2:]
assert len(samples)==34
assert [x[0] for x in samples]==[0x6013d5]*16+[0x680630]+[0x6013d5]*16+[0x680630]
assert case['writes'].count(['cr',0x1b,5])==1
assert not any(x[0]=='cr' and x[1]==0x1b and x[2]!=5 for x in case['writes'])
data={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'inputs':{str(p):sha(p) for p in [K/'audit001.json',K/'collection001.json',K/'sources001.json',K/'model001.json',K.parent/'batch-prefix733/audit001.json']},'first_changed_direct_sample_one_based':9,'direct_before':{'count':8,'value':5},'direct_after':{'count':8,'value':133},'reselected':{'count':16,'value':133},'630_after_blocks':[2,2],'physical_vs733_equal':['prefix write counts','first deferred mismatch/expected/observed/check count','entry/critical/restored flags','actual CR0/3/4','all saved/checked/final register fields'],'conclusion':'Full-byte CR1b readback changes05to85 within the direct-read block before selector reselection or recovery; later85 does not imply that05 was never observable.','not_established':['Meaning or write/read semantics of bit7','Elapsed time or exactly eight physical bus cycles as trigger','Read side effect versus autonomous device transition versus another mechanism','Safe writable/validation mask','Native708/709 first failure or corrected full-mode recipe'],'state':'734 CLOSED; automatic dashboard return, no manual reset; no hook or owned host process/VM'}
out.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
