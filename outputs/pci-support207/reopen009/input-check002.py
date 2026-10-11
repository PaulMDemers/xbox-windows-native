"""Bounded USB input observation in the journaled owned emulator after trace cleanup."""
import datetime,hashlib,json,socket,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001'
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
from PIL import Image
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
r=read(case/'run.json');t=read(case/'trace.json')
assert not r['closed'] and r['launch_requested']
assert 'tcp:127.0.0.1:4884,server,nowait' in r['argv']
assert t['status']=='both_class_failures_captured' and t['breakpoints_remaining']==0 and t['guest_resumed']
mode=sys.argv[1];commands={'before':None,'keyboard':'sendkey ctrl-esc','restore':'sendkey esc','mouse':'mouse_move 80 60'}
assert mode in commands
dest=case/('input002-'+mode+'.json');assert not dest.exists()
if mode=='keyboard':assert (case/'input002-before.json').exists()
if mode=='restore':assert (case/'input002-keyboard.json').exists()
if mode=='mouse':assert (case/'input002-restore.json').exists()
record=dict(scope=__doc__,pid=r['pid'],physical_access=False,mode=mode,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),trace_finished_utc=t['finished_utc'],commands=[])
def command(text):
    with socket.create_connection(('127.0.0.1',4884),timeout=5) as s:
        def reply():
            b=b''
            while not b.endswith(b'(qemu) '):
                part=s.recv(65536)
                if not part:raise EOFError('monitor closed')
                b+=part
            return b.decode(errors='replace')
        reply();s.sendall((text+'\n').encode());result=reply()
    record['commands'].append(dict(command=text,response=result))
if commands[mode]:command(commands[mode]);time.sleep(2)
png=case/'artifacts/runtime'/('input002-'+mode+'.png');assert not png.exists()
capture=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-prebuild/monitor_capture.py')
subprocess.run([sys.executable,str(capture),'--port','4884','--output',str(png),'--auto-framebuffer','--width','640','--height','480','--pitch','2560'],check=True)
record.update(capture_script_sha256=hashlib.sha256(capture.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),capture_metadata=json.loads(png.with_suffix('.json').read_text()))
record.update(image=str(png),sha256=hashlib.sha256(png.read_bytes()).hexdigest(),size=Image.open(png).size)
dest.write_text(json.dumps(record,indent=2)+'\n');print(png)
