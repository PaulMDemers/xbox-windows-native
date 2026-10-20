"""Review the failed copy and clean shutdown from cached artifacts only."""
import hashlib,json,re,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn608/pc001/cold1-002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from Registry import Registry
out=K/'failure-review001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
s=read('ntfs-phase1.json');c=read('ntfs-cold1-002.json');m=read('media001.json')
assert s['closed'] and s['exit_code']==0 and c['complete'] and c['normal_shutdown_delta']==1
assert not any(s.get(n) for n in ['deadline','host_quit','host_terminate','host_kill','space_stop'])
assert c['audit_unchanged'] and c['source_unchanged']
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in c['hives'])
manifest=json.loads((P/'manifest.json').read_text())
assert not any(n.startswith('xwn608/') for n in manifest)
assert 'xwn608-kit/copy-verified.txt' not in manifest
assert 'xwn608-kit/trace608.exe' not in manifest and 'xwn608-kit/verify608.exe' not in manifest
b=read('build001.json');runner=next(r for r in b['rows'] if r['path'].endswith('/run608.exe'))
assert manifest['xwn608-kit/run608.exe']['sha256']==runner['sha256']
assets=read('asset-integrity001.json')
assert all(manifest['xwn608-kit/'+n.lower()]['sha256']==v['sha256'] for n,v in assets.items())
reg=Registry.Registry(str(P/'files/WINNT/system32/config/software'))
try:reg.open('Fish Technology Group')
except Registry.RegistryKeyNotFoundException:pass
else:raise AssertionError('unexpected game registry')
requested=re.findall(r'^copy D:\\([A-Z0-9]+\.EXE) ',m['copy_script'],re.M)
missing=[n for n in requested if n not in m['files']]
assert missing==['TRACE606.EXE'] and 'TRACE608.EXE' in m['files']
screen=Path('C:/xwn608/pc001/phase1/screen-1792472967205799475.png')
out.write_text(json.dumps(dict(review_passed=True,runtime_passed=False,cleanup_passed=True,game_launched=False,
 cause='Copy batch requests TRACE606.EXE; media contains TRACE608.EXE. Guard stops before verifier/game.',
 requested_tools=requested,missing_tools=missing,all_assets_unchanged=len(assets),
 normal_shutdown_delta=1,new_system_events=c['new_system_events'],
 screenshot_sha256=hashlib.sha256(screen.read_bytes()).hexdigest(),
 screenshot_observation='System cannot find the file specified; XWN608 COPY FAILED - DO NOT RUN GAME; pause.',
 limits='Media byte readback passed but did not validate script tool references. No game or recorder result.'),
 indent=2)+'\n')
print('608 failed copy independently explained;503 assets unchanged, no game logs/registry, normal restart')
