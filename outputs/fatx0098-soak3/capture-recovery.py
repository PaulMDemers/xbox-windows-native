"""Read-only, resumable capture of this console's installed Windows baseline.

File-level recovery bundle, not a disk image. Never fetch game trees, firmware,
keys or the pagefile. Keep binaries and profiles in the user's local archive.
"""
import datetime, ftplib, hashlib, io, json, os, pathlib, socket, zipfile

KIT = pathlib.Path(__file__).resolve().parent
DEST = pathlib.Path('E:/Codex-archive/xbox-windows-native/fatx0098-video0093-20261006')
STAGE = DEST / 'physical-files'
STATE = DEST / 'capture-manifest.json'
sha = lambda b: hashlib.sha256(b).hexdigest()
utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()

class FTP(ftplib.FTP):
    def ntransfercmd(self, *a, **kw):
        sock, size = super().ntransfercmd(*a, **kw)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock, size

def get(f, p):
    b = io.BytesIO(); f.retrbinary('RETR ' + p, b.write, 65536)
    return b.getvalue()

def listing(f, p):
    f.cwd(p); lines = []; f.retrlines('LIST', lines.append)
    out = []
    for line in lines:
        parts = line.split(None, 8)
        assert len(parts) == 9, line
        name = parts[8]
        if name in ('.', '..'): continue
        assert '/' not in name and '\\' not in name and ':' not in name, name
        assert parts[0][0] in ('d', '-'), line
        out.append(dict(name=name, directory=parts[0][0]=='d', bytes=int(parts[4])))
    return sorted(out, key=lambda x: x['name'].lower())

def main():
    qualification=json.loads((KIT/'qualification.json').read_text());assert qualification['passed']
    assert json.loads((KIT/'final-state.json').read_text())['passed']
    DEST.mkdir(parents=True, exist_ok=True)
    r = json.loads(STATE.read_text()) if STATE.exists() else dict(
        started_utc=utc(), scope=__doc__, files={}, directories={}, complete=False)
    def save():
        temp = STATE.with_suffix('.tmp'); temp.write_text(json.dumps(r, indent=2)+'\n'); temp.replace(STATE)
    def file(f, remote, size):
        local = STAGE / remote.lstrip('/')
        old = r['files'].get(remote)
        if old and local.exists():
            assert old['bytes']==size and sha(local.read_bytes())==old['sha256'], remote
            return
        local.parent.mkdir(parents=True, exist_ok=True)
        temp = local.with_name(local.name+'.download')
        h = hashlib.sha256(); count = 0
        with temp.open('wb') as out:
            def write(b):
                nonlocal count
                count += len(b); assert count <= size, remote
                h.update(b); out.write(b)
            f.retrbinary('RETR '+remote, write, 65536)
        assert count == size, remote
        temp.replace(local)
        r['files'][remote] = dict(bytes=count, sha256=h.hexdigest())
        if len(r['files']) % 100 == 0:
            save(); print('Captured',len(r['files']),'files',flush=True)
    def tree(f, remote):
        entries = listing(f, remote)
        (STAGE / remote.lstrip('/')).mkdir(parents=True, exist_ok=True)
        for e in entries:
            p = remote+'/'+e['name']
            if e['directory']: tree(f, p)
            else: file(f, p, e['bytes'])
        assert listing(f, remote)==entries, 'Directory changed: '+remote
        r['directories'][remote] = entries; save()
    with FTP() as f:
        from physical import owner,checks,passed,startup,baseline
        f.connect(os.environ['XWN_FTP_HOST'], timeout=30); f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        owner(f);assert passed(checks(f,True))
        assert sha(get(f,startup))==baseline['startup_sha256']
        fingerprint={path:sha(get(f,path)) for path in [startup,'/F/winnt/system32/config/system','/F/winnt/system32/config/software','/F/winnt/system32/config/sysevent.evt']}
        if 'console_fingerprint' in r:assert r['console_fingerprint']==fingerprint,'Console changed since capture began; preserve this incomplete snapshot'
        else:r['console_fingerprint']=fingerprint;save()
        for p in ['/E/Applications/XWNFBoot','/F/winnt','/F/documents and settings','/F/program files','/F/xwnpaint','/F/xwnpaint16','/F/xwneof98','/F/xwns98','/F/xwns98-first','/F/xwns98-second']:
            tree(f,p)
        root = listing(f,'/F')
        for e in root:
            if not e['directory'] and (e['name'].lower().startswith('xwn') or e['name'].lower()=='hello_xbox.txt'): file(f,'/F/'+e['name'],e['bytes'])
        r['excluded']=['F:/Games','F:/Applications','F:/pagefile.sys','other console partitions and firmware','non-project F-root files except previously captured hello_xbox.txt']
        for name in ['config.xml','default.xbe']:
            data=get(f,'/C/Dashboard/'+name);p='/C/Dashboard/'+name
            target=STAGE/p.lstrip('/');target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists(): assert target.read_bytes()==data
            else: target.write_bytes(data)
            r['files'][p]=dict(bytes=len(data),sha256=sha(data))
        assert passed(checks(f,True))
        assert {path:sha(get(f,path)) for path in fingerprint}==fingerprint
        assert sha(get(f,startup))==baseline['startup_sha256']
    r['captured_utc']=utc();save()
    bundles=[]
    for name, prefix in [('xwn-fatx0098-video0093-physical-system.zip','/F/'),('xwn-fatx0098-video0093-boot-dashboard.zip',None)]:
        selected={p:v for p,v in r['files'].items() if (p.startswith(prefix) if prefix else not p.startswith('/F/'))}
        target=DEST/name
        if not target.exists():
            temp=target.with_suffix('.partial')
            with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                for p in selected: z.write(STAGE/p.lstrip('/'),p.lstrip('/'))
                for p in r['directories']:
                    if (p.startswith(prefix) if prefix else not p.startswith('/F/')): z.writestr(p.lstrip('/')+'/',b'')
                z.writestr('BUNDLE-MANIFEST.json',json.dumps(selected,indent=2))
            temp.replace(target)
        with zipfile.ZipFile(target) as z:
            for p,info in selected.items():
                data=z.read(p.lstrip('/'));assert len(data)==info['bytes'] and sha(data)==info['sha256'],p
        h=hashlib.sha256()
        with target.open('rb') as stream:
            for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
        bundles.append(dict(path=str(target),bytes=target.stat().st_size,sha256=h.hexdigest(),files=len(selected),all_entries_readback_verified=True))
    r.update(complete=True,completed_utc=utc(),bundles=bundles);save()
    summary=dict(scope='Local file-level physical recovery snapshot; no whole-disk or restore-test claim',
                 completed_utc=r['completed_utc'],files=len(r['files']),bytes=sum(v['bytes'] for v in r['files'].values()),
                 directories=len(r['directories']),bundles=bundles,manifest_path=str(STATE),manifest_sha256=sha(STATE.read_bytes()),
                 exclusions=r['excluded'],baseline_checks=True,console_left_on_dashboard=True)
    (KIT/'capture-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
