"""Pin build005 and compare extracted guest source with an independent oracle."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
import oracle
k=Path(__file__).resolve().parent;out=Path('E:/xwn271/oracle003');out.mkdir(exist_ok=False)
b=json.loads((k/'build005.json').read_text());source=(Path(b['path'])/'input/main.c').read_text()
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha((k/'native/main.c').read_bytes())==b['source']['main.c']
def function(name):
    m=re.search(r'(?m)^static (?:uint32_t|unsigned char) '+name+r'\([^)]*\)\s*\{',source);assert m
    n=m.end();depth=1
    while depth:depth+=(source[n]=='{')-(source[n]=='}');n+=1
    return source[m.start():n]
code='#include <stdint.h>\n#include <stdio.h>\n#define W 16u\n#define H 8u\n#define PAYLOAD 256u\n'
code+='\n'.join(function(n) for n in ['texel','expected_byte'])
code+='\nint main(void){for(unsigned u=0;u<4;u++)for(unsigned n=0;n<4096;n++)putchar(expected_byte(u,n));return 0;}\n'
(out/'test.c').write_text(code)
for n in ['oracle.py','test-oracle.py']:(out/n).write_bytes((k/n).read_bytes())
base='/mnt/e/xwn271/oracle003'
c=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
r=dict(compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'),guest_executed=False,real_gl=False)
assert not c.returncode,r
t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
r.update(test_exit=t.returncode,test_errors=t.stderr.decode(errors='replace'));assert not t.returncode and not t.stderr
expected=b''.join(oracle.blocks());assert t.stdout==expected
r['exact_source_and_guard_bytes']=len(expected)
h=[0]*43;h[:6]=[0x58323731,271,1612,22,0,0x271c0de]
for u in range(4):
    h[6+u]=0x80100000+u*4096;h[10+u]=0x100000+u*4096;h[14+u]=h[6+u]+256;h[18+u]=h[10+u]+256
h[22:27]=[16,8,64,4096,256];h[27:34]=[0x80200000,0x200000,2560,480,0x80110000,384,0x110000]
h[34:39]=[3,1,2,3,0]
good=struct.pack('<43I',*h)+oracle.framebuffer()*2
assert oracle.validate_record(good)
negative=0
# Every independently expected framebuffer/guard byte must be checked.
for pos in range(172,1612):
    bad=bytearray(good);bad[pos]^=1
    try:oracle.validate_record(bad)
    except AssertionError:negative+=1
    else:raise AssertionError(('accepted changed pixel',pos))
for field,value in [(0,0),(1,270),(2,0),(4,1),(22,17),(24,128),(29,4),(30,0),(32,24),(34,2),(35,10001),(39,1),(42,1),(10,h[11]),(18,0),(33,h[10])]:
    bad=bytearray(good);struct.pack_into('<I',bad,field*4,value)
    try:oracle.validate_record(bad)
    except AssertionError:negative+=1
    else:raise AssertionError(('accepted metadata mutation',field))
r.update(passed=True,synthetic_negative_controls=negative,expected_framebuffer_bytes=len(oracle.framebuffer()),
         texture_sha256=[sha(v) for v in oracle.textures()],guarded_blocks_sha256=[sha(v) for v in oracle.blocks()],framebuffer_sha256=sha(oracle.framebuffer()),
         extracted_functions_sha256={n:sha(function(n).encode()) for n in ['texel','expected_byte']},
         files={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()})
dest=k/'oracle-tests003.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
