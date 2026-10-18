"""Create new501 sources without changing any executed497/498/499/500 input."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;A=K.parent/'d3d-scene497';C=K.parent/'entry-control500'
assert not (K/'runner.c').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
def source(p):inputs[str(p)]=sha(p);return p.read_bytes()
def put(n,b):assert not (K/n).exists();(K/n).write_bytes(b)
put('runner.c',source(A/'runner.c').replace(b'497',b'501'))
for n in ['decode.py','primary_decode.py','witness_decode.py','receipts.py','legacy_refusal_decode.py','failure_marker.py']:
 put(n,source(A/n))
put('entry_decode.py',source(K.parent/'entry-receipt498/decode.py'))
put('launcher-input.json',source(K.parent/'entry-launch499/build001.json'))
b=source(A/'physical.py').replace(b'497',b'501')
b=b.replace(b"REMOTE='/E/Applications/XWNBoot501a';BUILD=Path('C:/xwn501/build002/default.xbe')",b"REMOTE='/E/Applications/XWNBoot499a';BUILD=Path('C:/xwn499/build001/default.xbe')")
b=b.replace(b'XWNBoot501a',b'XWNBoot499a')
b=b.replace(b"from decode import decode as decode_context",b"from decode import decode as decode_context\nfrom entry_decode import decode as decode_entry")
b=b.replace(b"K/'build002.json'",b"K/'launcher-input.json'")
# Exact500 bounded fixed-receipt read functions; classifier uses the copied decoder.
c=source(C/'physical.py')
lo=c.index(b'def listing(f):');hi=c.index(b'def stage():',lo)
helpers=c[lo:hi].replace(b'D.decode(data)',b'decode_entry(data)')
anchor=b'def stage():\n';assert b.count(anchor)==1
b=b.replace(anchor,b"RECEIPTS=('entry.bin','report.bin','refusal.bin','handoff.bin','context.bin')\n"+helpers+anchor)
# Intent and candidate references are explicit; the native499 cookie stays498/490.
b=b.replace(b'496 matched XYZ texture depth sample; inherited490 read-only CPU capture; diagnostic intervention',b'496 matched scene plus499 early entry witness; diagnostic intervention')
anchor=b"  assert get(f,REMOTE+'/report.bin',True) is None\n";assert b.count(anchor)==1
b=b.replace(anchor,b"  assert set(listing(f))=={'owner.json','default.xbe'}\n"+anchor)
# Stop observation on a recovered early entry even if preparation never produced report.
anchor=b"   with connect(timeout=3) as f:b=get(f,REMOTE+'/report.bin',True)\n"
assert b.count(anchor)==1
b=b.replace(anchor,b"   with connect(timeout=3) as f:\n    rows=listing(f);early=receipt(f,'entry.bin',rows);b=receipt(f,'report.bin',rows)\n   if early is not None:\n    r['entry_file']=keep(P/'observed',REMOTE+'/entry.bin',early);r['entry']=classify(early)\n")
b=b.replace(b'   if b is not None:\n',b'   if b is not None or early is not None:\n')
b=b.replace(b"    r['report']=keep(P/'observed',REMOTE+'/report.bin',b)\n    try:r['decoded']=decode(b)\n    except ValueError as e:r['decode_error']=str(e)\n",b"    if b is not None:\n     r['report']=keep(P/'observed',REMOTE+'/report.bin',b)\n     try:r['decoded']=decode(b)\n     except ValueError as e:r['decode_error']=str(e)\n")
# Read known receipts through listing+cap on each paired read; other files retain old reader.
anchor=b"    first=get(reader,path,True);second=get(reader,path,True)\n";assert b.count(anchor)==1
b=b.replace(anchor,b"    if path.startswith(REMOTE+'/') and path.rsplit('/',1)[1] in RECEIPTS:\n     name=path.rsplit('/',1)[1];first=receipt(reader,name,listing(reader));second=receipt(reader,name,listing(reader))\n    else:first=get(reader,path,True);second=get(reader,path,True)\n")
b=b.replace(b"+[REMOTE+'/report.bin',REMOTE+'/refusal.bin',REMOTE+'/handoff.bin',REMOTE+'/context.bin']:",b"+[REMOTE+'/'+name for name in RECEIPTS]:")
anchor=b"  b=r['files'].get(REMOTE+'/report.bin')\n";assert b.count(anchor)==1
b=b.replace(anchor,b"  entry=r['files'].get(REMOTE+'/entry.bin');r['entry']=classify(None if entry is None else Path(entry['path']).read_bytes())\n"+anchor)
put('physical.py',b)
for n in ['actual-context001.py','module-read001.py','actual-controls001.py','physical-closeout001.py','imports001.py']:
 b=source(A/n).replace(b'497',b'501').replace(b'XWNBoot501a',b'XWNBoot499a').replace(b"K/'build002.json'",b"K/'launcher-input.json'")
 if n=='imports001.py':b=b.replace(b"Path('C:/xwn501/build002/default.xbe')",b"Path('C:/xwn499/build001/default.xbe')")
 put(n,b)
b=source(C/'supervise002.py').replace(b'xwn500',b'xwn501').replace(b"atomic500",b"atomic501")
b=b.replace(b'LIMITS=dict(stage=180,launch=90,observe=240,collect=240)',b'LIMITS=dict(stage=240,launch=120,observe=540,collect=300)')
put('supervise.py',b)
(K/'source-derivation001.json').write_bytes((json.dumps(dict(inputs=inputs,files={p.name:sha(p) for p in K.iterdir() if p.is_file()},originals_unchanged=all(sha(Path(p))==h for p,h in inputs.items())),indent=2)+'\n').encode())
