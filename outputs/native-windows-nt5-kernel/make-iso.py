"""Package a debugger-gated kernel-entry diagnostic; no Windows files."""
import argparse,hashlib,io,json,pathlib,sys
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(out.parents[1]/'work/python-packages'))
sys.path.insert(0,str(out.parent/'native-windows-prebuild'))
import pycdlib
from validate_loader import validate
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--autorun',action='store_true');p.add_argument('--loader-directory',type=pathlib.Path);p.add_argument('--hal-directory',type=pathlib.Path);a=p.parse_args()
assert not a.output.exists()
art=out/'artifacts';loader=a.loader_directory or (art/'autorun' if a.autorun else art);files={'/LOADER/'+n.upper()+';1':((loader if n in ['freeldr.sys','rosload.exe'] else (a.hal_directory if n == 'halxboxnt5.dll' and a.hal_directory else art))/n).read_bytes() for n in ['freeldr.sys','rosload.exe','halxboxnt5.dll','xboxbvid.dll']}
assert b'XWNH30:' in files['/LOADER/ROSLOAD.EXE;1'] and b'XWNHPNT5' in files['/LOADER/ROSLOAD.EXE;1']
files['/PROBE.BIN;1']=bytes((i*37+(i>>8)+0x5a)&255 for i in range(131075))
files['/FREELDR.INI;1']=b'[XwnProbe]\r\nToken=XWN-SECOND-STAGE-20261003\r\n[FREELOADER]\r\nTimeOut=0\r\n[Display]\r\nDisplayMode=Normal\r\n'
report=validate(files['/LOADER/FREELDR.SYS;1'])
iso=pycdlib.PyCdlib();iso.new(interchange_level=3,vol_ident='XWN_NT5_HANDOFF');iso.add_directory(iso_path='/LOADER')
streams=[]
for name,data in files.items():
 stream=io.BytesIO(data);streams.append(stream);iso.add_fp(stream,len(data),iso_path=name)
iso.write(str(a.output));iso.close();iso=pycdlib.PyCdlib();iso.open(str(a.output))
for name,data in files.items():
 stream=io.BytesIO();iso.get_file_from_iso_fp(stream,iso_path=name);assert stream.getvalue()==data
iso.close()
report.update(files={n:hashlib.sha256(d).hexdigest() for n,d in files.items()},iso_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),readback_verified=True,windows_included=False,kernel_entry_enabled=True,requires_debugger_gate=not a.autorun)
a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
