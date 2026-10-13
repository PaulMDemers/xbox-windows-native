"""Explicitly include actual engine return-site and API providers before launch."""
from pathlib import Path
K=Path(__file__).resolve().parent
target=K/'review-sites002.py';assert not target.exists()
s=(K/'review-sites.py').read_text().replace("dest=K/'sites001.json'","dest=K/'sites002.json'")
needle='md=capstone.Cs'
assert s.count(needle)==1
s=s.replace(needle,"""for name in ['win32k.sys','gdi32.dll']:
    path=Path(old['modules'][name]['path']);assert sha(path)==old['modules'][name]['sha256']
    p=pes[name]=pefile.PE(str(path));mods[name]=dict(path=str(path),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage)
"""+needle)
target.write_bytes(s.encode())
