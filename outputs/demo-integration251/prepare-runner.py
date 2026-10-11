"""Derive one joined audio/video supervisor; preserve the existing drawing and restart gates."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
source = ws / 'outputs/video-unattended202/runner.c'
old = source.read_text()
marker = '    timestamp("MEASUREMENT_START_TIME");'
assert old.count(marker) == 1
added = r'''    /* Audio completes before the drawing workload; only this supervisor reboots. */
    for(i=0;i<2;i++) {
        STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};
        const char *name=i?"probe.exe":"state.exe";
        wsprintfA(path,"%s\\%s",base,name);si.cb=sizeof(si);
        if(!CreateProcessA(path,NULL,NULL,NULL,FALSE,0,NULL,base,&si,&pi)) {
            gate_record(NULL,"FAIL_AUDIO_CREATE",GetLastError());ExitProcess(40);
        }
        CloseHandle(pi.hThread);
        status=WaitForSingleObject(pi.hProcess,180000);
        gate_record(NULL,i?"AUDIO_PROBE_JOIN":"AUDIO_STATE_JOIN",status);
        if(status!=WAIT_OBJECT_0){record("FAIL_AUDIO_UNJOINED\r\n");ExitProcess(41);}
        if(!GetExitCodeProcess(pi.hProcess,&status))ExitProcess(42);
        CloseHandle(pi.hProcess);
        gate_record(NULL,i?"AUDIO_PROBE_EXIT":"AUDIO_STATE_EXIT",status);
        if(status)ExitProcess(43);
    }
'''
# Raw string preserves C escapes; only Windows path separators need two backslashes.
new = old.replace(marker, added + marker)
assert new.replace(added, '') == old
assert new.count('ExitWindowsEx(') == 1
for name in ['runner.c', 'runner-source.json']:
    assert not (k / name).exists(), name
(k / 'runner.c').write_text(new)
for name in ['restart_gate.h', 'setup_gate.h']:
    blob = (ws / 'outputs/video-unattended202' / name).read_bytes()
    (k / name).write_bytes(blob)
sha = lambda b: hashlib.sha256(b).hexdigest()
(k / 'runner-source.json').write_text(json.dumps(dict(
    parent=str(source), parent_sha256=sha(source.read_bytes()),
    runner_sha256=sha((k/'runner.c').read_bytes()),
    only_change='Two bounded joined audio children before original drawing workload',
    unchanged_source_inverse=True, one_restart_owner=True,
    headers={n:sha((k/n).read_bytes()) for n in ['restart_gate.h','setup_gate.h']}), indent=2)+'\n')
