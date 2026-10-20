"""Independent user-profile hive audit on retained physical before/after bytes."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'user-hive-audit001.json';assert not out.exists()
before=read(K/'stage001.json');after=read(K/'collection001.json')
assert before['completed'] and after['completed'] and after['hook_removed']
n='/E/documents and settings/Win2K/NTUSER.DAT';rows={}
for phase,group in [('before',before['before']),('after',after['files'])]:
    row=group[n];p=host(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
    rows[phase]=audit(p)
passed=all(r['clean'] and r['header_valid'] and r['independent_raw_values_agree'] for r in rows.values())
out.write_text(json.dumps(dict(passed=passed,hives=rows,source_sha256=sha(__file__),console_writes=False),indent=2)+'\n')
print('Physical user-hive audit',passed);assert passed
