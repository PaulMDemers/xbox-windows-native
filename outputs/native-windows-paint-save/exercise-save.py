"""Known Paint keyboard flow through the owned emulator monitor; no hardware access."""
import argparse,datetime,json,pathlib,subprocess,sys,time
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run=='nt5-paint-save-003'
run=ws/'work/runs'/a.run;assert run.exists() and not (run/'cleanup.json').exists()
report=run/'pattern-save-actions.json';assert not report.exists()
r=dict(scope=__doc__,actions=[],cases=[])
def action(c,delay=.2):
    with acquire_monitor_lock(4594):reply=command(4594,c)
    r['actions'].append(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=c))
    report.write_text(json.dumps(r,indent=2)+'\n');time.sleep(delay)
def text(s):
    mapping={':':'shift-semicolon','\\':'backslash',' ':'spc','.':'dot','-':'minus'}
    action('sendkey ctrl-a')
    for char in s:action('sendkey '+mapping.get(char,char)+' 1',.035)
def capture(name):
    subprocess.run([sys.executable,str(k.parent/'native-windows-prebuild/monitor_capture.py'),'--port','4594','--output',str(run/name),'--auto-framebuffer','--fallback-framebuffer','--width','1024','--height','576','--pitch','4096'],check=True)
for name in ['blank','coords','oddwidth']:
    action('sendkey ctrl-o');text('c:\\xwnpaint\\'+name+'.bmp');action('sendkey ret',2)
    capture(name+'-open.png')
    action('sendkey alt-f');action('sendkey a');text('c:\\xwnpaint\\saved-'+name+'.bmp');action('sendkey ret',3)
    capture(name+'-saved.png');r['cases'].append(dict(source='c:/xwnpaint/'+name+'.bmp',destination='c:/xwnpaint/saved-'+name+'.bmp',status='input_sent; visual and cold verification required'))
report.write_text(json.dumps(r,indent=2)+'\n')
