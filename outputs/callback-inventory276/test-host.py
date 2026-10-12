"""Compile the exact getter and test publication plus independent transport rejection."""
import hashlib,json,subprocess,re
from pathlib import Path
from decode import decode
k=Path(__file__).resolve().parent;out=Path('E:/Codex-archive/xbox-windows-native/callback276-host001');out.mkdir(exist_ok=False)
dest=k/'host-tests001.json';assert not dest.exists()
for n in ['inventory.c','test.c','test-host.py','decode.py','patch-renderer.py']:(out/n).write_bytes((k/n).read_bytes())
(out/'actual-test.c').write_text((k/'test.c').read_text().replace('/* ACTUAL_GETTER */',(k/'inventory.c').read_text()))
base='/mnt/e/Codex-archive/xbox-windows-native/callback276-host001'
r=dict(passed=False,guest_executed=False,scope='Exact getter and serializer with modeled persistent QEMU structs/CPU metadata; real pthread release/acquire publication, no live GL or QEMU job')
try:
    p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
    r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
    p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test',base+'/actual.txt'],capture_output=True,timeout=60)
    r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0
    text=(out/'actual.txt').read_text();decoded=decode(text);assert len(decoded['callbacks'])==256
    mutants=[text.replace('available=1','available=0'),text.replace('state=6','state=5'),text.replace('count=256','count=257'),text.replace('cpu_reason=0','cpu_reason=5'),text.replace('epoch=1','epoch=2'),text.replace('thread=8','thread=7'),text.replace('native_grant=0','native_grant=1'),text[:text.index(' c255=')],text+text[text.index(' c255='):]]
    for i in [0,127,255]:
        match=re.search(r' c'+str(i)+r'=([0-9:]+)',text);values=list(map(int,match[1].split(':')))
        for col,value in [(0,0),(1,0x4000000),(2,0),(3,0),(4,0),(5,0),(6,0xffffffffffffffff)]:
            changed=values.copy();changed[col]=value;mutants.append(text[:match.start(1)]+':'.join(map(str,changed))+text[match.end(1):])
    for m in mutants:
        try:decode(m)
        except (AssertionError,KeyError):pass
        else:raise AssertionError('Malformed inventory accepted')
    r.update(passed=True,independent_rows_decoded=256,mutations_rejected=len(mutants))
except BaseException as e:r['error']=repr(e)
r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({x:y for x,y in r.items() if x!='files'},indent=2));assert r['passed']
