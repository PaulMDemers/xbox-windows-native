"""Archive and remove only six enumerated game cache maps; preserve every other file."""
import argparse,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'fatx0101-physical'));import physical as m
archive=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/cache-cleanup-20261007')
items={'/X/cache002.map':83886080,'/X/cache003.map':83886080,'/X/cache004.map':293601280,'/X/cache005.map':293601280,'/Y/cache000.map':188743680,'/Y/cache001.map':545259520}
def listing(f,path):
    f.cwd(path);assert f.pwd().rstrip('/').lower()==path.lower();lines=[];f.retrlines('LIST',lines.append)
    out={}
    for line in lines:
        v=line.split(None,8);assert len(v)==9
        if v[8] not in ['.','..']:out[v[8]]=dict(directory=v[0].startswith('d'),bytes=int(v[4]))
    return out
def hashfile(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def main(action):
    with m.connect() as f:
        m.owner(f)
        if action=='backup':
            assert not (k/'cache-backup.json').exists() and not archive.exists()
            assert archive.resolve().is_relative_to(Path('E:/Codex-private-artifacts/xbox-windows-feasibility').resolve())
            archive.mkdir(parents=True);r=dict(scope=__doc__,utc=m.utc(),archive=str(archive),remote_writes=False,complete=False,files=[],before={d:listing(f,d) for d in ['/X','/Y']})
            m.save(r,k/'cache-backup.json')
            for path,size in items.items():
                parent,name=path.rsplit('/',1);assert r['before'][parent][name]==dict(directory=False,bytes=size)
                target=archive/(parent[1:]+'-'+name);assert not target.exists();h=hashlib.sha256();count=0;prefix=bytearray()
                with target.open('xb') as out:
                    def receive(data):
                        nonlocal count
                        count+=len(data);assert count<=size;h.update(data);out.write(data)
                        if len(prefix)<4096:prefix.extend(data[:4096-len(prefix)])
                    f.retrbinary('RETR '+path,receive,65536)
                assert count==size and hashfile(target)==h.hexdigest()
                r['files'].append(dict(path=path,bytes=size,local=str(target),sha256=h.hexdigest(),header_hex=bytes(prefix[:128]).hex()));m.save(r,k/'cache-backup.json');print('Archived/readback verified',path,size,flush=True)
            r.update(complete=True,completed_utc=m.utc());m.save(r,k/'cache-backup.json')
        else:
            r=json.loads((k/'cache-backup.json').read_text());assert r['complete'] and {v['path']:v['bytes'] for v in r['files']}==items
            assert not (k/'cache-removal.json').exists(),'Never repeat removal; inspect journal'
            assert all(listing(f,d)==r['before'][d] for d in ['/X','/Y'])
            result=dict(scope=__doc__,started_utc=m.utc(),backup_manifest_sha256=m.sha((k/'cache-backup.json').read_bytes()),deleted=[],complete=False)
            m.save(result,k/'cache-removal.json')
            for v in r['files']:
                local=Path(v['local']);assert local.resolve().parent==archive.resolve() and local.stat().st_size==v['bytes'] and hashfile(local)==v['sha256']
                h=hashlib.sha256();f.retrbinary('RETR '+v['path'],h.update,65536);assert h.hexdigest()==v['sha256'],'Remote changed; stop before deletion'
                result['pending_delete']=v['path'];m.save(result,k/'cache-removal.json')
                f.delete(v['path']);result['deleted'].append(v);result.pop('pending_delete');m.save(result,k/'cache-removal.json');print('Removed verified cached map',v['path'],flush=True)
            result['after']={d:listing(f,d) for d in ['/X','/Y']}
            for d in ['/X','/Y']:assert result['after'][d]=={name:value for name,value in r['before'][d].items() if d+'/'+name not in items}
            result.update(complete=True,completed_utc=m.utc(),reclaimed_file_bytes=sum(items.values()),all_other_root_entries_unchanged=True);m.save(result,k/'cache-removal.json')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['backup','remove']);main(p.parse_args().action)
