"""Package positive and negative CD/second-stage diagnostic fixtures."""
import argparse, hashlib, io, json, pathlib, sys
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parents[1]/'work/python-packages'))
import pycdlib
sys.path.insert(0,str(kit.parent/'native-windows-prebuild'))
from validate_loader import validate
parser=argparse.ArgumentParser()
parser.add_argument('--freeldr',type=pathlib.Path,required=True)
parser.add_argument('--rosload',type=pathlib.Path,required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
parser.add_argument('--variant',choices=['good','corrupt-data','bad-token'],default='good')
args=parser.parse_args()
if args.output.exists(): parser.error('Output exists; choose a fresh path')
freeldr=args.freeldr.read_bytes(); rosload=args.rosload.read_bytes()
report=validate(freeldr)
assert b'XWN50:' in freeldr and b'XWN60:' in rosload and b'XWN98:' in rosload
probe=bytearray((i*37+(i>>8)+0x5a)&255 for i in range(131075))
if args.variant=='corrupt-data': probe[65537]^=1
token='WRONG-TOKEN' if args.variant=='bad-token' else 'XWN-SECOND-STAGE-20261003'
config=f'[XwnProbe]\r\nToken={token}\r\n'.encode()
files={'/LOADER/FREELDR.SYS;1':freeldr,'/LOADER/ROSLOAD.EXE;1':rosload,'/PROBE.BIN;1':bytes(probe),'/FREELDR.INI;1':config}
iso=pycdlib.PyCdlib();iso.new(interchange_level=3,vol_ident='XWN_VOLUME_PROBE');iso.add_directory(iso_path='/LOADER')
streams=[]
for name,data in files.items():
    stream=io.BytesIO(data);streams.append(stream);iso.add_fp(stream,len(data),iso_path=name)
args.output.parent.mkdir(parents=True,exist_ok=True)
iso.write(str(args.output));iso.close()
iso=pycdlib.PyCdlib();iso.open(str(args.output))
for name,data in files.items():
    stream=io.BytesIO();iso.get_file_from_iso_fp(stream,iso_path=name);assert stream.getvalue()==data
iso.close()
report.update(variant=args.variant,files={n:hashlib.sha256(d).hexdigest() for n,d in files.items()},iso_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),readback_verified=True,windows_included=False)
args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
