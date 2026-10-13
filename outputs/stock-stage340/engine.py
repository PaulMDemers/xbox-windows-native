"""Create-only E installation transaction. No deletion, overwrite, launch, or C/F write API."""
import hashlib
ROOTS=('/E/winnt','/E/documents and settings','/E/program files','/E/Applications/XWNEBoot')
LAUNCHER=ROOTS[3]+'/default.xbe'
def digest(b):return hashlib.sha256(b).hexdigest()
def allowed(path):
    if not isinstance(path,str) or '\\' in path or ':' in path or path.endswith('/'):return False
    parts=path.split('/')
    if parts[0]!='' or any(not p or p in ('.','..') or len(p.encode('ascii',errors='replace'))>42 for p in parts[1:]):return False
    return any(path==r or path.startswith(r+'/') for r in ROOTS)
def stage(files,directories,read_local,remote,journal):
    assert LAUNCHER in files and all(allowed(p) for p in files) and all(allowed(p) for p in directories)
    assert len({p.lower() for p in files})==len(files)
    for p,meta in files.items():
        b=read_local(p);assert len(b)==meta['bytes'] and digest(b)==meta['sha256'],p
    # Every installation root must be absent; existing Apps/Applications are preserved.
    assert all(not remote.exists(p) for p in ROOTS)
    parents=set(ROOTS)|set(directories)
    for p in files:
        parent=p.rsplit('/',1)[0]
        while parent not in ('/E','/E/Applications'):
            assert allowed(parent);parents.add(parent);parent=parent.rsplit('/',1)[0]
    for p in sorted(parents,key=lambda x:(x.count('/'),x)):
        assert not remote.exists(p);journal('mkdir_intent',p,None);remote.mkdir(p);journal('mkdir_done',p,None)
    ordered=sorted(set(files)-{LAUNCHER})+[LAUNCHER]
    for p in ordered:
        b=read_local(p);assert len(b)==files[p]['bytes'] and digest(b)==files[p]['sha256']
        assert not remote.exists(p),p
        journal('write_intent',p,files[p]);remote.create(p,b)
        actual=remote.read(p);assert actual==b,'Readback mismatch: '+p
        journal('write_verified',p,files[p])
    return dict(complete=True,files=len(ordered),launcher_written_last=True,readback_verified=True)
