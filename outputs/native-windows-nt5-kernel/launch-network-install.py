"""Launch only the staged, task-owned NIC installer through emulated USB input."""
import argparse,json,pathlib,sys,time
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(out.parent/'native-windows-prebuild'))
from monitor_capture import command
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--run',type=pathlib.Path,required=True);a=p.parse_args()
actions=[]
def key(name):
 reply=command(a.port,'sendkey '+name);actions.append({'key':name,'reply':reply});time.sleep(.35)
key('meta_l-r');time.sleep(2);key('ctrl-a')
mapping={':':'shift-semicolon','\\':'backslash','.':'dot'}
for char in 'c:\\xwnsetup.exe':key(mapping.get(char,char))
key('ret');time.sleep(1);key('ret')
(a.run/'network-install-launch.json').write_text(json.dumps({'command':'C:\\xwnsetup.exe','actions':actions},indent=2)+'\n')
