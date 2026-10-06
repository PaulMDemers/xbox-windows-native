"""Preserve the current physical SetupAPI log for later shutdown-popup diagnosis."""
from physical import k,connect,owner,get,sha,save,utc,startup,baseline
p=k/'artifacts/diagnostics/setupapi.log';record=k/'setupapi-capture.json'
assert not record.exists()
with connect() as f:
    owner(f);assert sha(get(f,startup))==baseline['startup_sha256']
    data=get(f,'/F/winnt/setupapi.log')
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    save(dict(scope=__doc__,captured_utc=utc(),bytes=len(data),sha256=sha(data),console_path='/F/winnt/setupapi.log',limits='Whole post-run log; no pre-run SetupAPI capture exists for this attempt. Does not identify the popup process or its cause.'),record)
print('SetupAPI log preserved read-only:',len(data),'bytes')
