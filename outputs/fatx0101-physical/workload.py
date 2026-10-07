"""Verify the exact five-worker protocol; malformed, held or partial logs fail."""
def verify_log(log):
    rows={}
    try:
        for line in log.splitlines():
            fields=line.split()
            if not fields:continue
            if len(fields)!=4 or fields[0] in rows:return False,None
            rows[fields[0]]=list(map(int,fields[1:]))
    except ValueError:return False,None
    wait=rows.get('WAIT_RESULT',[])
    expected={'ATTEMPT_ONCE':[5,500,4097],'COUNTS':[500,500,500],
              'ERRORS':[0,0,0],'NAMESPACE_COUNTS':[500,500,0],
              'NAMESPACE_ERRORS':[0,0,0],'COMPLETE':[500,500,500],
              'NORMAL_RESTART_REQUEST':[0,0,0]}
    valid=set(rows)==set(expected)|{'WAIT_RESULT'} and all(rows.get(n)==v for n,v in expected.items())
    valid=bool(valid and len(wait)==3 and 0<=wait[0]<5 and 0<=wait[1]<600000 and wait[2]==0)
    return valid,wait[1] if len(wait)==3 else None
