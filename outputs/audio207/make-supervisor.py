"""Keep the existing single-launch, ordinary loopback-only observer contract."""
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'video-text-oracle206/supervise-emulator.py').read_text()
s=s.replace("k/('emu-'+case)","k/case").replace('nt5-text206-','nt5-audio207-').replace('4596','4696').replace('time.monotonic()+520','time.monotonic()+400').replace('text206','audio207')
s=s.replace("utc=lambda:",'''# Recover only the documented local fixture defaults; never read console config.
import ast
tree=ast.parse((k.parent/'native-windows-prebuild/launch_unleashx.py').read_text())
login=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='login')
for name,arg in zip(['XWN_EMULATOR_FTP_USER','XWN_EMULATOR_FTP_PASSWORD'],login.args):
    os.environ.setdefault(name,ast.literal_eval(arg))
utc=lambda:''')
(k/'supervise.py').write_text(s)
