"""Prepare one physical E-only boot check from exact qualified helper bytes; no FTP."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/e/xwn342/payload');assert not P.exists();P.mkdir(parents=True)
old=K.parent/'hd-large-physical331';r=json.loads((old/'package.json').read_text());helpers=[]
for row in r['helpers']:
    if row['name']=='replay.exe':continue
    data=(old/'artifacts/payload'/row['name']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];(P/row['name']).write_bytes(data);helpers.append(row)
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha
sys.path.insert(0,str(K.parent/'stock-runtime335'));from stock_io002 import readers
f=json.loads((K.parent/'stock-repeat339/emu001/fixture.json').read_text());disk=Path(f['fixture_path_linux']);assert sha(disk)==f['fixture_sha256']
with ColdIO(disk) as io:b=readers(io,disk)['E'].read('xwnstock339/replay.exe')
assert m.sha(b)=='e7372a4585ddafd5a81a179befb13745a6588b2f17ed4d6d7bddde64af4b2ab9';(P/'replay.exe').write_bytes(b);helpers.append(dict(name='replay.exe',sha256=m.sha(b),bytes=len(b),source=f['fixture_path_linux']+'!E/xwnstock339/replay.exe'))
assert json.loads((K.parent/'stock-repeat339/emu001/repeat-proof.json').read_text())['passed']
(K/'package.json').write_text(json.dumps(dict(prepared=True,helpers=helpers,physical_helper_original201=True,experimental_helper338_deployed=False,physical_writes=False),indent=2)+'\n')
# Exact established physical predicates, with E paths and small probe scope explicit.
t=(old/'audit.py').read_text().replace("remote='xwnhd331'","remote='xwnstock342'").replace("art/'F'","art/'E'").replace("prior/'F/","prior/'E/").replace("art/'F/","art/'E/")
t=t.replace("sys.path.insert(0,str(repo/'outputs/hd-large327'))\nfrom large_analysis import analyze as large_analysis\nr['large_samples']=[large_analysis(v) for v in texts]\nr['display_workload_passed'] &= all(v['passed'] for v in r['large_samples'])\n",'')
t=t.replace("offline_registry_edits='none; temporary six-file1080i chain only'","offline_registry_edits='Four MountedDevices values only in new E copy, before this run; normal startup temporarily replaced'")
t=t.replace('All six candidate files restored to incoming baseline after staged-byte capture regardless of scoped outcome.','Normal startup restored first. Installed E HD chain retained for diagnosis; original F Windows and loader untouched. Trace may be historical; this is not full disk-content or crash-dump qualification.')
(K/'audit.py').write_text(t,newline='\n')
for n in ['typed-state001.py','installed-binding001.py']:
    (K/n).write_text((old/n).read_text().replace("/'F/winnt/","/'E/winnt/"),newline='\n')
before=K/'artifacts/before001';before.mkdir(parents=True)
payload=Path('/mnt/e/xwn337/package001/E')
for path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']+['winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]:
    b=(payload/path).read_bytes();p=before/'E'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print('Physical E test prepared locally; original physical helper and normal rollback captured')
