"""Exercise real Windows reader sharing: retry succeeds without partial JSON."""
import ctypes,hashlib,json,tempfile,threading,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
create=kernel.CreateFileW
create.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
create.restype=ctypes.c_void_p
close=kernel.CloseHandle;close.argtypes=[ctypes.c_void_p];close.restype=ctypes.c_int
with tempfile.TemporaryDirectory(prefix='xwn-json-sharing-') as directory:
    p=Path(directory)/'trace.json';write_json(p,dict(version=1))
    # Reader intentionally withholds FILE_SHARE_DELETE, like an ordinary open.
    handle=create(str(p),0x80000000,1,None,3,0,None)
    assert handle!=ctypes.c_void_p(-1).value
    def release():
        time.sleep(.2);assert close(handle)
    worker=threading.Thread(target=release);worker.start();start=time.monotonic()
    write_json(p,dict(version=2,payload='verified'))
    elapsed=time.monotonic()-start;worker.join()
    assert elapsed>=.15 and json.loads(p.read_text())==dict(version=2,payload='verified')
    assert not p.with_suffix('.tmp').exists()
    # A permanent reader block must preserve the old JSON and complete new tmp.
    handle=create(str(p),0x80000000,1,None,3,0,None)
    assert handle!=ctypes.c_void_p(-1).value
    try:
        try:write_json(p,dict(version=3),timeout=.05)
        except PermissionError:pass
        else:raise AssertionError('Expected bounded failure with locked reader')
        assert json.loads(p.read_text())['version']==2
        assert json.loads(p.with_suffix('.tmp').read_text())==dict(version=3)
    finally:assert close(handle)
report=dict(real_windows_sharing_retry_passed=True,permanent_block_preserves_both_records=True,elapsed_seconds=elapsed,source_sha256=hashlib.sha256((k/'atomic_json.py').read_bytes()).hexdigest())
dest=k/'atomic-json-test.json';assert not dest.exists();dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
