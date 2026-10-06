"""Pure verification shared by cold-emulator and physical collection audits."""
import hashlib
SIZES=[1,2,511,512,513,4095,4096,4097,8191,8192,8193,65535,65536,65537,131071,131072,131073]
NAMES=[f'{kind}{i:02}.bin' for kind in ['input','output'] for i in range(17)]+[f'match{i:02}.bmp' for i in range(16)]+['matched.log','result.log']
ABSENT=[f'{kind}{i:02}.bin' for kind in ['copy','moved'] for i in range(17)]
def verify(read,scribble,interval):
    rows=[]
    for kind,round in [('input',0),('output',15)]:
        for i,size in enumerate(SIZES):
            name=f'{kind}{i:02}.bin';data=read(name)
            rows.append(dict(name=name,matched=data==bytes((v*13+i*17+round*29)&255 for v in range(size)),bytes=len(data or b''),sha256=hashlib.sha256(data or b'').hexdigest()))
    for i in range(16):
        name=f'match{i:02}.bmp';data=read(name)
        rows.append(dict(name=name,matched=data==scribble,bytes=len(data or b''),sha256=hashlib.sha256(data or b'').hexdigest()))
    absent={name:read(name) is None for name in ABSENT}
    log=(read('result.log') or b'').decode('ascii');lines=[v.split() for v in log.splitlines()]
    checks=[v for v in lines if v[0] in ['INPUT','OUTPUT','COPY']]
    sequence=[('INPUT',str(i)) for i in range(17)]+[(kind,str(i)) for _ in range(15) for i in range(17) for kind in ['OUTPUT','COPY']]
    timing=[list(map(int,v[1:])) for v in lines if v[0]=='ROUND_ELAPSED_MS']
    timed=len(timing)==15 and all(v[0]==i+1 and v[1]>=(i+1)*interval and v[2]==0 for i,v in enumerate(timing))
    matched=(read('matched.log') or b'').decode('ascii');mlines=[v.split() for v in matched.splitlines()]
    cases=[v for v in mlines if v[0]=='CASE_PASS']
    replay=len(cases)==16 and [int(v[1]) for v in cases]==list(range(16)) and all(int(v[3])==len(scribble) for v in cases) and any(v[0]=='PASS' and v[1]=='16' for v in mlines) and 'FAIL_' not in matched
    passed=(len(checks)==527 and [(v[0],v[1]) for v in checks]==sequence and all(v[2:]==['0','0'] for v in checks) and log.startswith('ATTEMPT_ONCE 17 15 997\r\nINTERVAL_MS '+str(interval)+' 0 0\r\n') and log.endswith('COMPLETE 0 17 15\r\nNORMAL_RESTART_REQUEST 0 0 0\r\n') and 'MATCHED_EXIT_ZERO 0 0 0\r\n' in log and 'FAIL_' not in log and timed and replay and all(v['matched'] for v in rows) and all(absent.values()))
    return dict(passed=passed,mapping_checks=len(checks),files=rows,deleted_files_absent=absent,timed_rounds=timing,required_duration_ms=15*interval,paint_api_replay_passed=replay,actual_paint_ui_tested=False,log=log,matched_log=matched)
