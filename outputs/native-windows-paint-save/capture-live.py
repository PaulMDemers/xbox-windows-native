"""Capture the known guest framebuffer without interfering with a GDB trace."""
import argparse,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path[:0]=[str(ws/'work/python-packages'),str(k.parent/'native-windows-prebuild')]
from PIL import Image
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
assert a.name.replace('-','').isalnum()
run=ws/'work/runs/nt5-paint-trace-001';ref=json.loads((run/'paint-ready.json').read_text())
raw=run/(a.name+'.raw');out=run/(a.name+'.png');assert not raw.exists() and not out.exists()
with acquire_monitor_lock(4594):command(4594,f'pmemsave {ref["address"]} {ref["pitch"]*ref["height"]} {json.dumps(raw.as_posix())}')
Image.frombytes('RGB',(ref['width'],ref['height']),raw.read_bytes(),'raw','BGRX',ref['pitch'],1).save(out)
raw.unlink();print(out)
