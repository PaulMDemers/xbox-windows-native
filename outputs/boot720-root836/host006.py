"""Build and exercise a fresh RAM-copy bridge; no console access."""
import ctypes as C,datetime,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn836/host006')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
r={'passed':False,'space':require_space(O,20.1),'physical_access':False,'commands':[]};O.mkdir(parents=True)
def run(args):
 r['commands'].append([str(a) for a in args]);v=subprocess.run(args,capture_output=True,timeout=90)
 with (O/'build.log').open('ab') as f:f.write(v.stdout+v.stderr)
 assert v.returncode==0,(args,v.stderr.decode());return v.stdout
try:
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4';r['compiler_sha256']=sha(cc)
 firmware=Path('/mnt/c/xwn836/chain002/image-crom.bin');b=json.loads((K/'chain002.json').read_text());assert b['passed'];assert sha(firmware)==b['artifacts']['image-crom.bin']['sha256'];raw=firmware.read_bytes();assert 4096<=len(raw)<=0xf0000 and len(raw)%4==0
 r['firmware']={'sha256':sha(firmware),'bytes':len(raw),'source_only_reuse':True}
 run(['as','--32',str(K/'bridge.S'),'-o',str(O/'bridge.o')]);run(['ld','-m','elf_i386','-Ttext=0','--entry=bridge_start',str(O/'bridge.o'),'-o',str(O/'bridge.elf')]);run(['objcopy','-O','binary','--only-section=.text',str(O/'bridge.elf'),str(O/'bridge.bin')])
 nm=run(['nm','-n',str(O/'bridge.elf')]).decode();(O/'symbols.txt').write_text(nm)
 sy={a[2]:int(a[0],16) for l in nm.splitlines() if len(a:=l.split())==3};r['bridge_symbols']=sy
 code=(O/'bridge.bin').read_bytes();assert len(code)==2304 and sy['bridge_code_end']<=0x800
 meta=[sy['bridge_code_end'],sy['bridge_flat'],sy['bridge_fault'],sy['bridge_post']]
 run([str(cc),'-shared','-fPIC','-O1','-Wall','-Wextra','-Werror','-fsanitize=undefined',str(K/'page.c'),'-o',str(O/'page.so')])
 run([str(cc),'-shared','-fPIC','-O1','-Wall','-Wextra','-Werror','-fsanitize=undefined',str(K/'plan.c'),'-o',str(O/'plan.so')])
 # Source-only reuse of established allocation and complete alias ownership tests.
 run(['python3','-B',str(K/'plan_test.py'),str(O)])
 lib=C.CDLL(str(O/'page.so'));f=lib.page829;f.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p]+[C.c_uint32]*5;f.restype=C.c_int
 cm=(C.c_uint32*4)(*meta);cb=C.create_string_buffer(code);count=0
 def page(base,fb,source,size,checksum,ok=True):
  global count
  buf=C.create_string_buffer(b'\x5a'*40960,40960);ret=f(buf,cb,cm,base,fb,source,size,checksum);count+=1
  assert bool(ret)==ok
  if not ok:assert buf.raw==b'\x5a'*40960
  return buf.raw
 size=len(raw);checksum=sum(struct.unpack('<%dI'%(size//4),raw))&0xffffffff
 for base in [0x1000000,0x1ef0000,0x1ed8000,0x1ff6000]:
  for fb in [0x2800000,0x3000000,0x4000000-3686400]:
   data=page(base,fb,0x410000,size,checksum)
   assert struct.unpack_from('<III',data,0x858)==(0x410000,size,checksum)
   assert sum(struct.unpack_from('<I',data,i)[0] for i in range(0,0x8f00,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff==struct.unpack_from('<I',data,0x854)[0]
 for i,values in enumerate([[0,0xffffff,0x1000001,0x1ff7000,0xffffffff],[0x1f9a200,0x27ff000,0x3fff000,0xffffffff],[0,0x20ffff,0x410001,0x1ef0000,0x1ef1000,0xffffffff],[0,1,4095,4097,0xf0004,0xffffffff]]):
  for value in values:
   args=[0x1ef0000,0x3000000,0x410000,size,checksum];args[i]=value;page(*args,ok=False)
 synthetic=b'\xfa\xf4\xeb\xfd'+bytes((i*37+11)&255 for i in range(size-4));(O/'synthetic.bin').write_bytes(synthetic)
 synsum=sum(struct.unpack('<%dI'%(size//4),synthetic))&0xffffffff
 for name,base in [('dual',0x1ef0000),('identity',0x1ef0000),('relocated',0x1ed8000),('scatter',0x1ef0000)]:
  d=O/name;d.mkdir();(d/'page.bin').write_bytes(page(base,0x3000000,0x410000,size,synsum))
 header='#include <stdint.h>\nstatic const uint32_t bridge_meta[4]={'+','.join(hex(v) for v in meta)+'};\nstatic const uint32_t firmware_sum='+hex(checksum)+';\n'
 for symbol,data in [('bridge_image',code),('firmware_image',raw)]:header+='static const uint8_t '+symbol+'['+str(len(data))+']={'+','.join(hex(v) for v in data)+'};\n'
 (O/'embed.h').write_text(header);r['page_cases']=count;r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['sources']={p.name:sha(p) for p in K.iterdir() if p.suffix in ('.c','.h','.S','.py')};r['files']={str(p.relative_to(O)):sha(p) for p in O.rglob('*') if p.is_file()};r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(K/'host006.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS bridge build and page tests',r.get('page_cases'))
