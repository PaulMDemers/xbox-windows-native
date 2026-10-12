"""Independent comparison/register/source-byte interpretation of closed321."""
import copy,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
plan=json.loads((k/'plan.json').read_text());trace=json.loads((k/'candidate001/trace.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def verify(t):
    assert t['status']=='captured' and t['resident_pins_passed']
    assert t['breakpoint_removed'] and t['physical_mode_restored'] and t['resumed'] and not t.get('teardown_error')
    assert not t['guest_memory_writes'] and not t['guest_register_writes']
    caps={Path(v['path']).name:v for v in t['captures']}
    for name,v in caps.items():
        b=Path(v['path']).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256']
    for i,c in enumerate(t['conditions']):
        assert c['point']==plan['condition_points'][i] and c['registers'][8]==c['point'] and c['registers'][10]&3==0
        regs=c['registers'];expected_address=regs[4]+0x5c if i==0 else regs[2]+0x38+regs[3]*4
        v=caps[f'condition{i}-expected.bin'];assert v['address']==expected_address==c['expected_address']
        expected=int.from_bytes(Path(v['path']).read_bytes(),'little');actual=(regs[0]&255) if i==0 else regs[0]
        assert (c['expected'],c['actual'],c['zero_flag'])==(expected,actual,bool(regs[9]&0x40))
        text=b''.join(Path(caps[f'condition{i}-text-{off}.bin']['path']).read_bytes() for off in range(0,plan['text']['bytes'],65536))
        assert sha(text)==plan['text']['sha256']
        assert text[c['point']-plan['text']['va']]==0x75 # short JNE
        assert bool(regs[9]&0x40)==(actual==expected)
    assert len(t['conditions'])==2
    assert (t['conditions'][0]['actual'],t['conditions'][0]['expected'])==(16,16)
    assert (t['conditions'][1]['actual'],t['conditions'][1]['expected'],t['conditions'][1]['registers'][3])==(0,1124,7)
    assert t['state']['error']==25 and t['state']['failure_stage']==4 and t['result_signed']==-1
    assert t['current_crtc']=={'index':57,'value':16}
verify(trace)
count=0
for i in range(2):
    for field in ['actual','expected','point','expected_address']:
        t=copy.deepcopy(trace);t['conditions'][i][field]^=1
        try:verify(t)
        except AssertionError:count+=1
        else:raise AssertionError(field)
    for idx in [0,8,9]:
        t=copy.deepcopy(trace);t['conditions'][i]['registers'][idx]^=64 if idx==9 else 1
        try:verify(t)
        except AssertionError:count+=1
        else:raise AssertionError(idx)
r={'passed':True,'actual_mutations_rejected':count,'captures_rehashed':len(trace['captures']),'trace_sha256':sha((k/'candidate001/trace.json').read_bytes()),'failing_offset':'0x680804','actual':0,'expected':1124,'crtc39_passed':True,'ordinary_qualified':False}
assert not (k/'conditions-review.json').exists();(k/'conditions-review.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
