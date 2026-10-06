"""Read back the actual filenames found in the user-indicated98 folder."""
import io,json,struct,sys
from physical import k,ws,connect,owner,get,sha,save,utc
sys.path.insert(0,str(ws/'work/python-packages'))
from PIL import Image
out=k/'artifacts/manual-discovered';out.mkdir(parents=True,exist_ok=True)
r=dict(scope=__doc__,collected_utc=utc(),user_location='C drive from Explorer in the98 folder',files=[],actual_ui_reopen_success='not explicitly reported',physical_result=True)
with connect() as f:
    owner(f)
    for name,size in [('manual-apint.bmp',1534342),('manuel-note.txt',27)]:
        remote='/F/xwns98/'+name;data=get(f,remote);assert len(data)==size
        path=out/name
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
        row=dict(dashboard_path=remote,windows_path='C:\\xwns98\\'+name,bytes=len(data),sha256=sha(data),readback_verified=True)
        if name.endswith('.bmp'):
            assert data[:2]==b'BM' and struct.unpack_from('<I',data,2)[0]==len(data)
            im=Image.open(io.BytesIO(data));im.load();assert im.format=='BMP'
            row.update(bitmap_complete=True,dimensions=list(im.size),mode=im.mode)
        else:row['text_encoding']='ASCII' if data.isascii() else 'not classified'
        r['files'].append(row)
r['passed']=len(r['files'])==2 and all(v['readback_verified'] for v in r['files'])
save(r,k/'manual-discovered-audit.json');print(json.dumps(r,indent=2))
