"""Cold physical Welcome/preferences evidence; no network or console writes."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
from Registry import Registry
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'welcome-review001.json';assert not out.exists()
before=read(K/'stage002.json');after=read(K/'collection001.json')
assert before['completed'] and after['completed'] and after['hook_removed']
profile='/E/documents and settings/Win2K/NTUSER.DAT'
welcome='/E/winnt/welcome.exe';show=[];clean=[]
for rows in [before['before'],after['files']]:
    row=rows[profile];p=Path(row['path']);assert sha(p)==row['sha256']
    data=p.read_bytes();seq=struct.unpack_from('<II',data,4)
    clean.append(data[:4]==b'regf' and seq[0]==seq[1])
    show.append(Registry.Registry(str(p)).open('Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\tips').value('Show').value())
    assert sha(rows[welcome]['path'])==rows[welcome]['sha256']
logrow=after['files'].get('/E/xwn593/runner.txt')
log=''
if logrow:
    assert sha(logrow['path'])==logrow['sha256'];log=Path(logrow['path']).read_text()
checks=dict(user_hive_headers_clean=all(clean),welcome_preference_unchanged=show[0]==show[1],
            welcome_executable_unchanged=before['before'][welcome]['sha256']==after['files'][welcome]['sha256'],
            no_pc_injection='pc_welcome_injected_pid=' not in log,
            no_pc_sentinel_staged=not any(n.lower().endswith('/inject-late-welcome.flag') for n in before['staged']))
r=dict(passed=all(checks.values()),checks=checks,show_before_after=show,
       normal_close_count=log.count('welcome_close_posted=1\n'),
       blocker_logs=[n for n in log.splitlines() if n.startswith('blocker ')],
       source_sha256=sha(__file__),console_writes=False,
       limits='Cold preference/header and executable comparison; does not prove full user-hive integrity or game input behavior. Absence of a marker is not a general audit of arbitrary window actions; scoped close logic is pinned separately.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(checks));assert r['passed']
