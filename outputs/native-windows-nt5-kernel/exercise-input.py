"""Exercise only the private emulator's USB input after its desktop boot."""
import argparse,json,pathlib,subprocess,sys,time
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(out.parent/'native-windows-prebuild'))
from monitor_capture import command
p=argparse.ArgumentParser();p.add_argument('--port',required=True,type=int);p.add_argument('--run',required=True,type=pathlib.Path)
p.add_argument('--width',type=int,default=640);p.add_argument('--height',type=int,default=480);p.add_argument('--pitch',type=int,default=2560);a=p.parse_args()
record={'scope':'Emulated USB input, not a physical keyboard or console test','actions':[]}
def action(text):
 reply=command(a.port,text);record['actions'].append({'command':text,'reply':reply})
def capture(name):
 subprocess.run([sys.executable,str(out.parent/'native-windows-prebuild/monitor_capture.py'),'--port',str(a.port),'--output',str(a.run/name),'--auto-framebuffer','--width',str(a.width),'--height',str(a.height),'--pitch',str(a.pitch)],check=True)
action('cont');time.sleep(20);capture('desktop-settled.png')
action('sendkey ctrl-esc');time.sleep(2);capture('keyboard-start-menu.png')
action('sendkey esc');time.sleep(1)
action('mouse_move 80 60');time.sleep(1);capture('mouse-moved.png')
(a.run/'input-exercise.json').write_text(json.dumps(record,indent=2)+'\n')
