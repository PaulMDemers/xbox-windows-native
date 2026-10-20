"""Static safety contract for the interactive launcher and fresh control fixture."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K/'launcher.c').read_text()
for forbidden in ['TerminateProcess(', 'ExitWindowsEx(', 'ChangeDisplaySettings', 'SendInput(', 'mouse_event(', 'keybd_event(', 'PostMessage', 'Sleep(']:assert forbidden not in s,forbidden
assert 'WaitForSingleObject(pi.hProcess,INFINITE)' in s
assert s.index('backup=CreateFileA')<s.index('changed=TRUE')<s.index('RegSetValueExA(key,"SetupPath"')<s.index('CreateProcessA(')
assert s.index('if(wait!=WAIT_OBJECT_0)')<s.index('cleanup:')
assert s.count('restore(key,')==3 and 'RegFlushKey(HKEY_LOCAL_MACHINE)' in s
assert 'CREATE_NEW' in s and 'if(!CreateDirectoryA("C:\\\\xwn624",0))' in s
assert 'C:\\\\xwn586-kit\\\\game' in s
files=[p for p in K.iterdir() if p.suffix in ['.py','.c','.h']]
r=dict(passed=True,scope='Static no-timer/no-input/no-reboot/no-force contract; not runtime or hardware proof',sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
(K/'host-tests002.json').write_text(json.dumps(r,indent=2)+'\n');print('Interactive launcher static contract passed')
