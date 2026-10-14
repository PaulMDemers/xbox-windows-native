import json,hashlib,shutil
from pathlib import Path
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
kit=root/'outputs/public-layout402'
manifest=json.loads((root/'upstream/components.json').read_text())
records=[]
for p in manifest['profiles']:
    work=Path('/home/paul/xbox-windows-native/build')/('public-layout402-'+p['name']+'001')
    record=json.loads((work/'build.json').read_text())
    assert record['source']['reference_match'] and record['source']['tree']==p['reference_tree']
    for a in record['artifacts']:
        assert hashlib.sha256((work/'artifacts'/a['file']).read_bytes()).hexdigest()==a['sha256']
    for name in ['build.json','source.json','build-command.json']:
        shutil.copyfile(work/name,kit/(p['name']+'-'+name))
    records.append(record)
result={'profiles':records,'six_complete_source_trees_exact':True,'all_six_compiled':True,'artifact_count':sum(len(r['artifacts']) for r in records),'scope':'Fresh compiler validation with pinned tools, no guest or deployment; binary reproducibility not asserted'}
(kit/'build-verification001.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'profiles':len(records),'artifacts':result['artifact_count']}))
