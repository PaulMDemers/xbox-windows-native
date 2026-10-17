"""Fresh physical six-case sprite kit; no console access or installed changes."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; old=K.parent/'key-retry449'; sprite=K.parent/'sprites444'
out=K/'source-review001.json';assert not out.exists();rows=[]
def put(name,source,s):
    p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
    if name.endswith('.py'):compile(s,str(p),'exec')
    rows.append(dict(file=name,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
def common(s):return s.replace('key-retry449','sprites-xbox451').replace('449','451')
cases="[('r04di','default','index8'),('r04si','hel','index8'),('r04d6','default','rgb565'),('r04s6','hel','rgb565'),('r04d3','default','rgb32'),('r04s3','hel','rgb32')]"
for name in ['build001.py','binary-review001.py','physical.py','observe002.py','review001.py','closeout001.py','package001.py']:
    src=old/name;s=common(src.read_text(encoding='utf-8'))
    if name=='build001.py':
        s=s.replace('key-semantics446-build001/keyprobe.exe','sprites444-build001/sprites.exe').replace('0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c','23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f')
    elif name=='physical.py':
        s=s.replace('key-depth447','sprites-depth450').replace("pc['all_semantics_passed']","pc['all_allowed_cases_passed']")
    elif name=='review001.py':
        s=s.replace('graphics_keyprobe','graphics_sprites').replace('keyprobe.exe','sprites.exe').replace('0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c','23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f')
        s=s.replace('range(2)','range(6)').replace("runner['completed_cases']=='2'","runner['completed_cases']=='6'").replace("for i,(name,backend) in enumerate([('keyd','default'),('keys','hel')]):","for i,(name,backend,fmt) in enumerate("+cases+"):")
        s=s.replace('row=dict(name=name,backend=backend,','row=dict(name=name,backend=backend,format=fmt,')
        s=s.replace("g.validate((root/(name+'.txt')).read_bytes(),(root/(name+'-source.bin')).read_bytes(),(root/(name+'-dest.bin')).read_bytes(),backend,int(code))","g.validate((root/(name+'.txt')).read_bytes(),{kind:(root/(name+'-'+kind+'.bin')).read_bytes() for kind in g.KINDS},backend,fmt,int(code))")
        s=s.replace("all(row.get('review',{}).get('semantics_passed') is True for row in r['rows'])","all(row.get('review',{}).get('passed') is True for row in r['rows'])")
    elif name=='closeout001.py':
        s=s.replace('scoped_keyprobe_passed','scoped_sprites_passed').replace("[['1280','720','32']]*2","[['1280','720','32']]*6").replace("get('captured_bytes',0)","get('exact_bytes',0)")
    elif name=='package001.py':
        s=s.replace('key-depth447','sprites-depth450').replace("review['all_semantics_passed']","review['all_allowed_cases_passed']").replace("['semantics_passed']","['full_rung04_passed']")
        s=s.replace('key-semantics446/runner.c','sprites444/runner.c').replace(".replace('xwn446','xwn451')",".replace('xwn444','xwn451')").replace("number(\"schema\",446)","number(\"schema\",444)").replace('KEYPROBE','SPRITES').replace('keyprobe','sprites').replace('actual446','actual444')
    put(name,src,s)
src=sprite/'runner.c';s=src.read_text(encoding='utf-8').replace('Owned NT5 fixture only','Owned physical Xbox Windows fixture only').replace('xwn444','xwn451').replace('number("schema",444)','number("schema",451)').replace('A:\\\\SPRITES.EXE','C:\\\\xwn451-kit\\\\sprites.exe')
put('runner.c',src,s)
src=sprite/'actual-controls001.py';s=src.read_text(encoding='utf-8')
s=s.replace("cold=json.loads((K/'ntfs-cold1-002.json').read_text());root=Path(cold['private_path'])/'files/xwn444'", "def hostpath(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\\\','/')) if len(s)>2 and s[1]==':' else Path(s)\nc=json.loads((K/'physical001-collection.json').read_text());root=hostpath(c['files']['/E/xwn451/runner.txt']['path']).parent")
put('actual-controls001.py',src,s)
out.write_text(json.dumps(dict(passed=True,rows=rows,changes='Fresh451 namespace; exact444 six-process controller with physical source-copy path; no mode/driver/DLL/sample/oracle changes',console_access=False),indent=2)+'\n',encoding='utf-8')
print('451 physical kit prepared; not built, staged or launched.')
