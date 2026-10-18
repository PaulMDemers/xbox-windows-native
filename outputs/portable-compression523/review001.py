# SPDX-License-Identifier: MIT
"""Independent raw Win32 allocation and standard-library hash readback."""
import ctypes,datetime,hashlib,json,shutil,stat,traceback
from ctypes import wintypes
from pathlib import Path
from common002 import processes
K=Path(__file__).resolve().parent;OUT=K/'review001.json';assert not OUT.exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
js=lambda p:json.loads(p.read_bytes())
class Info(ctypes.Structure):
    _fields_=[('allocation',ctypes.c_longlong),('size',ctypes.c_longlong),('links',wintypes.DWORD),('pending',wintypes.BOOLEAN),('directory',wintypes.BOOLEAN)]
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE];k.CreateFileW.restype=wintypes.HANDLE
k.GetFileInformationByHandleEx.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD];k.GetFileInformationByHandleEx.restype=wintypes.BOOL
k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
r=dict(passed=False,physical_access=False,files=[],inputs={})
try:
    plan=js(K/'plan002.json');a=js(K/'apply001.json');assert plan['passed'] and a['passed'] and a['attempted'] and a['tool_exit_code']==0
    assert a['plan_sha256']==sha(K/'plan002.json') and a['source_sha256']==sha(K/'apply001.py')
    assert not js(K/'plan001.json')['passed']
    assert (K/'common002.py').read_bytes()==(K/'common.py').read_bytes().replace(b'    return h\n',b'    return h.hexdigest()\n')
    for name,h in {**plan['records'],**plan['sources']}.items():assert sha(Path(name))==h;r['inputs'][name]=h
    assert len(plan['files'])==len(a['after'])==7
    after={v['path']:v for v in a['after']};saved=0;identities=set()
    for row in plan['files']:
        p=Path(row['path']);case=row['case'];expected=Path(f'C:/xwn{case}/instances/windows-native-entry{case}-emu001/EA3473314E6C0EA0/xemu-windows-native-entry{case}-emu001.exe')
        assert p.resolve(strict=True)==expected.absolute()
        for component in (p,*p.parents):assert not component.lstat().st_file_attributes&0x400
        s=p.stat();old=row['metadata'];post=after[str(p)];assert post['verified']
        assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_file_attributes&0x800 and not s.st_file_attributes&(0x400|0x4000|0x200)
        h=k.CreateFileW(str(p),0x80000000,7,None,3,0,None);assert h!=ctypes.c_void_p(-1).value
        try:
            info=Info();assert k.GetFileInformationByHandleEx(h,1,ctypes.byref(info),ctypes.sizeof(info))
        finally:assert k.CloseHandle(h)
        assert not info.pending and not info.directory and info.links==1 and info.size==s.st_size==old['bytes']==191317057
        digest=sha(p);assert digest==old['sha256']==row['recorded_original_sha256']==post['metadata']['sha256']
        assert s.st_ino==old['file_id']==post['metadata']['file_id'] and s.st_dev==old['device']==post['metadata']['device']
        assert info.allocation==post['metadata']['allocated_bytes'] and 0<info.allocation<old['allocated_bytes']
        assert s.st_file_attributes==post['metadata']['attributes']
        identities.add((s.st_dev,s.st_ino));saved+=old['allocated_bytes']-info.allocation
        r['files'].append(dict(path=str(p),case=case,bytes=s.st_size,sha256=digest,file_id=s.st_ino,device=s.st_dev,links=s.st_nlink,attributes=s.st_file_attributes,allocated_before=old['allocated_bytes'],allocated_after=info.allocation))
    assert len(identities)==7 and saved==a['allocated_bytes_recovered']
    r['processes']=processes();r['free_bytes']={d:shutil.disk_usage(d+':/').free for d in ('C','E')}
    r['minimum_bytes']=20*1024**3;r['projected_bytes']=768*1024**2
    margin=r['free_bytes']['C']-r['minimum_bytes']-r['projected_bytes']
    r.update(passed=True,allocated_bytes_recovered=saved,projected_guard_passed=margin>=0,additional_headroom_bytes=margin,operational_512MiB_target_passed=margin>=512*1024**2,all_original_content_and_identity_exact=True,all_owned_storage_subprocesses_closed=True)
    for p in sorted(K.iterdir()):
        if p.is_file() and p.name!='review001.json':r['inputs'][str(p.resolve())]=sha(p)
except Exception:r['failure']=traceback.format_exc()
r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','allocated_bytes_recovered','free_bytes','additional_headroom_bytes','operational_512MiB_target_passed'] if n in r}))
if not r['passed']:raise SystemExit(1)
