"""Create read-only diagnostic media after the loader build; includes no Windows files."""
import argparse,pathlib,sys,json
from validate_loader import validate
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parents[1]/'work/python-packages'))
import pycdlib
parser=argparse.ArgumentParser()
parser.add_argument('--freeldr',required=True,type=pathlib.Path)
parser.add_argument('--output',required=True,type=pathlib.Path)
args=parser.parse_args()
if args.output.exists(): parser.error('Output already exists; choose a fresh artifact name')
data=args.freeldr.read_bytes();report=validate(data)
if b'XWN40: Diagnostic complete.' not in data:
    parser.error('Expected the diagnostic build containing the XWN40 stop marker')
iso=pycdlib.PyCdlib();iso.new(interchange_level=3,vol_ident='XWN_PREFLIGHT')
iso.add_directory(iso_path='/LOADER')
iso.add_file(str(args.freeldr),iso_path='/LOADER/FREELDR.SYS;1')
args.output.parent.mkdir(parents=True,exist_ok=True)
iso.write(str(args.output));iso.close()
report['iso']=str(args.output.resolve());report['windows_included']=False
args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
