"""Read-only framebuffer capture from the owned running native001 monitor."""
import hashlib,json,socket,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;out=k/'native001/artifacts/runtime'
run=json.loads((k/'native001/run.json').read_text());assert not run['closed'] and run['launch_requested']
p=out/'screen.ppm';assert not p.exists()
with socket.create_connection(('127.0.0.1',4684),timeout=10) as s:
    def reply():
        data=b''
        while not data.endswith(b'(qemu) '):
            b=s.recv(65536)
            if not b:raise EOFError()
            data+=b
        return data.decode('utf-8',errors='replace')
    reply();command='screendump "'+p.as_posix()+'"'
    s.sendall((command+'\n').encode());response=reply()
assert p.exists()
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
from PIL import Image
Image.open(p).save(out/'screen.png')
(k/'native001/capture.json').write_text(json.dumps(dict(scope=__doc__,pid=run['pid'],command=command,response=response,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),no_input=True),indent=2)+'\n')
print('Owned framebuffer saved')
