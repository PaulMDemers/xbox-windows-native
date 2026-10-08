"""Prospective gate correction; never alter executed source packets or launch."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
FIELDS=['source','event_id','type','strings','data_hex']
def eligible(a,expected):
    reasons=[]
    if not a.get('workload_passed') or not a.get('integrity_passed'):reasons.append('Incomplete workload/integrity')
    if not a.get('event_history_preserved'):reasons.append('Changed event history')
    if a.get('new_events',{}).get('application'):reasons.append('Application event delta')
    if any(v['source']=='Application Popup' for v in a.get('new_events',{}).get('system',[])):reasons.append('Application Popup, including informational type4')
    actual=a.get('warnings_errors',[])
    if len(actual)!=len(expected) or any(any(v[f]!=e[f] for f in FIELDS) for v,e in zip(actual,expected)):reasons.append('Unexpected warning/error signature')
    if not all(v.get('counters_passed') for v in a.get('samples',[])) or len(a.get('samples',[]))!=5:reasons.append('Incomplete counters')
    return dict(eligible=not reasons,reasons=reasons,strict_release_qualified=False)
if __name__=='__main__':
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
    actual=read(k/'candidate001/audit.json');result=eligible(actual,expected)
    assert not result['eligible'] and result['reasons']==['Application Popup, including informational type4']
    clean=dict(actual,new_events=dict(system=[v for v in actual['new_events']['system'] if v['source']!='Application Popup'],application=[]))
    assert eligible(clean,expected)['eligible']
    for typ in [1,2,4,8,16]:
        changed=dict(clean,new_events=dict(system=clean['new_events']['system']+[dict(source='Application Popup',type=typ)],application=[]))
        assert not eligible(changed,expected)['eligible']
    dest=k/'eligibility-correction.json';assert not dest.exists()
    dest.write_text(json.dumps(dict(actual_emulator=result,all_popup_types_rejected=True,
        executed_gate_missed_informational_popup=True,physical_already_closed_and_restored=True,
        executed_source_packets_unchanged=True,future_gate_only=True),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
