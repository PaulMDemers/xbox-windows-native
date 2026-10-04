from pathlib import Path
import sys,json,hashlib
kit=Path(__file__).resolve().parent;sys.path.insert(0,str(kit.parent.parent/'work/python-packages'))
import pefile
p=kit/'artifacts-normal/halxboxnt5.dll';pe=pefile.PE(str(p));rva=next(s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'XwnConfigureEntryProbe')
data=pe.get_data(rva,5);assert data==bytes.fromhex('31c0c20800'),data.hex()
map_rva=next(s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'XwnConfigureMapProbe')
assert pe.get_data(map_rva,5)==bytes.fromhex('31c0c20800')
(kit/'normal-hal-audit.json').write_text(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ordinary_hal_cannot_arm_probe':True,'configure_rva':hex(rva),'instructions':data.hex()},indent=2)+'\n')
