"""Fresh six-case sprite control with the verified447 temporary24-bit mode transaction."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; old=K.parent/'key-depth447'; sprite=K.parent/'sprites444'
out=K/'source-review001.json'; assert not out.exists()
rows=[]
def put(name,source,text):
    p=K/name; assert not p.exists(); p.write_text(text,encoding='utf-8',newline='\n')
    if name.endswith('.py'): compile(text,str(p),'exec')
    rows.append(dict(file=name,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
def common(s):
    return s.replace('key-depth447','sprites-depth450').replace('xwn447','xwn450').replace('XWN447','XWN450').replace('run447','run450')
for name in ['build001.py','binary-review001.py','prepare001.py','cold002.py','cold003.py','login001.py','run001.py','preflight001.py','mode-tests001.py']:
    src=old/name; s=common(src.read_text(encoding='utf-8'))
    if name=='build001.py':
        s=s.replace('key-semantics446-build001/keyprobe.exe','sprites444-build001/sprites.exe').replace('0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c','23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f')
    elif name=='preflight001.py':
        s=s.replace('keyprobe','sprites')
    elif name=='run001.py':
        s=s.replace('no driver or mode change','temporary enumerated24-bit mode, restored before restart')
    put(name,src,s)
for name in ['launch_gate.py','mode_receipt.py','inherited-gate-tests001.json']:
    p=K/name;assert not p.exists();p.write_bytes((old/name).read_bytes())
(K/'sample-build001.json').write_bytes((sprite/'sample-build001.json').read_bytes())
for name in ['independent001.py','actual-controls001.py','closeout001.py','review001.py']:
    src=sprite/name;s=src.read_text(encoding='utf-8').replace('sprites444','sprites-depth450').replace('xwn444','xwn450')
    if name=='review001.py':
        s=s.replace("import graphics_sprites as g","import graphics_sprites as g\nfrom mode_receipt import validate_mode")
        s=s.replace("runner['schema']=='444'","runner['schema']=='450'")
        s=s.replace('record=dict(runner=runner,','mode_review=validate_mode(runner)\nrecord=dict(mode_review=mode_review,runner=runner,')
        s=s.replace("row=dict(name=name,format=fmt", "assert [fields[k] for k in ('mode.width','mode.height','mode.bpp')]==['640','480','24']\n row=dict(name=name,format=fmt")
        s=s.replace("out.write_text(json.dumps(record,indent=2)+'\\n')", "admission=json.loads((K/'launch-admission001.json').read_text());assert admission['preflight_finished_ns']<=admission['validated_ns']\nrecord['launch_admission']=admission\nout.write_text(json.dumps(record,indent=2)+'\\n')")
        s=s.replace("print(json.dumps({k:record[k] for k in ('all_allowed_cases_passed','rows')}))", "print(json.dumps(dict(passed=record['all_allowed_cases_passed'],rows=[dict(name=r['name'],exit=r['process_exit'],error=r.get('review_failure'),bytes=r.get('review',{}).get('exact_bytes')) for r in record['rows']])))")
    put(name,src,s)
s=common((old/'runner.c').read_text(encoding='utf-8')).replace('number("schema",447)','number("schema",450)')
s=s.replace('Two isolated','Six isolated').replace('KEYPROBE','SPRITES').replace('keyprobe','sprites').replace('i<2','i<6').replace('completed==2','completed==6')
s=s.replace('"default keyd","hel keys"','"default index8 r04di","hel index8 r04si","default rgb565 r04d6","hel rgb565 r04s6","default rgb32 r04d3","hel rgb32 r04s3"').replace('"keyd","keys"','"r04di","r04si","r04d6","r04s6","r04d3","r04s3"')
put('runner.c',old/'runner.c',s)
start=s.index('static void mode_fields(');end=s.index('void WINAPI mainCRTStartup(')
oldmode=(old/'runner.c').read_text(encoding='utf-8');oldmode=oldmode[oldmode.index('static void mode_fields('):oldmode.index('void WINAPI mainCRTStartup(')]
assert s[start:end]==oldmode
stripped=s.replace('static DEVMODEA original_mode,requested_mode,observed_mode;\nstatic int mode_changed,mode_restored;\n','').replace(s[start:end],'').replace('    if(!enter_mode())goto done;\n','').replace('    leave_mode();\n','').replace('completed==6&&mode_restored','completed==6').replace('xwn450','xwn444').replace('number("schema",450)','number("schema",444)')
assert stripped==(sprite/'runner.c').read_text(encoding='utf-8')
record=dict(passed=True,rows=rows,original444_controller_reconstructed=True,original447_mode_transaction_exact=True,original447_gate_exact=(K/'launch_gate.py').read_bytes()==(old/'launch_gate.py').read_bytes(),sample_unchanged=True,changes='Fresh namespace plus six original444 cases with exact447 mode enter/restore; independent parser now accepts24-bit without changing expected pixels')
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('450 kit prepared; original444 controller and447 mode transaction exactly reconstructed.')
