"""Independent activation evidence, separate from unchanged201 Cancel/idle decoder."""
def analyze(blob):
    assert isinstance(blob,bytes) and 0<len(blob)<=1048576 and blob.endswith(b'\r\n')
    rows=[]
    for line in blob.decode('ascii').splitlines():
        p=line.split();assert len(p)==4
        v=list(map(int,p[1:]));assert all(0<=n<=0xffffffff for n in v)
        assert not p[0].startswith('FAIL_') and p[0]!='TIMEOUT201'
        rows.append((p[0],v))
    owners=[];attempts=[];at=0
    while at<len(rows):
        label,v=rows[at]
        if label!='ACTIVATE_OWNER313':at+=1;continue
        assert v[0] and (v[1] or v[2]) and v not in owners and len(owners)<8
        owners.append(v);pid=v[0]
        labels=['ACTIVATE_OWNER313','ACTIVATE_INTENT313','FG_ACTIVATE_BEFORE313','GUI_ACTIVATE_BEFORE313_OWNER','GUI_ACTIVATE_BEFORE313_ACTIVE','GUI_ACTIVATE_BEFORE313_CAPTURE','ACTIVATE_RESULT313','FG_ACTIVATE_AFTER313','GUI_ACTIVATE_AFTER313_OWNER','GUI_ACTIVATE_AFTER313_ACTIVE','GUI_ACTIVATE_AFTER313_CAPTURE']
        part=rows[at:at+len(labels)];assert [a for a,b in part]==labels
        d={a:b for a,b in part};intent=d['ACTIVATE_INTENT313'];h=intent[1]
        assert intent==[pid,h,len(owners)] and h
        before=d['FG_ACTIVATE_BEFORE313'];after=d['FG_ACTIVATE_AFTER313']
        assert all(before) and before[1]!=h
        own=d['GUI_ACTIVATE_BEFORE313_OWNER'];assert own[0]==pid and own[1] and own[2]==0
        assert d['GUI_ACTIVATE_AFTER313_OWNER']==own
        for phase in ['BEFORE','AFTER']:
            g=d['GUI_ACTIVATE_'+phase+'313_ACTIVE'];assert g[0]&~1==0 and g[1]==h
            assert d['GUI_ACTIVATE_'+phase+'313_CAPTURE']==[0,0,0]
        result=d['ACTIVATE_RESULT313'];assert result[:2]==[pid,h] and result[2] in [0,1]
        # A return value alone is not coverage; require actual foreground owner and subsequent verified Cancel.
        succeeded=after==[pid,h,own[1]]
        tail=rows[at+len(labels):]
        cancels=[(i,x) for i,(tag,x) in enumerate(tail) if tag=='CANCEL_ACTIVE_VERIFIED' and x[:2]==[pid,h]]
        if succeeded:
            assert len(cancels)==1 and cancels[0][1][2]==own[1]
            assert ('CANCEL_CLOSED_OWNER',v) in tail and ('CANCEL_WINDOW_CLOSED',[pid,h,0]) in tail
        attempts.append(dict(owner=v,hwnd=h,api_return=result[2],actual_foreground=succeeded,cancel_verified=succeeded))
        at+=len(labels)
    assert attempts,'No actual activation coverage'
    assert rows[-1][0]=='IDLE201' and rows[-1][1][0]>=5000
    assert all(v['actual_foreground'] and v['cancel_verified'] for v in attempts)
    return dict(passed=True,attempts=attempts,limits='Actual normal activation/Cancel closure only; original setup/idle decoder remains independently required.')

if __name__=='__main__':
    import json,sys
    from pathlib import Path
    p=Path(sys.argv[1]);dest=Path(sys.argv[2]);assert not dest.exists()
    result=analyze(p.read_bytes());dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
