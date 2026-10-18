# SPDX-License-Identifier: MIT
"""Exact closed-file selection and Windows allocation inspection."""
import ctypes,hashlib,json,os,stat,subprocess
from ctypes import wintypes
from pathlib import Path
K=Path(__file__).resolve().parent
CASES={501:'entry-scene501',508:'entry-physical508',514:'entry-physical514',518:'entry-physical518'}
NAMES=('system','software','sam','security','default','sysevent.evt','appevent.evt')
MINIMUM=20*1024**3;PROJECTED=768*1024**2
COMPACT=Path(os.environ['SystemRoot'])/'System32/compact.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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

def metadata(p):
    s=p.stat();return dict(bytes=s.st_size,allocated_bytes=allocated(p),attributes=s.st_file_attributes,links=s.st_nlink,file_id=s.st_ino,device=s.st_dev,sha256=sha(p))

def validate_path(p,case,phase,name):
    root=Path(f'C:/xwn{case}/physical001');expected=root/phase/'E/winnt/system32/config'/name
    assert case in CASES and phase in ('before','after') and name in NAMES
    assert p.absolute()==expected.absolute() and p.resolve(strict=True)==expected.absolute()
    assert p.resolve(strict=True).is_relative_to(root.resolve(strict=True))
    for component in [p,*p.parents]:assert not component.lstat().st_file_attributes&0x400,str(component)
    s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not s.st_file_attributes&(0x4000|0x200|0x400)
    return p

def processes():
    command='Get-CimInstance Win32_Process | Where-Object { $_.Name -match "^(xemu|qemu)" -or $_.CommandLine -match "(?i)(C:[\\/]+|/mnt/c/)xwn(501|508|514|518)[\\/]" } | Select-Object ProcessId,Name | ConvertTo-Json -Compress'
    live=subprocess.check_output(['pwsh','-NoProfile','-Command',command],text=True,timeout=20).strip();assert not live,live
    q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-af','(^|/)(qemu-system[^ ]*|xwn(501|508|514|518)/)'],capture_output=True,text=True,timeout=20)
    assert q.returncode==1 and not q.stdout.strip(),q.stdout
    return dict(windows_matches=[],wsl_matches=[])

def selection():
    rows=[];records={}
    for case,folder in CASES.items():
        k=K.parent/folder;data={}
        for name in ['physical001-stage.json','physical001-collection.json','physical-final001.json','final-review.json']:
            p=k/name;data[name]=js(p);records[str(p.resolve())]=sha(p)
        s=data['physical001-stage.json'];c=data['physical001-collection.json'];f=data['physical-final001.json'];r=data['final-review.json']
        assert s['completed'] and c['completed'] and f['closed'] and r['review_passed'] and r['all_owned_processes_closed']
        for phase,mapping in [('before',s['before']),('after',c['files'])]:
            for name in NAMES:
                remote='/E/winnt/system32/config/'+name;row=mapping[remote];p=validate_path(Path(row['path']),case,phase,name)
                value=metadata(p);assert value['bytes']==row['bytes'] and value['sha256']==row['sha256']
                rows.append(dict(path=str(p),case=case,phase=phase,name=name,original=row,metadata=value))
    assert len(rows)==56 and len({r['path'].lower() for r in rows})==56
    return rows,records
