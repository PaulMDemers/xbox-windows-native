"""Private fixed-profile E migration package. No overwrite, delete or Windows boot API."""
import hashlib,json,zipfile
from pathlib import Path

ROOTS=('/E/winnt','/E/documents and settings','/E/program files','/E/Applications/XWNEBoot')
LAUNCHER=ROOTS[3]+'/default.xbe'
class Refused(RuntimeError):pass
def require(ok,why):
    if not ok:raise Refused(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def info(b):return dict(bytes=len(b),sha256=sha(b))
def allowed(p):
    return isinstance(p,str) and p.isascii() and p.startswith('/') and all(ord(c)>=32 and ord(c)!=127 and c not in '\\:*?"<>|' for c in p) and all(x and x not in ('.','..') and len(x)<=42 for x in p.split('/')[1:]) and any(p==r or p.startswith(r+'/') for r in ROOTS)
def layout(m):
    require(m['profile']=='stock-e-1080i' and m['version']==1,'Unknown profile')
    files=m['files'];dirs=set(m['directories'])|set(ROOTS)
    require(LAUNCHER in files and all(allowed(p) for p in files) and all(allowed(p) for p in dirs),'Invalid E path')
    require(len({p.lower() for p in files})==len(files),'Case collision')
    for p,meta in files.items():
        require(type(meta['bytes']) is int and 0<=meta['bytes']<=64*1024**2,'File size bound')
        require(isinstance(meta['sha256'],str) and len(meta['sha256'])==64 and all(c in '0123456789abcdef' for c in meta['sha256']),'Hash encoding')
        parent=p.rsplit('/',1)[0]
        while parent not in ('/E','/E/Applications'):
            require(allowed(parent),'Invalid parent');dirs.add(parent);parent=parent.rsplit('/',1)[0]
    require(not ({p.lower() for p in files}&{p.lower() for p in dirs}),'File/directory collision')
    require(len({p.lower() for p in dirs})==len(dirs),'Directory collision')
    return files,dirs

class Package:
    def __init__(self,archive,policy):
        self.archive=Path(archive);self.policy=load(policy)
        self.z=zipfile.ZipFile(archive)
        require(self.z.getinfo('MANIFEST.json').file_size<=2*1024**2,'Manifest size bound')
        raw=self.z.read('MANIFEST.json')
        require(sha(raw)==self.policy['manifest_sha256'],'Unrecognized manifest')
        self.m=json.loads(raw);self.files,self.dirs=layout(self.m)
        expected={'payload'+p for p in self.files}|set(self.m['support'])|{'MANIFEST.json'}
        require(len(self.z.infolist())==len(expected) and set(self.z.namelist())==expected,'Duplicate/missing/extra ZIP entry')
        self.archive_sha256=self.hash_archive()
        for p in self.files:require(info(self.read(p))==self.files[p],'Payload differs: '+p)
        for p,meta in self.m['support'].items():
            require(0<=meta['bytes']<=64*1024**2 and self.z.getinfo(p).file_size==meta['bytes'],'Support size bound')
            require(info(self.z.read(p))==meta,'Support differs: '+p)
        self.allocated=sum(((v['bytes']+16383)//16384)*16384 for v in self.files.values())+(len(self.dirs)+20)*16384
    def hash_archive(self):
        h=hashlib.sha256()
        with self.archive.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        return h.hexdigest()
    def read(self,p):
        require(p in self.files,'Read outside package')
        row=self.z.getinfo('payload'+p);require(row.file_size==self.files[p]['bytes'],'ZIP declared size mismatch')
        return self.z.read(row)

def vacant(remote):
    for p in ROOTS:require(not remote.exists(p),'Occupied target refused: '+p)

def create(package,remote,record):
    vacant(remote)
    for p in sorted(package.dirs,key=lambda x:(x.count('/'),x)):
        require(not remote.exists(p),'Directory appeared: '+p)
        record('mkdir_intent',p,None);remote.mkdir(p);record('mkdir_done',p,None)
    for p in sorted(set(package.files)-{LAUNCHER})+[LAUNCHER]:
        require(not remote.exists(p),'File appeared: '+p)
        b=package.read(p);require(info(b)==package.files[p],'Local bytes changed')
        record('write_intent',p,package.files[p]);remote.create(p,b)
        require(remote.read(p)==b,'Readback mismatch: '+p)
        record('write_verified',p,package.files[p])
    return dict(files=len(package.files),launcher_last=True,overwritten_files=0)

def capacity(raw,allocated):
    rows=raw.decode('ascii').splitlines()
    require(len(rows)==4 and rows[0]=='XWN-CAPACITY-333' and rows[-1]=='COMPLETE 333','Incomplete capacity report')
    parsed=[]
    for row,pid in zip(rows[1:3],[1,6]):
        v=row.split();require(len(v)==7 and v[0]=='SPACE','Malformed capacity row')
        n,start,length,unit,total,free=map(int,v[1:]);require(n==pid and 0<=free<=total<=length and unit>0,'Capacity range')
        parsed.append(dict(partition=n,start=start,length=length,cluster_bytes=unit,total_bytes=total,free_bytes=free))
    e=parsed[0]
    require((e['start'],e['length'],e['cluster_bytes'])==(2884108288,5120024576,16384),'Not the reviewed standard E geometry')
    require(e['free_bytes']>=allocated+256*1024**2,'Insufficient E capacity plus reserve')
    return parsed
