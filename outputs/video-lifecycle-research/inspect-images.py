"""Record actual owned debug identifiers and desktop API export RVAs, not symbols."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'));import pefile
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
rows=[];wanted={'CreateDesktopA','CreateDesktopW','SwitchDesktop','SetThreadDesktop','CloseDesktop','OpenDesktopA','OpenInputDesktop','GetThreadDesktop','ChangeDisplaySettingsExA'}
for name in ['win32k.sys','user32.dll','gdi32.dll']:
 b=(base/name).read_bytes();p=pefile.PE(data=b);row=dict(name=name,path=str(base/name),sha256=hashlib.sha256(b).hexdigest(),timestamp=p.FILE_HEADER.TimeDateStamp,image_base=p.OPTIONAL_HEADER.ImageBase,image_size=p.OPTIONAL_HEADER.SizeOfImage,debug=[],exports=[])
 for entry in getattr(p,'DIRECTORY_ENTRY_DEBUG',[]):
  d=entry.struct;payload=b[d.PointerToRawData:d.PointerToRawData+d.SizeOfData];assert len(payload)==d.SizeOfData
  row['debug'].append(dict(type=d.Type,file_offset=d.PointerToRawData,size=d.SizeOfData,sha256=hashlib.sha256(payload).hexdigest(),payload_hex=payload.hex()))
 for e in p.DIRECTORY_ENTRY_EXPORT.symbols:
  if e.name and e.name.decode() in wanted:
   row['exports'].append(dict(name=e.name.decode(),ordinal=e.ordinal,rva=e.address,forwarder=e.forwarder.decode() if e.forwarder else None,first32_hex=None if e.forwarder else p.get_data(e.address,32).hex()))
 rows.append(row)
assert rows[0]['sha256']=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
out=k/'owned-images.json';assert not out.exists();out.write_text(json.dumps(dict(physical_access=False,guest_launched=False,static_export_information_only=True,images=rows),indent=2)+'\n',encoding='utf-8');print('Owned PE identifiers and actual exports recorded; no inferred Win32k function names')
