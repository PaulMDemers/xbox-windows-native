"""Read completed builds only; do not rebuild or replace historical records."""
import hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent
B=Path('/home/paul/xbox-windows-native')
out=K/'compiled-records001';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'profiles':[],'artifact_count':0,'scope':'Fresh builds, not guest validation of these binaries'}
for item in json.loads((K/'build-batch001.json').read_text()):
 assert item['exit_code']==0
 root=Path(item['output']);dest=out/item['profile'];dest.mkdir()
 for name in ['source.json','build.json','build-command.json']:
  shutil.copyfile(root/name,dest/name)
 record=json.loads((root/'build.json').read_text())
 artifacts=[]
 for p in sorted((root/'artifacts').rglob('*')):
  if p.is_file():artifacts.append({'path':p.relative_to(root).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
 assert artifacts
 result['artifact_count']+=len(artifacts)
 result['profiles'].append({'profile':item['profile'],'artifacts':artifacts,'build_record_sha256':sha(root/'build.json'),'log_sha256':sha(root/'build.log')})
for sub,name in [('dependencies001','fetch.json'),('bootstrap001','bootstrap.json')]:
 p=B/('release-readiness403-'+sub)/name;shutil.copyfile(p,out/name)
receipt=B/'release-readiness403-bootstrap001/toolchain.json'
r=json.loads(receipt.read_text())
result['toolchain_receipt']={'sha256':sha(receipt),'files':len(r['files']),'path':str(receipt)}
result['settings']=json.loads((K/'settings-build001.json').read_text())
assert result['settings']['exit_code']==0
result['artifact_count_with_settings']=result['artifact_count']+1
(K/'build-verification001.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'profiles':len(result['profiles']),'artifacts':result['artifact_count_with_settings'],'toolchain_files':len(r['files'])}))
