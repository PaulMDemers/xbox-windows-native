# SPDX-License-Identifier: MIT
"""Independent exact-source, fixture-scope and evidence review; no runtime."""
import ast,datetime,hashlib,json,shutil,struct,subprocess,traceback
from pathlib import Path
K=Path(__file__).resolve().parent;OUT=K/'review001.json';assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
js=lambda p:json.loads(p.read_bytes())
r=dict(passed=False,physical_access=False,inputs={},captures=[],private=[])
def pin(p):r['inputs'][str(p.resolve())]=sha(p)
try:
    manifest=js(K/'source-copy001.json');pin(K/'source-copy001.json')
    block=b"    for offset, expected in ((0x10c, 544096), (0x350, 540000), (0x358, 540000)):\n        if struct.unpack_from('<I', header, offset)[0] != expected or struct.unpack_from('<I', image, offset)[0] != expected:\n            raise ValueError('image or section extent')\n"
    for name,row in manifest.items():
        src=Path(row['parent']);assert sha(src)==row['parent_sha256'];expected=src.read_bytes();pin(src)
        for a,b in row['substitutions']:assert a.encode() in expected;expected=expected.replace(a.encode(),b.encode())
        if name=='trampoline.py':
            marker=b"    if struct.unpack_from('<I', header, 0x128)[0] != ENTRY:"
            assert expected.count(marker)==1;expected=expected.replace(marker,block+marker)
        assert (K/name).read_bytes()==expected and sha(K/name)==row['sha256'];pin(K/name)
    assert (K/'entry_decode.py').read_bytes()==(K.parent/'entry-observer517/entry_decode.py').read_bytes()
    for n in range(1,6):
        j=K/f'host{n:03}.json';h=js(j);assert h['passed'];pin(j);pin(K/f'host{n:03}.py')
        for field in ['sources','source_sha256']:
            if isinstance(h.get(field),dict):
                for name,v in h[field].items():assert sha(K/name)==v
        if isinstance(h.get('source_sha256'),str):assert sha(K/'trace001.py')==h['source_sha256']
    x=Path('C:/xwn520/build001/default.xbe');xbe=x.read_bytes();pin(x)
    assert len(xbe)==544096 and sha(x)=='73b3623af2694d3c803f70f49fc9c8c072df54a7010d3238358cf6576589ca13'
    build=K.parent/'entry-extent520/build001.json';pin(build);assert js(build)['sha256']==sha(x)
    for n in ['review001.json','final-review.json']:pin(K.parent/'entry-extent520'/n)
    priorfile=K.parent/'entry-observer517/emu001/trace.json';prior=js(priorfile);assert prior['passed'];pin(priorfile)
    tree=ast.parse((K/'host001.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fixture')
    code=compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'fixture-only','exec');env={'xbe':xbe};exec(code,env)
    changed=[]
    for row in prior['reads']:
        p=Path(row['private_file']);b=p.read_bytes();assert len(b)==row['bytes'] and sha(p)==row['sha256'];pin(p)
        address,after=env['fixture'](row,b);assert address==row['address'] and len(after)==len(b)
        label=row['label'];allowed=set()
        if label in ('trampoline-loaded-header','loaded-xbe-header'):
            for off,n in [(0x10c,4),(0x350,4),(0x358,4),(0x36c,20)]:allowed.update(range(off,off+n))
            for off,value in [(0x10c,544096),(0x350,540000),(0x358,540000)]:assert struct.unpack_from('<I',after,off)[0]==value
            assert struct.unpack_from('<I',after,0x128)[0]==0x11100
        elif label in ('entry-data','path'):
            assert b.count(b'XWNBoot516a')==1
            assert after==b.replace(b'XWNBoot516a',b'XWNBoot520a')
            start=b.index(b'XWNBoot516a');allowed.update(range(start,start+11))
        else:assert after==b
        offsets=[i for i,(a,z) in enumerate(zip(b,after)) if a!=z];assert set(offsets)<=allowed
        if offsets:changed.append(label)
        r['captures'].append(dict(path=str(p),label=label,address=address,bytes=len(b),original_sha256=sha(p),modeled_sha256=hashlib.sha256(after).hexdigest(),changed_offsets=offsets))
    assert changed==['trampoline-loaded-header','loaded-xbe-header','entry-data','path']
    assert len(r['captures'])==88
    for p in sorted(Path('C:/xwn522/transport001').rglob('*')):
        if p.is_file():r['private'].append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
    for case in js(K/'host005.json')['capture_cases']:
        for row in case['reads']:assert sha(Path(row['private_file']))==row['sha256']
    query='Get-CimInstance Win32_Process | Where-Object {$_.Name -match "^(xemu|qemu)"} | Select-Object ProcessId,Name | ConvertTo-Json -Compress'
    live=subprocess.check_output(['pwsh','-NoProfile','-Command',query],text=True,timeout=20).strip();assert not live,live
    q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-af','(^|/)qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
    for p in sorted(K.iterdir()):
        if p.is_file() and p.name!='review001.json':pin(p)
    r.update(passed=True,source_transforms_exact=9,decoder_byte_exact=True,retained_capture_addresses_unchanged=True,fixture_changed_labels=changed,all_owned_processes_closed=True,emulator_processes=[],new_runtime_or_hardware_proof=False,free_bytes={d:shutil.disk_usage(d+':/').free for d in ['C','E']})
except Exception:r['failure']=traceback.format_exc()
r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','source_transforms_exact','fixture_changed_labels','free_bytes'] if n in r}))
if not r['passed']:raise SystemExit(1)
