"""Verify the exact five-worker protocol; malformed, held or partial logs fail."""
def parse_log(log):
    rows={}
    try:
        for line in log.splitlines():
            fields=line.split()
            if not fields:continue
            if len(fields)!=4 or fields[0] in rows:return None
            rows[fields[0]]=list(map(int,fields[1:]))
    except ValueError:return None
    return rows
def verify_log(log):
    rows=parse_log(log)
    if rows is None:return False,None
    wait=rows.get('WAIT_RESULT',[])
    expected={'ATTEMPT_ONCE':[5,500,4097],'COUNTS':[500,500,500],
              'ERRORS':[0,0,0],'NAMESPACE_COUNTS':[500,500,0],
              'NAMESPACE_ERRORS':[0,0,0],'COMPLETE':[500,500,500],
              'NORMAL_RESTART_REQUEST':[0,0,0]}
    valid=set(rows)==set(expected)|{'WAIT_RESULT'} and all(rows.get(n)==v for n,v in expected.items())
    valid=bool(valid and len(wait)==3 and 0<=wait[0]<5 and 0<=wait[1]<600000 and wait[2]==0)
    return valid,wait[1] if len(wait)==3 else None

def describe_log(log):
    """Separate completed workers from restart protocol; never changes PASS gates."""
    rows=parse_log(log)
    if rows is None:return dict(well_formed=False,workers_completed=False)
    wait=rows.get('WAIT_RESULT',[])
    required={'ATTEMPT_ONCE':[5,500,4097],'COUNTS':[500,500,500],
              'ERRORS':[0,0,0],'NAMESPACE_COUNTS':[500,500,0],
              'NAMESPACE_ERRORS':[0,0,0],'COMPLETE':[500,500,500]}
    workers=bool(all(rows.get(n)==v for n,v in required.items()) and len(wait)==3 and 0<=wait[0]<5 and 0<=wait[1]<600000 and wait[2]==0)
    return dict(well_formed=True,workers_completed=workers,
                pending_install_hold=rows.get('RESTART_BLOCKED_PENDING_INSTALL'),
                normal_restart_requested=rows.get('NORMAL_RESTART_REQUEST')==[0,0,0],
                protocol_passed=verify_log(log)[0])
