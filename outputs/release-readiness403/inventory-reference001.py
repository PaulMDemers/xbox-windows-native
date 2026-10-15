import zipfile,json,hashlib
from pathlib import Path
p=Path('C:/xwn399/system002/xwn-private-E-720p-demo-20261014.zip')
out=Path('C:/xwn403/installed-reference001');out.mkdir(parents=True,exist_ok=False)
rows=[]
with zipfile.ZipFile(p) as z:
    for n in z.namelist():
        low=n.lower();leaf=low.rsplit('/',1)[-1]
        if low.startswith('payload/e/') and (leaf=='halxboxnt5.dll' or low.endswith(('.sys','.dll','.exe')) and any(x in leaf for x in ['usb','hid','mou','kbd','xinput','nvnet'])):
            b=z.read(n);dest=out/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
            rows.append({'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
Path('outputs/release-readiness403/reference-inventory001.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
