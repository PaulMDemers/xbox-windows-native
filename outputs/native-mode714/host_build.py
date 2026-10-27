"""Fresh host construction of714; no nxdk/XBE/physical admission yet."""
import sys,os,json,hashlib,subprocess,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn714/host001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'physical_access':False,'space':require_space(O,20.15),'commands':[]}
O.mkdir(parents=True)
def run(cmd):
 r['commands'].append([str(v) for v in cmd]);p=subprocess.run(cmd,capture_output=True,timeout=90)
 with (O/'build.log').open('ab') as f:f.write(p.stdout+p.stderr)
 assert p.returncode==0,(cmd,p.stderr.decode());return p.stdout
try:
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc)
 payload=Path('/mnt/c/xwn714/payload001/payload.bin')
 meta=json.loads((K/'payload001.json').read_text());assert meta['passed']
 for n,h in meta['files'].items():assert sha(payload.parent/n)==h
 for n,h in meta['sources'].items():assert sha(K/n)==h
 r['payload_inputs']={str(p):sha(p) for p in [payload,payload.parent/'symbols.stdout',payload.parent/'relocations.stdout']}
 (O/'payload.bin').write_bytes(payload.read_bytes())
 # Reuse the reviewed parser as a retained source input, not a closed runtime.
 #714 parser preserves internal relocation validation, with the new17-entry count.
 sys.path.insert(0,str(K));from relocate import entries
 rows=entries((payload.parent/'relocations.stdout').read_text(),payload.read_bytes())
 absolute=[v for v in rows if v['type']=='R_386_32'];assert len(absolute)==4
 run(['as','--32',str(K/'bridge.S'),'-o',str(O/'bridge.o')])
 run(['ld','-m','elf_i386','-Ttext=0','--entry=bridge_start',str(O/'bridge.o'),'-o',str(O/'bridge.elf')])
 run(['objcopy','-O','binary','--only-section=.text',str(O/'bridge.elf'),str(O/'bridge.bin')])
 nm=run(['nm','-n',str(O/'bridge.elf')]).decode();(O/'bridge-symbols.txt').write_text(nm)
 sy={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
 ps={a[2]:int(a[0],16) for line in (payload.parent/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
 assert sy['bridge_code_end']<=0x800 and len((O/'bridge.bin').read_bytes())==4096
 m=[sy['bridge_code_end'],sy['bridge_flat'],sy['bridge_fault'],sy['bridge_post'],ps['native_transaction704']-0x100000]
 hdr='static const uint32_t bridge_meta[5]={'+','.join(hex(v) for v in m)+'};\n'
 hdr+='static const struct reloc705 payload_reloc[4]={'+','.join('{'+hex(v['offset'])+','+hex(v['value'])+'}' for v in absolute)+'};\n'
 (O/'payload_meta.h').write_text(hdr);r['bridge_symbols']=sy;r['metadata']=m;r['relocations']=rows
 run([str(cc),'-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(O),str(K/'page002.c'),str(K/'page_tool.c'),'-o',str(O/'page-tool')])
 run([str(cc),'-std=c11','-O1','-Wall','-Wextra','-Werror','-shared','-fPIC','-fsanitize=undefined',str(K/'plan.c'),'-o',str(O/'plan.so')])
 run(['python3','-B',str(K/'plan_test.py'),str(O)])
 for name,base in [('dual',0x1ef0000),('identity',0x1ef0000),('relocated',0x1ed8000),('scatter',0x1ef0000)]:
  d=O/name;d.mkdir();run([str(O/'page-tool'),str(O/'bridge.bin'),str(O/'payload.bin'),str(d/'page.bin'),str(base),str(0x3000000)])
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['sources']={p.name:sha(p) for p in K.iterdir() if p.is_file() and p.suffix in ('.c','.h','.S','.py')}
 r['files']={str(p.relative_to(O)):sha(p) for p in O.rglob('*') if p.is_file()}
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS fresh bridge/page construction and ownership tests; no XBE')
