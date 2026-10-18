"""MIT. Offline join of live module reports to paired cold captures; no network."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if sys.platform!='win32' and len(s)>2 and s[1]==':' else Path(s)
out=K/'module-review001.json';assert not out.exists()
c=read(K/'collection001.json');v=read(K/'runtime-review001.json');q=read(K/'package001.json')
assert c['completed'] and c['hook_removed'] and v['all_allowed_cases_passed']
rows=[]
for case in v['rows']:
    modules=[]
    for j,name in enumerate(case['review']['modules']):
        low=name.lower()
        if low=='c:\\xwn545\\d3d.exe':remote='/E/xwn545/d3d.exe';expected=q['files']['d3d.exe']['sha256']
        else:
            assert low.startswith('c:\\winnt\\system32\\') and low.count('\\')==3
            n=low.rsplit('\\',1)[-1];assert n in q['runtime_module_pins'];remote='/E/winnt/system32/'+n;expected=q['runtime_module_pins'][n]
        row=c['files'][remote];p=host(row['path']);assert sha(p)==row['sha256']==expected
        assert p.stat().st_size==row['bytes']
        pe=pefile.PE(str(p));size=pe.OPTIONAL_HEADER.SizeOfImage;assert size==int(case['fields'][f'module{j}.bytes'])
        modules.append(dict(runtime_path=name,cold_path=str(p),sha256=expected,file_bytes=row['bytes'],image_bytes=size))
    rows.append(dict(case=case['name'],modules=modules))
out.write_text(json.dumps(dict(passed=True,rows=rows,physical_access=False,scope='Actual live reports joined to already paired cold module captures and prelaunch pins; no recollection or unloaded-module trace.'),indent=2)+'\n',encoding='utf-8')
print('PASS live/cold module match:',[len(r['modules']) for r in rows])
