"""Preserve all prior owned test files locally and rename their console directory."""
import json
from physical import k,connect,owner,get,save,sha,utc,missing,startup,baseline
source='/F/xwns98';destination='/F/xwns98-second';record=k/'archive-previous.json'
assert not record.exists(),'Inspect recorded state; never repeat an uncertain rename'
old=k.parent/'fatx0098-soak2';trial=json.loads((old/'physical.json').read_text())
assert trial['collected_utc'] and not trial['startup_enabled']
def listing(f,path):
    f.cwd(path);assert f.pwd().rstrip('/').lower()==path.lower()
    lines=[];f.retrlines('LIST',lines.append);rows=[]
    for line in lines:
        p=line.split(None,8);assert len(p)==9
        if p[8] in ['.','..']:continue
        assert p[0][0]=='-' and not any(c in p[8] for c in '/\\:'),line
        rows.append((p[8],int(p[4])))
    return sorted(rows)
with connect() as f:
    owner(f);assert sha(get(f,startup))==baseline['startup_sha256'];missing(f,destination)
    rows=listing(f,source);assert rows
    r=dict(scope=__doc__,started_utc=utc(),source=source,destination=destination,files=[],rename_attempted=False,verified_after_rename=False)
    local=k/'artifacts/previous-folder';local.mkdir(parents=True,exist_ok=True)
    for name,size in rows:
        data=get(f,source+'/'+name);assert len(data)==size
        prior=trial['collected'].get(name)
        if prior:assert sha(data)==prior['sha256'],name
        path=local/name
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
        r['files'].append(dict(name=name,bytes=len(data),sha256=sha(data)))
    expected={v['path'].rsplit('/',1)[1]:v['sha256'] for v in trial['payloads']}
    assert {v['name']:v['sha256'] for v in r['files']}==expected
    assert listing(f,source)==rows
    r.update(rename_attempted=True,rename_requested_utc=utc());save(r,record)
    f.cwd('/F');r['reply']=f.rename(source,destination);save(r,record)
    missing(f,source);assert listing(f,destination)==rows
    for row in r['files']:assert sha(get(f,destination+'/'+row['name']))==row['sha256']
    r.update(verified_after_rename=True,verified_utc=utc());save(r,record)
    print('Archived and readback verified',len(rows),'previous files; no Windows launch')
