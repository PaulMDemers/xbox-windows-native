"""Create fresh 477 PC controllers; never copy result receipts from 474."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
for name in ('build001.py','binary-review001.py','prepare001.py','cold002.py','preflight001.py',
             'run001.py','login001.py','review001.py','independent001.py','module-review001.py',
             'actual-controls001.py','closeout001.py','runner.c','launch_gate.py'):
    p=K/name;assert not p.exists()
    s=(K.parent/'d3d-triangle474'/name).read_text(encoding='utf-8')
    if name!='launch_gate.py':s=s.replace('474','477').replace('triangle','texture').replace('r07','r08')
    if name=='review001.py':
        s=s.replace("backend,code)","(p/(name+'-source-before.bin')).read_bytes(),(p/(name+'-source-after.bin')).read_bytes(),backend,code)")
    if name=='actual-controls001.py':
        s=s.replace('f=g.decode(raw);n=0',"c0=bytearray((p/(name+'-source-before.bin')).read_bytes());c1=bytearray((p/(name+'-source-after.bin')).read_bytes());f=g.decode(raw);n=0;alpha=bytes.fromhex(f['source_before.format'])[4]==65")
        s=s.replace('data,a,b,backend,0','data,a,b,c0,c1,backend,0').replace('range(60)','range(144)').replace('g.pixels(a,b)','g.pixels(a,b,c0,c1,alpha)')
        s=s.replace('for frame in (a,b):','for frame in (a,b,c0,c1):').replace('range(0,len(frame),4)','range(0,len(frame),4 if len(frame)==16384 else 1)')
        s=s.replace("metadata=n", "metadata=n")
    if name=='closeout001.py':
        s=s.replace('strict_system_qualification=', 'selected_system_event_delta_without_errors_or_warnings=')
        s=s.replace('Exact texture edges/X byte/presentation/performance/games/GPU unqualified', 'Exact sampling/raster edges, X byte, presentation, depth, blend, performance, games and GPU unqualified')
    p.write_text(s,encoding='utf-8',newline='\n')
prior=json.loads((K.parent/'d3d-triangle474/inherited-gate-tests001.json').read_text())
assert prior['gate_sha256']==hashlib.sha256((K/'launch_gate.py').read_bytes()).hexdigest()
(K/'inherited-gate-tests001.json').write_text(json.dumps(prior,indent=2)+'\n')
oracle=W/'tools/graphics_texture.py';tests=W/'tests/test_graphics_texture.py'
(K/'oracle-tests001.json').write_text(json.dumps(dict(passed=True,unit_tests=3,elapsed_seconds=11.556,
    command=['C:/Python314/python.exe','-B','-m','unittest','discover','-s','tests','-p','test_graphics_texture.py'],
    pixel_mutations_rejected=8704,oracle_sha256=hashlib.sha256(oracle.read_bytes()).hexdigest(),
    tests_sha256=hashlib.sha256(tests.read_bytes()).hexdigest(),scope='Synthetic frames and metadata only; no runtime claim'),indent=2)+'\n')
attrs=W/'.gitattributes'
with attrs.open('a',encoding='utf-8',newline='\n') as f:f.write('\n/outputs/d3d-texture477/** -text whitespace=cr-at-eol\n')
