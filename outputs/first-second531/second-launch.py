"""One explicitly planned second request; never erase first-run receipts."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
FIRST=W/'outputs/visible-dispatch528'
sys.dont_write_bytecode=True
sys.path.insert(0,str(FIRST))
spec=importlib.util.spec_from_file_location('first528',FIRST/'physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def admit(stage,collection,closure,observation):
    assert stage['completed'] and collection['completed'] and closure['closed']
    assert not stage['temporary_startup_added'] and not collection['temporary_hook_installed']
    assert collection['remote_writes']==[] and collection['protected_code_exact']
    assert closure['physical_launches']==1 and closure['no_next_launch_queued']
    assert observation['user_report_received'] and observation['at_dashboard']
    assert observation['manual_reset_between_launches'] is False
    assert stage['remote']==m.REMOTE
    required={m.REMOTE+'/owner.json',m.REMOTE+'/default.xbe'}
    assert set(stage['staged'])==required
    for n in required:
        assert collection['files'][n]['sha256']==stage['staged'][n]['sha256']
    assert set(collection['files'])==set([m.NORMAL,m.TARGET]+m.MUTABLE+list(required)+[m.REMOTE+'/'+n for n in m.RECEIPTS])
    return {n:row for n,row in collection['files'].items() if row is not None}


def request_once(f,out,record):
    assert not out.exists(),'second ordinal already consumed'
    record.update(utc=m.utc(),requested=True,
                  command=r'SITE EXEC E:\Applications\XWNDispatch528\default.xbe',
                  ordinal=2,automatic_retry_allowed=False,remote_writes=[])
    # Exclusive creation persists intent before the one remote request.
    with out.open('x',encoding='utf-8') as stream:
        json.dump(record,stream,indent=2);stream.write('\n')
    f.sock.settimeout(20)
    try:record['reply']=f.sendcmd(record['command'])
    except Exception as exc:record['reply_uncertain']=type(exc).__name__
    m.write_json(out,record)
    return record


def main():
    out=K/'second-launch.json';assert not out.exists()
    assert read(K/'second-host001.json')['passed']
    assert read(K/'second-host001.json')['source_sha256']==sha(Path(__file__))
    m.verify()
    paths=[FIRST/'physical001-stage.json',FIRST/'physical001-collection.json',
           FIRST/'physical-final001.json',K/'first-observation.json']
    s,c,z,o=[read(p) for p in paths]
    expected=admit(s,c,z,o)
    pins={str(p):sha(p) for p in paths+[Path(__file__),FIRST/'package001.json',K/'second-host001.json']}
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==s['startup_listing']
        actual=m.listing(f)
        assert set(actual)=={n.rsplit('/',1)[1] for n in expected if n.startswith(m.REMOTE+'/')}
        for n,row in expected.items():
            data=m.get(f,n)
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],n
        record=dict(source_pins=pins,first_collection_sha256=sha(paths[1]),
                    receipt_reset_performed=False,executable_unchanged=True,
                    launch_path_and_method_unchanged=True,manual_reset_between_launches=False,
                    existing_receipts_cannot_prove_second_execution=True,
                    console_C_accessed=False,windows_boot_intended=False)
        result=request_once(f,out,record)
    print(json.dumps(result))


if __name__=='__main__':
    main()
