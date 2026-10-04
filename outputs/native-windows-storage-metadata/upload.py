"""Install the validated inventory in its own F: directory; never launch it."""
from pathlib import Path
import datetime, ftplib, hashlib, io, json, os

kit = Path(__file__).resolve().parent
data = (kit/'artifacts/default.xbe').read_bytes()
v = json.loads((kit/'validation.json').read_text())
assert v['emulator_inventory_passed']
assert hashlib.sha256(data).hexdigest() == v['xbe_sha256']
r = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'host': '192.168.50.242', 'destination': '/F/Applications/XWNMetadata',
     'launched': False, 'xbe_sha256': v['xbe_sha256']}
f = ftplib.FTP()
try:
    f.connect(r['host'], 21, timeout=12)
    f.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F')
    for directory in ['Applications', 'XWNMetadata']:
        try: f.cwd(directory)
        except ftplib.error_perm as e:
            if not str(e).startswith(('550', '553')): raise
            f.mkd(directory); f.cwd(directory)
    def read(name):
        b = io.BytesIO()
        try: f.retrbinary('RETR '+name, b.write)
        except ftplib.error_perm as e:
            if str(e).startswith('550'): return None
            raise
        return b.getvalue()
    previous = read('default.xbe')
    assert previous is None or previous == data, 'Unrelated application at destination'
    if previous is None:
        stage = read('default.xbe.xwn-new')
        assert stage is None or stage == data, 'Unrecognized staging file'
        if stage is None:
            for at in range(0, len(data), 32768):
                f.storbinary(('STOR' if at == 0 else 'APPE')+' default.xbe.xwn-new',
                             io.BytesIO(data[at:at+32768]), blocksize=1024)
        assert read('default.xbe.xwn-new') == data
        f.rename('default.xbe.xwn-new', 'default.xbe')
    assert read('default.xbe') == data
    r.update(readback_verified=True, bytes=len(data),
             completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
except Exception as e:
    r['error'] = type(e).__name__+': '+str(e)
    raise
finally:
    f.close()
    (kit/'ftp-upload.json').write_text(json.dumps(r, indent=2)+'\n')
print('Metadata probe uploaded and verified. Manual launch only; XWNLoader unchanged.')
