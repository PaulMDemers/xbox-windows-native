"""Create a private verified staging overlay; never deploy, tag or publish."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=Path('D:/Codex-archive/xbox-windows-native/hd-staging325')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
assert not out.exists() and not (k/'bundle.json').exists()
a=read(ws/'outputs/hd-observed315/final-review.json');b=read(ws/'outputs/hd-physical324/final-review.json')
assert a['scoped_passed'] and b['scoped_passed'] and a['integrity_passed'] and b['integrity_passed']
assert b['normal_shutdown_count']==1 and all(b['restored_payloads'].values())
assert not b['release_qualified']
profiles={'720p':read(ws/'outputs/hd-observed315/package.json')['video'],'1080i':read(ws/'outputs/hd-physical324/package.json')['video']}
assert len(profiles['720p'])==len(profiles['1080i'])==6
assert {r['path'] for r in profiles['720p']}=={r['path'] for r in profiles['1080i']}
assert [x['path'] for x,y in zip(profiles['720p'],profiles['1080i']) if x['sha256']!=y['sha256']]==['/E/Applications/XWNFBoot/default.xbe']
capture=read(ws/'outputs/hd-physical324/capture001.json');payload={};manifest={}
for mode,rows in profiles.items():
    for r in rows:
        p=Path(r['source']);data=p.read_bytes();assert sha(data)==r['sha256'] and len(data)==r['bytes']
        name=mode+r['path'];assert '..' not in Path(name).parts;payload[name]=data
for r in profiles['1080i']:
    data=(ws/'outputs/hd-physical324/artifacts/before001'/r['path'].lstrip('/')).read_bytes()
    assert sha(data)==capture['files'][r['path']]['sha256'];payload['baseline-restore'+r['path']]=data
for name,data in payload.items():manifest[name]={'bytes':len(data),'sha256':sha(data)}
recovery=read(ws/'outputs/demo-audio-level256/capture-summary.json')
for row in recovery['bundles']:
    p=Path(row['path']);assert p.stat().st_size==row['bytes'] and file_sha(p)==row['sha256']
base={path:r for path,r in capture['files'].items() if path in {v['path'] for v in profiles['1080i']} or path.endswith(('/drivers/xwnfatx.sys','/drivers/xwnaci207.sys','/hal.dll','/xwnsetup.cmd'))}
qualification={'staging_only':True,'release_tag_created':False,'physical720p_workload_passed':True,'physical1080i_workload_passed':True,'physical1080i_visual_observation':read(ws/'outputs/hd-physical324/user-observation.json'),'strict_passed':b['strict_passed'],'known_Ftdisk49_retained':any(v['source']=='Ftdisk' and v['event_id']==49 for group in b['new_events'].values() for v in group),'gpu_acceleration':False,'full_system_snapshot_included':False,'full_restore_tested':False,'physical324_report_sha256':file_sha(ws/'outputs/hd-physical324/final-review.json')}
meta={'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ws,text=True).strip(),'builder_sha256':file_sha(Path(__file__)),'usage_sha256':file_sha(k/'USAGE.md'),'files':manifest,'installed_prerequisite_files':base,'existing_private_recovery':recovery['bundles'],'target':'Existing qualified Conexant HDTV demo; no universal installation claim'}
payload['USAGE.md']=(k/'USAGE.md').read_bytes();payload['MANIFEST.json']=(json.dumps(meta,indent=2)+'\n').encode();payload['QUALIFICATION.json']=(json.dumps(qualification,indent=2)+'\n').encode()
out.mkdir(parents=True);z=out/'xwn-hd-staging325.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as f:
    for name,data in sorted(payload.items()):
        info=zipfile.ZipInfo(name,date_time=(2026,10,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;f.writestr(info,data)
with zipfile.ZipFile(z) as f:
    assert f.testzip() is None and len(f.infolist())==len(payload)
    for name,data in payload.items():assert f.read(name)==data
result={'completed':True,'staging_only':True,'path':str(z),'bytes':z.stat().st_size,'sha256':file_sha(z),'entries':len(payload),'all_entries_readback_verified':True,'physical_writes':False,'release_tag_created':False,'qualification':qualification,'manifest':meta}
(out/'bundle.json').write_text(json.dumps(result,indent=2)+'\n');(k/'bundle.json').write_text(json.dumps(result,indent=2)+'\n');print({n:result[n] for n in ['path','bytes','sha256','entries','staging_only']})
