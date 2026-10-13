"""Read-only completion gate joining the preserved failed stage and continuation."""
import json
from pathlib import Path
from engine import digest, LAUNCHER

def staged():
    k=Path(__file__).resolve().parent;w=k.parents[1]
    read=lambda p:json.loads(p.read_text())
    r=read(k/'resume002.json');old=k/'physical001.json';package=k.parent/'stock-physical337/package001.json'
    assert r['complete'] and not r.get('quarantined',False)
    assert r['original_receipt_sha256']==digest(old.read_bytes())
    assert r['package_sha256']==digest(package.read_bytes())
    assert r['readback_verified'] and r['launcher_written_last'] and r['overwritten_files']==0
    assert r['normal_startup'] and not r['launch_sent'] and not r['console_c_accessed'] and not r['console_f_written']
    assert all(r['baseline_before'].values()) and all(r['baseline_after'].values())
    for p,h in r['source_pins'].items():assert digest((w/p).read_bytes())==h,p
    private=Path('E:/xwn340/resume002')
    j=(private/'journal.jsonl').read_bytes();assert digest(j)==r['journal_sha256']
    assert digest((private/'original-journal.jsonl').read_bytes())==r['original_journal_sha256']==read(old)['journal_sha256']
    rows=[json.loads(x) for x in j.splitlines()];files=read(package)['files'];seen=set();pending=None;writing=False;existing=0;created=0
    for row in rows:
        p=row['path'];assert p in files and row['meta']==files[p]
        if row['kind']=='existing_verified':
            assert not writing and pending is None and p not in seen and p!=LAUNCHER
            seen.add(p);existing+=1
        elif row['kind']=='write_intent':
            assert pending is None and p not in seen;pending=p;writing=True
        elif row['kind']=='write_verified':
            assert pending==p and p not in seen;pending=None;seen.add(p);created+=1
        else:raise AssertionError('Unknown continuation event')
    assert seen==set(files) and pending is None and rows[-1]['path']==LAUNCHER and rows[-1]['kind']=='write_verified'
    assert existing==r['existing_files']==r['existing_verified']
    assert created==r['created_files']==r['new_verified']
    assert existing+created==r['files']==len(files)
    return r
