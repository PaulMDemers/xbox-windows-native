"""Exercise actual Windows sharing failures and publication without console access."""
import ctypes
import json
import os
from pathlib import Path
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import hd_overlay as h

assert os.name == 'nt'
out = Path('D:/xwn326/sharing001')
out.mkdir(parents=True, exist_ok=False)
report = Path(__file__).with_name('sharing001.json')
assert not report.exists()
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
kernel.CreateFileW.restype = ctypes.c_void_p
kernel.CloseHandle.argtypes = [ctypes.c_void_p]
kernel.CloseHandle.restype = ctypes.c_int


def hold(path):
    handle = kernel.CreateFileW(str(path), 0x80000000, 0, None, 3, 0, None)
    assert handle not in (None, ctypes.c_void_p(-1).value), ctypes.get_last_error()
    return handle


results = []
for transient in (True, False):
    path = out / ('transient.json' if transient else 'permanent.json')
    h.save(path, {'generation': 1})
    original = path.read_bytes()
    handle = hold(path)
    thread = None
    if transient:
        def release():
            time.sleep(.2)
            assert kernel.CloseHandle(handle)
        thread = threading.Thread(target=release)
        thread.start()
    started = time.monotonic()
    try:
        try:
            h.save(path, {'generation': 2})
        except PermissionError:
            assert not transient
            outcome = 'bounded_refusal'
        else:
            assert transient
            outcome = 'published_after_release'
    finally:
        if thread:
            thread.join(timeout=3)
            assert not thread.is_alive()
        else:
            assert kernel.CloseHandle(handle)
    elapsed = time.monotonic() - started
    assert elapsed < 6
    if transient:
        assert h.load(path) == {'generation': 2}
    else:
        assert path.read_bytes() == original
        assert path.with_suffix('.tmp').exists()
        assert h.load(path.with_suffix('.tmp')) == {'generation': 2}
    results.append({'case': path.stem, 'result': outcome, 'elapsed_seconds': elapsed})
h.save(report, {'passed': True, 'cases': results, 'actual_windows_handles': True,
                'physical_access': False, 'source_sha256': h.sha(Path(__file__).read_bytes()),
                'core_sha256': h.sha((ROOT/'tools/hd_overlay.py').read_bytes())})
print(json.dumps({'passed': True, 'cases': results}))
