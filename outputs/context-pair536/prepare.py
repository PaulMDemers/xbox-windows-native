"""Namespace-only packaging of two qualified binaries; no compiler or network."""
from pathlib import Path
import datetime,hashlib,json,shutil,struct
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn536/package001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def transform(b,old,new):
    old=old.encode();new=new.encode()
    assert len(b)==542839 and len(old)==len(new) and b.count(old)==4 and new not in b
    c=bytearray(b.replace(old,new))
    c[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(c)-4096)+c[4096:]).digest()
    return bytes(c)
if __name__=='__main__':
    out=K/'prepared001.json';assert not out.exists() and not P.exists()
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    parents=[];pins={}
    for kit,path in [('context-adapter490','C:/xwn490/build001'),('d3d-transform494','C:/xwn494/build002')]:
        receipt=W/'outputs'/kit/('build001.json' if kit.endswith('490') else 'build002.json')
        r=read(receipt);b=(Path(path)/'default.xbe').read_bytes()
        assert sha(b)==r['sha256'];parents.append(b)
        pins[str(receipt)]=sha(receipt.read_bytes());pins[str(Path(path)/'default.xbe')]=sha(b)
    assert read(W/'outputs/context-adapter490/full-host002.json')['status']=='passed'
    syms=read(W/'outputs/context-adapter490/build001.json')['wrapper_symbols']
    assert syms==read(W/'outputs/d3d-transform494/build002.json')['wrapper_symbols']
    P.mkdir(parents=True);images={}
    for i,suffix in [(1,'a'),(2,'b')]:
        name='XWNBoot536'+suffix
        c=transform(parents[0],'XWNBoot490a',name)
        assert c==transform(parents[1],'XWNBoot494a',name)
        assert transform(c,name,'XWNBoot490a')==parents[0]
        folder=P/name;folder.mkdir();(folder/'default.xbe').write_bytes(c)
        source_rows=[]
        for n in ['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S']:
            old=(Path('C:/xwn490/build001')/n).read_bytes()
            expected=read(W/'outputs/context-adapter490/build001.json')['files']['/mnt/c/xwn490/build001/'+n]['sha256']
            assert sha(old)==expected
            new=old.replace(b'XWNBoot490a',name.encode())
            assert new.replace(name.encode(),b'XWNBoot490a')==old
            (folder/n).write_bytes(new)
            source_rows.append(dict(name=n,parent_sha256=sha(old),sha256=sha(new)))
        images[str(i)]=dict(path=str(folder/'default.xbe'),remote='/E/Applications/'+name,
                            sha256=sha(c),bytes=len(c),sources=source_rows)
    # Namespace-only package; no inherited runtime is executed or reparented.
    for n in ['decode.py','primary_decode.py','witness_decode.py','legacy_refusal_decode.py','failure_marker.py','receipts.py']:
        p=W/'outputs/d3d-transform494'/n;data=p.read_bytes();assert not (K/n).exists()
        (K/n).write_bytes(data);pins[str(p)]=sha(data)
    for rel in ['outputs/context-adapter490/full-host002.json','outputs/context-adapter490/full-transport002.json',
                'outputs/context-adapter490/host-run001.json','outputs/cold-pair534/final001.json',
                'outputs/cold-pair534/after2.json','outputs/restart-review535/audit001.json']:
        p=W/rel;pins[str(p)]=sha(p.read_bytes())
    r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),images=images,
           pins=pins,wrapper_symbols=syms,compiled=False,new_code=False,namespace_changes_per_image=4,
           physical_access=False,source_sha256=sha(Path(__file__).read_bytes()))
    out.write_text(json.dumps(r,indent=2)+'\n');print('PASS namespace-only packages from490 and494')
