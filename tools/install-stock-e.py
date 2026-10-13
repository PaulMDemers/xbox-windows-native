"""Verify, prepare (one capacity probe), or create-only install on the owned migration console."""
import argparse,datetime,importlib.util,json,os,secrets,sys,time
from pathlib import Path
from stock_e import Package,ROOTS,create,vacant,capacity,require,sha,load,info
from hd_overlay import save
W=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['verify','prepare','install'])
    p.add_argument('--profile',choices=['stock-e-1080i'],required=True)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--attempt',type=Path)
    a=p.parse_args();pkg=Package(a.archive,W/'tools/stock-e-profile.json')
    if a.action=='verify':
        print(json.dumps(dict(verified=True,files=len(pkg.files),archive_sha256=pkg.archive_sha256,physical_access=False)));return
    require(a.attempt is not None,'Private --attempt directory required')
    attempt=a.attempt.resolve();journal=attempt/'transaction.json'
    if a.action=='prepare':
        attempt.mkdir(parents=True,exist_ok=False)
        r=dict(state='preparing',profile=a.profile,archive_sha256=pkg.archive_sha256,source_pins={},writes=[],launch_requested=False,windows_launch_requested=False,console_C_accessed=False)
        for q in ['tools/install-stock-e.py','tools/stock_e.py','tools/stock-e-profile.json','tools/hd_overlay.py','outputs/demo-audio-level256/common001.py']:
            r['source_pins'][q]=sha((W/q).read_bytes())
        save(journal,r)
    else:
        r=load(journal);require(r['state']=='prepared','Attempt is not a completed preparation; never replay failed/consumed attempts')
        require(r['profile']==a.profile and r['archive_sha256']==pkg.archive_sha256,'Inputs changed')
        raw=(attempt/'capacity.txt').read_bytes()
        require(sha(raw)==r['capacity_sha256'],'Captured capacity report changed')
        require(capacity(raw,pkg.allocated)==r['capacity'],'Capacity interpretation changed')
        for q,h in r['source_pins'].items():require(sha((W/q).read_bytes())==h,'Source changed: '+q)
        require(0<=time.time()-r['prepared_unix']<=600,'Capacity preparation expired; obtain a new unique preparation')
    spec=importlib.util.spec_from_file_location('physical256',W/'outputs/demo-audio-level256/common001.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    h.ticket();fd=None;lock=h.queue/'stock-e343-active.lock'
    def protected(f):
        for q,meta in pkg.m['baseline'].items():require(info(h.get(f,q))==meta,'Original F rollback changed: '+q)
    class Remote:
        def __init__(self,f):self.f=f
        def exists(self,q):
            parent,name=q.rsplit('/',1);return name.lower() in {n.lower() for n in h.names(self.f,parent)}
        def mkdir(self,q):self.f.mkd(q)
        def create(self,q,b):h.ticket();h.put(self.f,q,b)
        def read(self,q):return h.get(self.f,q)
    try:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,str(attempt).encode());os.fsync(fd)
        with h.connect() as f:
            remote=Remote(f);vacant(remote);protected(f)
            if a.action=='prepare':
                folder='/E/Applications/XWNECap'+secrets.token_hex(4)
                require(not remote.exists(folder),'Probe namespace exists')
                b=pkg.z.read('support/capacity.xbe');r.update(capacity_remote=folder,capacity_payload_sha256=sha(b));save(journal,r)
                r['writes'].append(folder);save(journal,r);f.mkd(folder)
                r['writes'].append(folder+'/default.xbe');save(journal,r);h.put(f,folder+'/default.xbe',b)
                r.update(launch_requested=True,launch_utc=h.utc());save(journal,r);f.sock.settimeout(20)
                try:f.sendcmd('SITE EXEC '+folder.replace('/','\\').replace('\\E\\','E:\\',1)+'\\default.xbe')
                except Exception as exc:r['launch_reply_uncertain']=type(exc).__name__;save(journal,r)
            else:
                # A preparation is consumed before any directory or file mutation.
                r.update(state='installing',install_started_utc=h.utc());save(journal,r)
                deadline=time.monotonic()+7200
                with (attempt/'writes.jsonl').open('xb',buffering=0) as stream:
                    def record(kind,q,meta):
                        require(time.monotonic()<deadline,'Install deadline; preserve journal and inspect, never retry blindly')
                        stream.write((json.dumps(dict(utc=h.utc(),kind=kind,path=q,meta=meta))+'\n').encode());os.fsync(stream.fileno())
                    r.update(create(pkg,remote,record))
                protected(f);r.update(state='installed',normal_startup_unchanged=True);save(journal,r)
        if a.action=='prepare':
            deadline=time.monotonic()+300;done=False
            while time.monotonic()<deadline:
                time.sleep(3)
                try:
                    with h.connect(timeout=3) as f:
                        raw=h.get(f,folder+'/capacity.txt',optional=True)
                        if raw is None:continue
                        require(h.get(f,folder+'/default.xbe')==b,'Probe identity changed')
                        r['capacity']=capacity(raw,pkg.allocated);protected(f);vacant(Remote(f))
                        (attempt/'capacity.txt').write_bytes(raw);r['capacity_sha256']=sha(raw);done=True;break
                except (OSError,EOFError):continue
            require(done,'No complete capacity return; inspect recorded launch, never relaunch')
            r.update(state='prepared',prepared_unix=time.time(),allocated_bytes=pkg.allocated);save(journal,r)
    except BaseException as exc:
        r.update(state='failed',error_type=type(exc).__name__,quarantined=True);save(journal,r);raise
    finally:
        if fd is not None:os.close(fd);lock.unlink()
    print(json.dumps(dict(state=r['state'],windows_launch_requested=False,attempt=str(attempt))))

if __name__=='__main__':main()
