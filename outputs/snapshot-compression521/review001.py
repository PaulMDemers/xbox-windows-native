# SPDX-License-Identifier: MIT
"""Independent byte, identity, allocation and historical-record closeout."""
import ctypes,datetime,hashlib,json,shutil,stat,traceback
from ctypes import wintypes
from pathlib import Path
from common003 import processes
K=Path(__file__).resolve().parent;OUT=K/'review001.json';assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
k32=ctypes.WinDLL('kernel32',use_last_error=True)
k32.GetCompressedFileSizeW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
k32.GetCompressedFileSizeW.restype=wintypes.DWORD
r=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=[],batches=[],physical_access=False)
try:
    seen=set();records={}
    for n,total in [(1,56),(2,48),(3,132)]:
        pp=K/f'plan{n:03}.json';ap=K/f'apply{n:03}.json';plan=read(pp);a=read(ap)
        assert plan['passed'] and a['plan_sha256']==sha(pp)
        assert a['source_sha256']==sha(K/f'apply{n:03}.py')
        assert a['attempted'] and a['tool_completed'] and a['tool_exit_code']==0 and 'failure' not in a
        assert a['passed']==(n!=1)
        assert a['deleted_files']==a['moved_files']==a['modified_content_files']==[]
        for name,h in {**plan['sources'],**plan['records']}.items():
            assert sha(Path(name))==h,name;records[name]=h
        assert len(plan['files'])==len(a['after'])==total
        after={v['path']:v for v in a['after']};assert len(after)==total
        saved=0;compressed=0;skipped=[]
        for row in plan['files']:
            p=Path(row['path']);original=row['metadata'];post=after[row['path']]
            key=str(p.resolve(strict=True)).casefold();assert key not in seen;seen.add(key)
            expected=Path(f"C:/xwn{row['case']}/physical001")/row['phase']/'E/winnt/system32/config'/row['name']
            assert row['phase'] in ('before','after') and row['name'] in ('system','software','sam','security','default','sysevent.evt','appevent.evt')
            assert p.resolve(strict=True)==expected.absolute()
            for c in (p,*p.parents):assert not c.lstat().st_file_attributes&0x400
            s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
            assert not s.st_file_attributes&(0x400|0x4000|0x200)
            high=wintypes.DWORD();ctypes.set_last_error(0);low=k32.GetCompressedFileSizeW(str(p),ctypes.byref(high))
            assert low!=0xffffffff or ctypes.get_last_error()==0
            now=dict(bytes=s.st_size,allocated_bytes=(high.value<<32)|low,attributes=s.st_file_attributes,links=s.st_nlink,file_id=s.st_ino,device=s.st_dev,sha256=sha(p))
            assert now==post['metadata']
            for field in ('bytes','sha256','links','file_id','device'):assert now[field]==original[field],(str(p),field)
            assert now['sha256']==row['original']['sha256'] and now['bytes']==row['original']['bytes']
            is_compressed=bool(now['attributes']&0x800)
            if n==1 and row['name']=='system':
                assert not is_compressed and not post['verified'] and now==original
                assert 'AssertionError' in post['failure'];skipped.append(str(p))
            else:assert is_compressed and post['verified']
            compressed+=int(is_compressed);saved+=original['allocated_bytes']-now['allocated_bytes']
            r['files'].append(dict(path=str(p),original=original,current=now,content_and_identity_exact=True))
        assert len(skipped)==(8 if n==1 else 0)
        if n!=1:assert saved==a['allocated_bytes_recovered']
        r['batches'].append(dict(id=n,files=total,compressed=compressed,uncompressed_skipped=skipped,allocated_bytes_recovered=saved,original_application_passed=a['passed']))
    assert len(seen)==236
    r['processes']=processes();r['free_bytes']={d:shutil.disk_usage(d+':/').free for d in ('C','E')}
    r['projected_bytes']=768*1024**2;r['minimum_bytes']=20*1024**3
    r['projected_guard_passed']=r['free_bytes']['C']-r['projected_bytes']>=r['minimum_bytes']
    r['allocated_bytes_recovered']=sum(x['allocated_bytes_recovered'] for x in r['batches'])
    r['compressed_files']=sum(x['compressed'] for x in r['batches'])
    r['frozen_records']=records
    r['inputs']={str(p.resolve()):sha(p) for p in sorted(K.iterdir()) if p.is_file() and p.name not in ('review001.json','final-review.json','REPORT.md','NEXT.md','sessions.json')}
    r.update(passed=True,all_selected_content_and_identity_exact=True,all_owned_storage_subprocesses_closed=True,application001_partial_failure_preserved=True)
except Exception:r['failure']=traceback.format_exc()
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode())
    print(json.dumps({k:r[k] for k in ('passed','failure','allocated_bytes_recovered','compressed_files','projected_guard_passed','free_bytes') if k in r}))
if not r['passed']:raise SystemExit(1)
