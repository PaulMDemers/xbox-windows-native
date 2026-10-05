"""Collect cycle014 after dashboard return; preserve Paint file and disable autostart."""
import datetime, ftplib, hashlib, io, json, os, pathlib, struct
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-014.json'
r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('evidence_collected_utc')
sha=lambda b:hashlib.sha256(b).hexdigest()
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def get(f,name,optional=False):
    b=io.BytesIO()
    try:f.retrbinary('RETR '+name,b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):return None
        raise
    return b.getvalue()
def preserve(name,b):
    p=k/'artifacts'/('physical-014-'+name)
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    return {'bytes':len(b),'sha256':sha(b)}
with ftplib.FTP() as f:
    f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F');assert json.loads(get(f,'xwn-deploy-v1.json'))==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    previous=get(f,r['startup_backup'])
    assert sha(previous)==json.loads((k/'physical-cycle-013.json').read_text())['current_startup_sha256']
    f.cwd('/F/documents and settings/all users/start menu/programs/startup')
    current=get(f,'xwnsetup.cmd');assert sha(current) in [r['startup_sha256'],sha(previous)]
    if current!=previous:f.storbinary('STOR xwnsetup.cmd',io.BytesIO(previous),blocksize=1024)
    assert get(f,'xwnsetup.cmd')==previous
    r.update(startup_paint_enabled=False,current_startup_sha256=sha(previous));save()
    f.cwd('/F');assert sha(get(f,'xwn-report-v2.txt'))==r['prior_cache_report_sha256']
    bitmap=get(f,'xwn-paint-test.bmp',True)
    r['paint_file']=None
    if bitmap is not None:
        row=preserve('xwn-paint-test.bmp',bitmap);row['bmp_header_valid']=False
        if len(bitmap)>=54 and bitmap[:2]==b'BM':
            declared,offset,dib=struct.unpack_from('<I',bitmap,2)[0],struct.unpack_from('<I',bitmap,10)[0],struct.unpack_from('<I',bitmap,14)[0]
            width,height,planes,bpp=struct.unpack_from('<iiHH',bitmap,18)
            row.update(declared_bytes=declared,pixel_offset=offset,dib_bytes=dib,width=width,height=height,bits_per_pixel=bpp,
                       bmp_header_valid=declared==len(bitmap) and 54<=offset<=len(bitmap) and dib>=40 and width>0 and height!=0 and planes==1)
        r['paint_file']=row
    for directory,names in [('/F/winnt/system32',['xwn-video-trace.bin']),('/F/winnt/system32/config',['sysevent.evt','appevent.evt','system','software','sam','security','default']),('/F/winnt',['setupapi.log'])]:
        f.cwd(directory)
        for name in names:r.setdefault('collected',{})[name]=preserve(name,get(f,name))
    f.cwd('/F/winnt/system32/drivers')
    assert sha(get(f,'xwnfatx.sys'))==r['filesystem_sha256']
    assert sha(get(f,'xboxvnt5.sys'))==r['miniport_sha256']
    assert sha(get(f,'xboxvnt5.xwn-c13'))==r['previous_miniport_sha256']
    f.cwd('/E/Applications/XWNFBoot/loader');assert sha(get(f,'halxboxnt5.dll'))==r['hal_sha256']
    r['evidence_collected_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r['status']='physical_paint_evidence_collected';save()
print(json.dumps(r,indent=2))
