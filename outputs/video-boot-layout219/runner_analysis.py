"""Exact joined-helper prelude, actual Cancel lifecycle, then unchanged194 boundary grammar."""
from boundary_analysis import analyze as boundary


def helper(data,mode):
    assert isinstance(data,bytes) and len(data)<=1024*1024 and data.endswith(b'\r\n')
    rows=[]
    for line in data.decode('ascii').splitlines():
        p=line.split();assert len(p)==4
        v=[int(x) for x in p[1:]];assert all(0<=x<=0xffffffff for x in v)
        rows.append((p[0],v))
    assert [v for label,v in rows if label=='START201']==[[1,mode,120000]]
    owners=[];intents=[];closed=[];pending=None;owner=None;closed_owner=None;sent=[]
    for label,v in rows:
        assert not label.startswith('FAIL_') and label!='TIMEOUT201'
        if label=='CANCEL_OWNER':assert v[0] and v not in owners;owners.append(v);owner=v
        if label=='CANCEL_INTENT':
            assert pending is None and owner and owner[0]==v[0] and v[1] and 1<=v[2]<=4+mode
            intents.append(v);pending=v
        if label=='CANCEL_SENT':assert pending==v;sent.append(v)
        if label=='CANCEL_CLOSED_OWNER':closed_owner=v
        if label=='CANCEL_WINDOW_CLOSED':
            assert pending and v[:2]==pending[:2] and v[2]==0 and sent[-1]==pending and closed_owner==owner
            closed.append(v);pending=None
    idles=[v for label,v in rows if label=='IDLE201']
    assert rows[-1][0]=='IDLE201' and len(idles)==1 and idles[0][0]>=5000 and idles[0][2]<120000
    assert not pending and len(owners)==len(intents)==len(sent)==len(closed)==idles[0][1]<=8
    active=[v for label,v in rows if label=='CANCEL_ACTIVE_VERIFIED']
    fg=[v for label,v in rows if label=='FG_BEFORE'];gui=[v for label,v in rows if label=='GUI_BEFORE_ACTIVE']
    capture=[v for label,v in rows if label=='GUI_BEFORE_CAPTURE']
    assert len(active)==len(fg)==len(gui)==len(capture)==len(intents)
    assert all(a[:2]==i[:2] and f[:2]==i[:2] and g[1]==i[1] and c==[0,0,0]
               for a,f,g,c,i in zip(active,fg,gui,capture,intents))
    return dict(passed=True,mode=mode,actions=len(intents),targets=[v[2] for v in intents],owners=owners,
                closed=closed,actual_idle=idles[0])


def analyze(log,snapshots,wizard,mode):
    r=dict(idle_branch_passed=False,pending_branch_passed=False,cancellation_passed=False)
    try:
        h=helper(wizard,mode);lines=(log or '').splitlines();assert lines[0]=='ATTEMPT_ONCE'
        def number(at,label):
            p=lines[at].split();assert len(p)==2 and p[0]==label
            v=int(p[1]);assert 0<=v<=0xffffffff;return v
        def timestamp(at,label):
            p=lines[at].split();assert len(p)==3 and p[0]==label
            lo,hi=map(int,p[1:]);assert 0<=lo<=0xffffffff and 0<=hi<=0xffffffff
            return (hi<<32)|lo
        start=timestamp(1,'WIZARD_START_TIME');assert number(2,'WIZARD_MODE')==mode
        pid=number(3,'WIZARD_STARTED');assert pid>0
        assert number(4,'WIZARD_JOIN_RESULT')==0 and number(5,'WIZARD_EXIT')==0
        end=timestamp(6,'WIZARD_END_TIME');assert 0<start<=end and end-start<=150000*10000
        projected='\n'.join([lines[0]]+lines[7:])
        b=boundary(projected,snapshots)
        wait=[v.split() for v in lines if v.startswith('SETUP_WAIT_START_TIME ')]
        assert len(wait)==1 and len(wait[0])==3
        assert end<=(int(wait[0][2])<<32)|int(wait[0][1])
        r.update(b,cancellation_passed=True,helper=h,helper_pid=pid,
                 prelude=dict(start_filetime=start,end_filetime=end,join=0,exit=0))
        r['idle_branch_passed'] &= h['passed']
    except (AssertionError,IndexError,ValueError,TypeError,UnicodeError) as exc:
        r['refusal']=type(exc).__name__
    return r
