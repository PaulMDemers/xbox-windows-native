"""Reconstruct all eight full trees using only the extracted public-source candidate."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
export=Path('/mnt/c/xwn403/source-review002/source')
out=Path('/home/paul/xbox-windows-native/release-readiness403-export001')
sys.path.insert(0,str(export/'tools'));from build_space import require_space
space=require_space(out);out.mkdir(exist_ok=False)
manifest=json.loads((export/'SOURCE-MANIFEST.json').read_text())
for name,row in manifest['files'].items():assert hashlib.sha256((export/name).read_bytes()).hexdigest()==row['sha256']
result={'space':space,'profiles':[],'export_entries':len(manifest['files']),'scope':'Full source-tree reconstruction from the extracted review ZIP inputs; no repeated compilation or guest'}
deps=Path('/home/paul/xbox-windows-native/release-readiness403-dependencies002')
fetch=json.loads((deps/'fetch.json').read_text());assert fetch['anonymous']
for profile in json.loads((export/'upstream/components.json').read_text())['profiles']:
 name=profile['name'];command=['python3','-B',str(export/'tools/xwn.py'),'source','--profile',name,'--cache',str(deps/profile['upstream']),'--output',str(out/name)]
 with (out/(name+'.log')).open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
 row=json.loads((out/name/'source.json').read_text());assert row['reference_match'] and not row['changed_sources'];result['profiles'].append(row)
 print(name,row['tree'],flush=True)
with (K/'export-verification001.json').open('x') as f:json.dump(result,f,indent=2)
with (K/'dependency-fetch002.json').open('x') as f:json.dump(fetch,f,indent=2)
