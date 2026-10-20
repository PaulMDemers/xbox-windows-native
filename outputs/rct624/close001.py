"""Seal the original interactive control after one normal shutdown and cold audit."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn624/pc001')
sys.path.insert(0,str(W/'work/python-packages'));from Registry import Registry
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
c=read(K/'ntfs-cold1-002.json');v=read(K/'ntfs-phase1.json');assert v['closed'] and v['exit_code']==0 and not any(v.get(n) for n in ['host_quit','host_terminate','host_kill','deadline'])
assert c['complete'] and c['source_unchanged'] and c['audit_unchanged'] and c['normal_shutdown_delta']==1
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in c['hives'])
f=P/'cold1-002/files';manifest=read(P/'cold1-002/manifest.json')
def find(rel):
 matches=[p for p in f.rglob('*') if p.is_file() and p.relative_to(f).as_posix().lower()==rel];assert len(matches)==1;return matches[0]
log=find('xwn624/runner.txt').read_text();values=dict(line.split('=',1) for line in log.splitlines());assert values['launched']=='1' and values['wait']=='0' and values['game_exit']=='0' and values['registry_restored']=='1'
assert int(values['end_tick'])-int(values['start_tick'])>=180000
assert find('xwn624/subject.txt').read_bytes()==b'1'
assert values['parent_disposition']=='1' and values['key_disposition']=='1'
assert find('xwn624/registry.bin').stat().st_size==3*(12+512)
for phase in [0,1]:
 folder=P/f'cold{phase}-002/files';p=next(p for p in folder.rglob('*') if p.is_file() and p.name.lower()=='software')
 hive=Registry.Registry(str(p))
 try:hive.open('Fish Technology Group');raise AssertionError('Temporary registry tree remains')
 except Registry.RegistryKeyNotFoundException:pass
rows=read(K/'build002.json')['rows'];expected={Path(row['path']).name.lower():row for row in rows}
for name,dest in [('play624.exe','xwn624-kit/play624.exe'),('rct.exe','xwn586-kit/game/rct.exe')]:
 entry=next(v for k,v in manifest.items() if k.lower()==dest);assert entry['sha256']==expected[name]['sha256']
obs=read(K/'visual-review001.json');assert obs['passed']
r=dict(closed=True,passed=True,scope='Original stand-in process, temporary registry setup/restoration, >3-minute user-controlled lifetime, no automatic restart; not retail rendering or physical Xbox proof',launcher_sha256=expected['play624.exe']['sha256'],control_lifetime_ms=int(values['end_tick'])-int(values['start_tick']),normal_shutdown_delta=1,registry_restored=True,physical_access=False,game_included=False,processes_closed=True,failures_preserved=['build001 compiler warning','initial VM environment admission failure','blank fixture logon refusal'],pins={p.name:sha(p) for p in K.iterdir() if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n');print('624 CLOSED PASS; exact interactive launcher qualified with original control')
