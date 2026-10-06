"""Inspect optional manually saved files; does not assert UI success or provenance."""
import io,json,struct,sys
from physical import k,ws,art,sha,save
sys.path.insert(0,str(ws/'work/python-packages'))
from PIL import Image
trial=json.loads((k/'physical.json').read_text());assert trial.get('collected_utc') and not trial['startup_enabled']
r=dict(scope=__doc__,files=[],user_observations='No observation recorded by this script; read the conversation separately.')
for name in ['manual-paint.bmp','manual-paint2.bmp','manual-note.txt']:
    path=art/('after-'+name);row=dict(name=name,present=path.exists())
    if path.exists():
        data=path.read_bytes();assert sha(data)==trial['collected'][name]['sha256'];row.update(bytes=len(data),sha256=sha(data))
        if name.endswith('.bmp'):
            try:
                assert data[:2]==b'BM' and struct.unpack_from('<I',data,2)[0]==len(data)
                im=Image.open(io.BytesIO(data));im.load();assert im.format=='BMP'
                row.update(bitmap_complete=True,dimensions=list(im.size),mode=im.mode)
            except Exception as exc:row.update(bitmap_complete=False,error=repr(exc))
    r['files'].append(row)
r['actual_ui_reopen_qualified']=False
save(r,k/'manual-file-audit.json');print(json.dumps(r,indent=2))
