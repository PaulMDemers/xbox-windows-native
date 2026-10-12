"""Freeze unique host capsule; run actual adapter functions and independent parser."""
import hashlib,json,re,struct,subprocess,sys
from pathlib import Path
from decode import decode
k=Path(__file__).resolve().parent;out=Path('E:/Codex-archive/xbox-windows-native/lifetime273-host002');out.mkdir(exist_ok=False)
dest=k/'host-tests002.json';assert not dest.exists();sha=lambda b:hashlib.sha256(b).hexdigest()
for name in ['lifetime.h','wire.h','watch.c','adapter-test.c','test-host.py','decode.py']:(out/name).write_bytes((k/name).read_bytes())
source=(k/'watch.c').read_text()
def function(name):
    m=re.search(r'(?m)^(?:static )?(?:bool|void|unsigned) '+name+r'\([^)]*\)\s*\{',source);assert m,name
    n=m.end();depth=1
    while depth:depth+=(source[n]=='{')-(source[n]=='}');n+=1
    return source[m.start():n]
names=['pgraph_gl_reuse269_error','pgraph_gl_reuse269_seal','x269_enter','x273_terminal','x273_record','x269_bound','x269_destroying']
functions='\n'.join(function(n) for n in names)
(out/'actual-test.c').write_text((k/'adapter-test.c').read_text().replace('/* INSERT_ACTUAL_FUNCTIONS */',functions))
base='/mnt/e/Codex-archive/xbox-windows-native/lifetime273-host002'
cmd=['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/actual-test.c','-o',base+'/test']
c=subprocess.run(cmd,capture_output=True,timeout=60)
r=dict(passed=False,scope='Exact renderer adapter functions with counted GL snapshot/file-open models; actual serializer and error/seal logic. Not guest/GL coverage.',functions_sha256=sha(functions.encode()),compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'))
try:
    if not c.returncode:
        t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test',base+'/terminal.bin'],capture_output=True,timeout=60)
        r.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'))
        if not t.returncode:
            data=(out/'terminal.bin').read_bytes();result=decode(data);r['independent_parse']=result
            assert result['sequence']==1000006 and result['runs']==2
            bads=[]
            def word(offset,value):
                bad=bytearray(data);struct.pack_into('<Q',bad,offset,value);bads.append(bytes(bad))
            for field in [0,1,2,3,4,5,6,7,8,10,11,12,13,14,15]:word(field*8,struct.unpack_from('<Q',data,field*8)[0]^1)
            for i in range(4):
                for field in range(20):
                    offset=128+i*160+field*8;word(offset,struct.unpack_from('<Q',data,offset)[0]^1)
            for i in range(2):
                for field in range(8):
                    offset=768+i*64+field*8
                    value=struct.unpack_from('<Q',data,offset)[0]^1
                    if i==0 and field==5:value=1 # DEC1 belongs in reserved FREE, never a run
                    word(offset,value)
            # Truncation/trailing bytes are rejected without allocating from hostile counts.
            bads += [data[:-1],data+bytes(8),data[:128],data[:768]]
            rejected=0
            for i,bad in enumerate(bads):
                try:decode(bad)
                except (AssertionError,struct.error):rejected+=1
                else:raise AssertionError(('Accepted wire mutation',i))
            r.update(passed=True,independent_mutations_rejected=rejected,terminal_sha256=sha(data))
except BaseException as error:r.update(passed=False,error=repr(error))
r['files']={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({key:r[key] for key in ['passed','compile_exit','compile_output','test_exit','test_output','independent_mutations_rejected'] if key in r},indent=2));assert r['passed']
