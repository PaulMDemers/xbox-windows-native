"""After visual confirmation of the owned logon screen, type private defaults."""
import json, sys, time
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
case=sys.argv[1];assert case in ['emu005']
out=K/case/'logon-action.json';assert not out.exists()
secret=json.loads(Path('C:/xwn405/logon-private001.json').read_text())['DefaultPassword']
plain={' ':'spc','-':'minus','=':'equal','.':'dot',',':'comma','/':'slash',';':'semicolon',"'":'apostrophe','[':'bracket_left',']':'bracket_right','\\':'backslash','`':'grave_accent'}
shift=dict(zip('!@#$%^&*()_+<>?:"{}|~',['1','2','3','4','5','6','7','8','9','0','minus','equal','comma','dot','slash','semicolon','apostrophe','bracket_left','bracket_right','backslash','grave_accent']))
keys=[]
for c in secret:
    if c.isascii() and c.isalnum():keys.append(('shift-' if c.isupper() else '')+c.lower())
    elif c in plain:keys.append(plain[c])
    elif c in shift:keys.append('shift-'+shift[c])
    else:raise ValueError('Unsupported private input character')
lock=acquire_monitor_lock(5456)
for key in ['alt-p','home','shift-end']+keys+['ret']:
    command(5456,'sendkey '+key);time.sleep(.15)
out.write_text(json.dumps(dict(source='Private default credentials from owned fresh404 installation',ordinary_keyboard_input=True,values_logged=False))+'\n')
print('Normal logon submitted; private values omitted')
