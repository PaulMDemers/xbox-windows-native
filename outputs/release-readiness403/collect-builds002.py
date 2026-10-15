"""Complete read-only collection after001 expected fetch.json instead of report.json."""
import hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native')
out=K/'compiled-records001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'profiles':[],'artifact_count':0,'scope':'Fresh builds, not guest validation of these binaries','prior_collection_failure':'collect-builds001 completed eight record copies then expected fetch.json; actual investigation receipt is report.json. No build repeated.'}
for item in json.loads((K/'build-batch001.json').read_text()):
 assert item['exit_code']==0
 root=Path(item['output']);dest=out/item['profile']
 for name in ['source.json','build.json','build-command.json']:assert sha(root/name)==sha(dest/name)
 record=json.loads((root/'build.json').read_text());artifacts=[]
 for entry in record['artifacts']:
  p=root/'artifacts'/entry['file'];assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes'];artifacts.append(entry)
 assert record['source']['reference_match'] and not record['source']['changed_sources']
 result['artifact_count']+=len(artifacts)
 result['profiles'].append({'profile':item['profile'],'artifacts':artifacts,'build_record_sha256':sha(root/'build.json'),'log_sha256':sha(root/'build.log'),'warning_lines':sum('warning:' in line.lower() for line in (root/'build.log').read_text(errors='replace').splitlines())})
for sub,name,target in [('dependencies001','report.json','fetch-investigation001.json'),('bootstrap001','bootstrap.json','bootstrap.json')]:
 p=B/('release-readiness403-'+sub)/name
 assert not (out/target).exists();shutil.copyfile(p,out/target)
receipt=B/'release-readiness403-bootstrap001/toolchain.json';r=json.loads(receipt.read_text())
result['toolchain_receipt']={'sha256':sha(receipt),'files':len(r['files']),'path':str(receipt)}
result['settings']=json.loads((K/'settings-build001.json').read_text());assert result['settings']['exit_code']==0
result['artifact_count_with_settings']=result['artifact_count']+1
with (K/'build-verification002.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps({'profiles':len(result['profiles']),'artifacts':result['artifact_count_with_settings'],'toolchain_files':len(r['files'])}))
