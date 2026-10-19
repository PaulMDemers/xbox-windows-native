"""Close only the two observed, independently captured physical file-save phases."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
records={n:read(K/(n+'.json')) for n in ['before','after1','after2','audit1','audit2','observer1','observer2','launch1','launch2','phase1-review']}
for n in ['before','after1','after2']:
 r=records[n];assert r['completed'] and r['ordinary_code_exact']
 assert not r['remote_writes'] and not r['temporary_hook_installed'] and not r['console_C_accessed']
 for path,row in r['files'].items():
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],path
for ordinal in (1,2):
 a=records[f'audit{ordinal}'];o=records[f'observer{ordinal}'];l=records[f'launch{ordinal}']
 assert a['closed'] and a['hives_clean'] and a['ordinary_code_exact']
 assert a['events']['system']['normal_shutdown_delta']==1
 assert o['normal_restart_reported'] and o['at_dashboard'] and not o['manual_reset_reported']
 assert l['requested'] and l['reply'].startswith('200') and not l['automatic_retry_allowed']
assert records['observer1']['saved_and_reopened_reported']
assert records['observer2']['saved_text_reopened_after_boot_reported']
assert records['phase1-review']['passed'] and records['audit2']['saved_bytes_unchanged']
saved='/E/xwn588.txt';assert saved not in records['before']['files']
rows=[records[n]['files'][saved] for n in ('after1','after2')]
assert all(Path(row['path']).read_bytes()==b'Xbox save test 588' for row in rows)
assert rows[0]['sha256']==rows[1]['sha256']
assert not (K/'launch3.json').exists()
r=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 scope='Original physical Xbox: new Notepad file saved/reopened, normal Restart, reopened after second boot, another normal Restart; paired cold byte readbacks.',
 launches=2,normal_shutdown_deltas=[1,1],saved_bytes=rows[0]['bytes'],saved_sha256=rows[0]['sha256'],
 exact_text='Xbox save test 588',saved_file_left_on_console=saved,
 hives_clean=True,protected_720p_and_ordinary_startup_unchanged=True,
 no_temporary_hook=True,no_owned_host_job_left=True,console_last_observed='dashboard FTP during after2 capture; user also reports dashboard',
 event_findings={n:{k:[{'source':e['source'],'event_id':e['event_id']} for e in v['new_records']] for k,v in records[n]['events'].items()} for n in ('audit1','audit2')},
 receipt_sha256={n:sha(K/(n+'.json')) for n in records},
 limitations=['No full FATX allocation audit or paging-health qualification.',
 'Ftdisk49 and Srv2013 retained; no warning was suppressed.',
 'This is not RCT save/load, another-console compatibility, boot reliability statistics or GPU qualification.',
 'First audit invocation import failure and pre-execution source-review correction are preserved.'],
 automation='PAUSED',next='Hardware inventory and watched package boot on another Xbox when available; no third launch of588.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['closed','passed','launches','normal_shutdown_deltas','saved_bytes','saved_sha256']}))
