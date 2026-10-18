# SPDX-License-Identifier: MIT
"""Exact closed-file selection and Windows allocation inspection."""
import ctypes,hashlib,json,os,stat,subprocess
from ctypes import wintypes
from pathlib import Path
K=Path(__file__).resolve().parent
CASES={502:'entry-kernel502',505:'entry-runtime505',507:'entry-return507',511:'entry-runtime511',512:'entry-loaded512',513:'entry-contract513',517:'entry-observer517'}
MINIMUM=20*1024**3;PROJECTED=768*1024**2
COMPACT=Path(os.environ['SystemRoot'])/'System32/compact.exe'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
js=lambda p:json.loads(p.read_bytes())
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.GetCompressedFileSizeW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)];kernel.GetCompressedFileSizeW.restype=wintypes.DWORD
kernel.GetVolumeInformationW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD),ctypes.POINTER(wintypes.DWORD),ctypes.POINTER(wintypes.DWORD),wintypes.LPWSTR,wintypes.DWORD];kernel.GetVolumeInformationW.restype=wintypes.BOOL

def volume():
    serial=wintypes.DWORD();maxcomponent=wintypes.DWORD();flags=wintypes.DWORD();fs=ctypes.create_unicode_buffer(32)
    if not kernel.GetVolumeInformationW('C:\\',None,0,ctypes.byref(serial),ctypes.byref(maxcomponent),ctypes.byref(flags),fs,len(fs)):raise ctypes.WinError(ctypes.get_last_error())
    assert fs.value=='NTFS' and flags.value&0x10
    return dict(filesystem=fs.value,serial=serial.value,flags=flags.value,compression_supported=True)

def allocated(p):
    high=wintypes.DWORD();ctypes.set_last_error(0);low=kernel.GetCompressedFileSizeW(str(p),ctypes.byref(high))
    if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
    return (high.value<<32)|low

class Standard(ctypes.Structure):
    _fields_=[('allocation',ctypes.c_longlong),('end',ctypes.c_longlong),('links',wintypes.DWORD),('delete_pending',wintypes.BOOLEAN),('directory',wintypes.BOOLEAN)]
kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE];kernel.CreateFileW.restype=wintypes.HANDLE
kernel.GetFileInformationByHandleEx.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD];kernel.GetFileInformationByHandleEx.restype=wintypes.BOOL
kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL

def metadata(p):
    s=p.stat();h=kernel.CreateFileW(str(p),0x80000000,7,None,3,0,None)
    if h==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    try:
        info=Standard()
        if not kernel.GetFileInformationByHandleEx(h,1,ctypes.byref(info),ctypes.sizeof(info)):raise ctypes.WinError(ctypes.get_last_error())
        assert info.end==s.st_size and info.links==s.st_nlink and not info.directory and not info.delete_pending
    finally:assert kernel.CloseHandle(h)
    return dict(bytes=s.st_size,allocated_bytes=info.allocation,compressed_size_api=allocated(p),attributes=s.st_file_attributes,links=s.st_nlink,file_id=s.st_ino,device=s.st_dev,sha256=sha(p))

def validate_path(p,case):
    assert case in CASES
    expected=Path(f'C:/xwn{case}/instances/windows-native-entry{case}-emu001/EA3473314E6C0EA0/xemu-windows-native-entry{case}-emu001.exe')
    assert p.absolute()==expected.absolute() and p.resolve(strict=True)==expected.absolute()
    for component in [p,*p.parents]:assert not component.lstat().st_file_attributes&0x400,str(component)
    s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not s.st_file_attributes&(0x4000|0x200|0x400)
    return p

def processes():
    command='Get-CimInstance Win32_Process | Where-Object {$_.Name -match "^(xemu|qemu)"} | Select-Object ProcessId,Name | ConvertTo-Json -Compress'
    live=subprocess.check_output(['pwsh','-NoProfile','-Command',command],text=True,timeout=20).strip();assert not live,live
    q=subprocess.run(['wsl','-d','Ubuntu','--','ps','-eo','pid=,comm='],capture_output=True,text=True,timeout=20);assert q.returncode==0 and not q.stderr.strip()
    rows=[line.split(None,1) for line in q.stdout.splitlines() if line.strip()];assert all(len(r)==2 and not r[1].startswith(('qemu','xemu')) for r in rows)
    return dict(windows_matches=[],wsl_inventory=rows,wsl_matches=[])

def selection():
    rows=[];records={}
    for case,folder in CASES.items():
        fp=K.parent/folder/'final-review.json';run=Path(f'C:/xwn{case}/runs/nt5-entry{case}-emu001')
        paths=[fp,run/'instance.json',run/'host-exit.json',run/'cleanup.json'];f,i,e,c=[js(p) for p in paths]
        for p in paths:records[str(p.resolve())]=sha(p)
        assert f['all_owned_processes_closed'] and (f.get('passed') or f.get('closeout_passed'))
        assert e['closed'] and e['exit_code']==0 and not e['fallback_kill'] and not e['timeout']
        assert c['completedUtc'] and not c['retained']
        p=validate_path(Path(i['executable']),case);m=metadata(p)
        assert m['sha256']==i['sourceSha256'].lower()==f['private_files'][str(p)]=='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
        assert m['bytes']==191317057
        rows.append(dict(case=case,path=str(p),metadata=m,recorded_original_sha256=f['private_files'][str(p)]))
    assert len(rows)==7 and len({r['path'].casefold() for r in rows})==7
    return rows,records
