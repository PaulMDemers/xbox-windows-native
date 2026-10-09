"""Bounded raw numeric201 log verification, no UI or qualification waiver."""
def analyze(data):
    assert len(data)<=1024*1024 and data.endswith(b'\r\n')
    lines=data.decode('ascii').splitlines();rows=[]
    for line in lines:
        parts=line.split();assert len(parts)==4
        values=[int(x) for x in parts[1:]];assert all(0<=x<=0xffffffff for x in values)
        rows.append(dict(label=parts[0],values=values))
    start=[v for v in rows if v['label']=='START201'];end=[v for v in rows if v['label']=='TIMEOUT201']
    matches=[v for v in rows if v['label']=='MATCHED_WINDOW']
    actions=[v for v in rows if v['label'].startswith('CANCEL_')]
    states=[v for v in rows if v['label']=='INSTALL_STATE']
    failures=[v for v in rows if v['label'].startswith('FAIL_')]
    good=(len(start)==1 and start[0]['values']==[0,1,120000] and len(end)==1 and
          end[0]['values'][0:2]==[0,0] and end[0]['values'][2]>=120000 and
          matches and all(v['values'][0]>0 and v['values'][1]>0 and 1<=v['values'][2]<=5 for v in matches) and
          states and any(v['values'][0]==258 for v in states) and not actions and not failures)
    return dict(passive_observation_passed=bool(good),row_count=len(rows),matched_windows=len(matches),
                target_ids=sorted(set(v['values'][2] for v in matches)),action_count=len(actions),failures=failures,
                timeout=end,pending_queries=sum(v['values'][0]==258 for v in states),rows=rows)
