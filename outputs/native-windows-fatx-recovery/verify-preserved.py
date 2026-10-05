"""Verify that physical preservation files still contain the exact pre-repair bytes."""
import ftplib,hashlib,io,json,pathlib,struct,os
k=pathlib.Path(__file__).resolve().parent;plan=json.loads((k/'repair-plan.json').read_text());scope=json.loads((k.parent/'native-windows-fatx-preflight/recovery-scope.json').read_text())
blob=(k/'artifacts/physical-001/cluster-data.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()==plan['backup_sha256']
blocks={struct.unpack_from('<I',blob,at)[0]:blob[at+4:at+65540] for at in range(0,len(blob),65540)}
files=[]
pressure=next(v for v in scope['files'] if v['path']=='/xwn-cache-pressure.tmp.c12');cim=next(v for v in scope['files'] if v['path'].endswith('/CIM.REP'))
for path,chain,size in [(pressure['path'],pressure['chain'],pressure['size']),('/xwn-recovery-cim.bin',cim['chain'],cim['chain_clusters']*65536),('/xwn-recovery-orphan.bin',scope['orphan_clusters'],65536)]:
 expected=b''.join(blocks[c] for c in chain)[:size]
 with ftplib.FTP('192.168.50.242',timeout=30) as f:
  f.login('xbox',os.environ['XWN_FTP_PASSWORD']);b=io.BytesIO();f.retrbinary('RETR /F'+path,b.write,blocksize=65536)
 assert b.getvalue()==expected;files.append(dict(path=path,bytes=size,sha256=hashlib.sha256(expected).hexdigest(),matches_backup=True))
r=dict(scope=__doc__,files=files,passed=True);(k/'preserved-payloads.json').write_text(json.dumps(r,indent=2)+'\n');print('All three preservation files match raw backup bytes')
