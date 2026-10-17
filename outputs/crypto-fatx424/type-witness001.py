"""Type a reviewed path into the visible Run dialog; submit only after screenshot review."""
import json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
out=K/'emu001/manual-witness-typed.json';assert not out.exists()
lock=acquire_monitor_lock(5456);command(5456,'sendkey meta_l-r');time.sleep(1)
for c in r'C:\XWN423BIN\create.exe':
    key='shift-'+c.lower() if c.isupper() else {':':'shift-semicolon','\\':'backslash','.':'dot'}.get(c,c)
    command(5456,'sendkey '+key);time.sleep(.15)
out.write_text(json.dumps(dict(path=r'C:\XWN423BIN\create.exe',submitted=False,ordinary_keyboard_input=True))+'\n')
