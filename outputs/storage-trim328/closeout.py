"""Verify cleanup receipts and retained paths; do not repeat archival or pruning."""
import ast,hashlib,json,shutil,ntpath
from datetime import datetime,timezone
from pathlib import Path
k=Path(__file__).resolve().parent;private=Path('E:/xwn328')
assert (private/'remaining-complete001.json').exists()
dest=k/'result.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
man=[];bydrive={'C':0,'E':0};counts={}
for num,wanted in [('001',385),('002',49)]:
    latest={}
    for line in (private/('archive-journal'+num+'.jsonl')).read_text(encoding='utf-8-sig').splitlines():
        row=json.loads(line);latest[row['source']]=row
    assert len(latest)==wanted
    for row in latest.values():
        src=Path(row['source']);archive=Path(row['archive']);assert row['roundtrip_verified'] and row['source_removed']
        assert not src.exists() and archive.is_file() and archive.stat().st_size==row['archive_bytes']
        receipt=json.loads(Path(str(src)+'.archived328.json').read_text(encoding='utf-8-sig'))
        assert receipt==row
        bydrive[src.drive[0].upper()]+=row['original_bytes']-row['archive_bytes'];man.append(row)
    counts[num]=len(latest)
pruned=[json.loads(line) for line in (private/'prune-journal001.jsonl').read_text(encoding='utf-8-sig').splitlines()]
assert len(pruned)==66
for row in pruned:
    assert row['removed'] and not Path(row['target']).exists()
    if 'canonical' in row:assert Path(row['canonical']).is_file() and Path(row['canonical']).stat().st_size==row['bytes']
    bydrive[Path(row['target']).drive[0].upper()]+=row['bytes']
# Retained known recovery archives and newest probe inputs were not pruning targets.
inventory=json.loads((private/'inventory001.json').read_text())
def norm(p):
    p=p.replace('\\','/')
    if p.startswith('/mnt/c/'):p='C:'+p[6:]
    elif p.startswith('/mnt/e/'):p='E:'+p[6:]
    return ntpath.normpath(p).lower()
links=sorted([(norm(v['path']),norm(v['target'])) for v in inventory['links']],key=lambda v:len(v[0]),reverse=True)
def resolve(p):
    p=norm(p)
    for source,target in links:
        if p==source or p.startswith(source+'\\'):return target+p[len(source):]
    return p
parents=set()
for row in json.loads((private/'qcow-dependencies.json').read_text()):
    if backing:=row.get('backing'):
        absolute=backing.startswith('/mnt/') or (len(backing)>1 and backing[1]==':')
        parents.add(resolve(backing if absolute else ntpath.join(ntpath.dirname(row['path']),backing)))
parents.add(resolve('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5/artifacts/windows2000-pc-base.qcow2'))
assert not parents.intersection(resolve(v['source']) for v in man)
retained_parents=0
for row in inventory['files']:
    if norm(row['path']) in parents:
        p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'];retained_parents+=1
recovery=[]
for row in inventory['files']:
    s=row['path'].replace('\\','/').lower()
    if ('/0.1.0/' in s or '/demo256-audio004-video118-20261011/' in s) and s.endswith('.zip'):
        p=Path(row['path']);assert p.exists() and p.stat().st_size==row['bytes'];recovery.append(row['path'])
probe=json.loads((k.parent/'hd-large327/final-review.json').read_text())
for name,row in probe['private_files'].items():assert sha(Path(name))==row['sha256']
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
(k/'archive-manifest.json').write_text(json.dumps(man,indent=2)+'\n')
(k/'prune-manifest.json').write_text(json.dumps(pruned,indent=2)+'\n')
r={'utc':datetime.now(timezone.utc).isoformat(),'completed':True,'archive_passes':counts,'archived_files':len(man),
   'loose_cpu_traces_removed':308,'loose_leaf_disk_images_removed':126,'duplicate_executables_removed':64,
   'downloaded_installers_removed':2,'verified_logical_bytes_saved_by_drive':bydrive,
   'verified_logical_bytes_saved_total':sum(bydrive.values()),
   'free_bytes':{d:shutil.disk_usage(d+':/').free for d in ['C','E']},
   'roundtrip_verification':'Every archive fully decompressed and matched to original SHA256 before source removal; one separate restore-file.py test also passed',
   'backing_chains_rebased_or_moved':False,'physical_console_access':False,'source_or_sdk_removed':False,
   'inventoried_backing_parents_still_present_with_original_lengths':retained_parents,
   'retained_recovery_zips':recovery,'newest327_private_inputs_unchanged':True,
   'limitations':['Original paths for archived files require explicit restoration before old audits or disk use.',
                 'Sparse Linux raw disk logical lengths were not treated as allocated bytes; other project disks left untouched.',
                 'Historical D: release/runtime paths not found on inventoried C:/E:; no claim those absent files were preserved or currently available.'],
   'source_hashes':{p.name:sha(p) for p in sorted(k.iterdir()) if p.is_file() and p.name!='result.json'}}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({v:r[v] for v in ['completed','archived_files','verified_logical_bytes_saved_total','free_bytes']}))
