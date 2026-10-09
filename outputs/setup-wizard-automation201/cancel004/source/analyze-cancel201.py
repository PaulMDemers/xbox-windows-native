"""Verify durable target/action/closure/idle and genuine guardian restart sequence."""
def analyze(data,guardian):
    assert len(data)<=1024*1024 and data.endswith(b'\r\n')
    rows=[]
    for line in data.decode('ascii').splitlines():
        parts=line.split();assert len(parts)==4
        values=[int(x) for x in parts[1:]];assert all(0<=x<=0xffffffff for x in values)
        rows.append((parts[0],values))
    starts=[v for label,v in rows if label=='START201'];idles=[v for label,v in rows if label=='IDLE201']
    intents=[];sent=[];closed=[];pending=None;errors=[]
    for label,v in rows:
        if label.startswith('FAIL_') or label=='TIMEOUT201':errors.append((label,v))
        if label=='CANCEL_INTENT':
            assert pending is None and v[0]>0 and v[1]>0 and 1<=v[2]<=5
            assert not any(old[0]==v[0] for old in intents)
            intents.append(v);pending=v
        if label=='CANCEL_SENT':assert pending==v;sent.append(v)
        if label=='CANCEL_WINDOW_CLOSED':
            assert pending and v[:2]==pending[:2] and v[2]==0 and sent[-1]==pending
            closed.append(v);pending=None
    g=guardian.decode('ascii').splitlines()
    def last(label):
        found=[int(line.split()[1]) for line in g if line.split()[0]==label]
        return found[-1] if found else None
    good=(starts==[[1,1,120000]] and len(idles)==1 and idles[0][0]>=5000 and
          1<=len(intents)<=8 and len(sent)==len(intents)==len(closed)==idles[0][1] and
          not pending and not errors and last('HELPER_JOIN_RESULT')==0 and last('HELPER_EXIT')==0 and
          last('SETUP_IDLE_OBSERVED_MS') is not None and last('SETUP_IDLE_OBSERVED_MS')>=5000 and
          last('INSTALL_WAIT_RESULT')==0 and last('INSTALL_FINAL_RESULT')==0 and
          g.count('NORMAL_RESTART_REQUEST 0')==1 and
          not any(line.startswith(('FAIL_','RESTART_BLOCKED')) for line in g))
    return dict(cancellation_lifecycle_passed=bool(good),actions=len(intents),targets=[v[2] for v in intents],
                intents=intents,sent=sent,closed=closed,helper_idles=idles,failures=errors,guardian_lines=g,
                limits='Only exact known guest Cancel messages; real queue idle and joined helper. Not device support, physical or strict event qualification.')
