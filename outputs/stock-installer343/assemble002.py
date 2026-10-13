"""Assemble twice from separately reconstructed payloads; no console access."""
import hashlib,json,sys,zipfile
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'tools'))
from stock_e import info,load,layout,Package
P=Path('E:/xwn343');out=P/'bundle002';assert not out.exists();out.mkdir()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def original(p):return '/F/'+p[3:] if not p.startswith('/E/Applications/') else p.replace('/XWNEBoot/','/XWNFBoot/')
a=load(K/'package001.json');b=load(K/'package002.json');old=load(W/'outputs/stock-physical337/package001.json')
assert a['files']==b['files']==old['files'] and a['changes']==b['changes']==old['changes']
assert a['directories']==b['directories']==old['directories'] and len(a['files'])==6566
c=load(W/'outputs/stock-physical337/capture001.json');review=load(W/'outputs/stock-physical337/capture-review001.json')
bycase={p.lower():p for p in c['files']}
baseline={bycase[p.lower()]:c['files'][bycase[p.lower()]] for p in review['baseline_files']}
for name in ['system','software','default','sam','security']:
    p='/F/winnt/system32/config/'+name;baseline[p]=c['files'][p]
assert len(baseline)==31 and all(not p.startswith('/C/') for p in baseline)
plan={p:dict(target_before='MUST_BE_ABSENT',origin=original(p),origin_metadata=c['files'][original(p)],installed=v) for p,v in a['files'].items()}
support={'support/INSTALL-PLAN.json':encoded(plan),'support/USAGE.md':(K/'USAGE.md').read_bytes(),
         'support/capacity.xbe':Path('E:/xwn343/capacity-build001/bin/default.xbe').read_bytes()}
assert info(support['support/capacity.xbe'])['sha256']=='fd232843c60636ae14e91096f87ddb884c4329ea0ec3aba8b72cf77bd21ecc7a'
for p in a['changes']:
    q=original(p);data=(Path('E:/xwn337/capture001')/q.lstrip('/')).read_bytes();assert info(data)==c['files'][q]
    support['support/rollback'+q]=data
for name in ['package-stock-e.py','install-stock-e.py','stock_e.py','hd_overlay.py']:
    support['support/tools/'+name]=(W/'tools'/name).read_bytes()
m=dict(version=1,profile='stock-e-1080i',files=a['files'],directories=a['directories'],baseline=baseline,
       support={p:info(data) for p,data in support.items()},changes=a['changes'],hive_semantic_changes=a['hive_semantic_changes'],
       provenance=dict(capture_sha256=a['capture_sha256'],hd_archive_sha256=a['archive_sha256'],physical_payload='stock-boot342',
                       compiled_from_scratch=False,payload_reconstructed_twice=True),
       qualification=dict(physical_drawing_audio_api_integrity=True,combined=False,strict=False,
                          failures=['Srv2013 dashboard C warning; C not queried or changed','Ftdisk49 crash-dump configuration'],
                          fresh_installer_physical_install_tested=False),
       limits='Private same-console F-to-E migration. Requires owned repo/ticket/F marker and exact F rollback baseline. Not generic fresh-console provisioning, not a new release. Xbox C forbidden.')
layout(m);raw=encoded(m);assert len(raw)<=2*1024**2
policy=W/'tools/stock-e-profile.json';assert not policy.exists();policy.write_bytes(encoded(dict(profile=m['profile'],manifest_sha256=info(raw)['sha256'])))
report=dict(passed=False,payload_reconstruction_exact=True,exact_physical337_payload=True,files=len(a['files']),logical_bytes=sum(v['bytes'] for v in a['files'].values()),archives=[],physical_access=False)
for n in [1,2]:
    dest=out/('stock-e-1080i-%03d.zip'%n)
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name in sorted(['MANIFEST.json']+list(support)+['payload'+p for p in a['files']]):
            data=raw if name=='MANIFEST.json' else support[name] if name in support else (P/('package%03d'%n)/name[len('payload/'):]).read_bytes()
            if name.startswith('payload'):assert info(data)==a['files'][name[len('payload'):]]
            row=zipfile.ZipInfo(name,(1980,1,1,0,0,0));row.compress_type=zipfile.ZIP_DEFLATED;row.external_attr=0o100600<<16;row.create_system=3
            z.writestr(row,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    verified=Package(dest,policy);report['archives'].append(dict(path=str(dest),bytes=dest.stat().st_size,sha256=verified.archive_sha256,entries=len(verified.z.infolist()),allocated_bytes=verified.allocated));verified.z.close()
assert report['archives'][0]['sha256']==report['archives'][1]['sha256']
report.update(passed=True,manifest_sha256=info(raw)['sha256'],deterministic_zip=True)
(K/'assembly002.json').write_bytes(encoded(report));(out/'MANIFEST.json').write_bytes(raw)
print(json.dumps(report))
