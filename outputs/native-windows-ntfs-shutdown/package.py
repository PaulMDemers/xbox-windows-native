"""Pin the proven NTFS loader when combining the new HAL and boot video."""
from pathlib import Path
import argparse,hashlib,io,json,subprocess,sys
kit=Path(__file__).resolve().parent;root=kit.parents[1]
sys.path.insert(0,str(root/'work/python-packages'))
import pycdlib
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert not a.output.exists()
source=root/'outputs/native-windows-nt5-kernel/artifacts/kernel-autorun-006.iso'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='2d6f0d0813dcb12a29ecb8d8693cdd4f424b26d0d7b9bde746af88de14a67180'
loader=kit/'artifacts/loader006';loader.mkdir(exist_ok=True)
iso=pycdlib.PyCdlib();iso.open(str(source))
for name in ['freeldr.sys','rosload.exe']:
 data=io.BytesIO();iso.get_file_from_iso_fp(data,iso_path='/LOADER/'+name.upper()+';1')
 path=loader/name
 if path.exists():assert path.read_bytes()==data.getvalue()
 else:path.write_bytes(data.getvalue())
iso.close()
for path,sha in [(root/'outputs/native-windows-hal-paging/artifacts/halxboxnt5.dll','747b7fb8137757e8757b28b274107ea642a7236a95a54840e05f824aae1c710f'),
                 (root/'outputs/native-windows-bootvid-framebuffer/artifacts/xboxbvid.dll','2196f646653c4c944d73fee4944ee3d056c82cf01903e4f435e67d63c03ed4b7')]:
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
subprocess.run([sys.executable,str(root/'outputs/native-windows-nt5-kernel/make-iso.py'),'--autorun',
 '--loader-directory',str(loader),'--hal-directory',str(root/'outputs/native-windows-hal-paging/artifacts'),
 '--bootvid-directory',str(root/'outputs/native-windows-bootvid-framebuffer/artifacts'),'--output',str(a.output)],check=True)
