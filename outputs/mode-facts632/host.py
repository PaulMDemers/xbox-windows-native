"""Fresh bounded host proof. Modeled memory is never claimed as captured4034."""
import datetime,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
P=Path('/mnt/c/xwn632/host001');assert not P.exists();P.mkdir(parents=True)
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
space=require_space(P,minimum_gib=20.02)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,emulator_launched=False,space=space,checks=0,modeled_digest_is_not_native_proof=True)
def save():(K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
assert not (K/'host001.json').exists();save()
try:
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 for n in ('host.c','facts.h','sha256.h','known.h','memory.h'):(P/n).write_bytes((K/n).read_bytes())
 r['sources']={n:sha(P/n) for n in ('host.c','facts.h','sha256.h','known.h','memory.h')}
 for label,flags in [('native',[]),('modeled',['-DDIGEST_MODEL'])]:
  args=[str(cc),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-pie','-no-pie',*flags,str(P/'host.c'),'-o',str(P/label)]
  x=subprocess.run(args,capture_output=True,timeout=40);(P/(label+'-compile.log')).write_bytes(x.stdout+x.stderr);assert x.returncode==0,(x.stdout+x.stderr).decode()
  r.setdefault('binaries',{})[label]=sha(P/label)
 def run(exe,args,data=b''):
  x=subprocess.run([str(P/exe),*args],input=data,capture_output=True,timeout=10)
  assert x.returncode==0,(x.returncode,x.stderr.decode());assert not x.stderr,x.stderr
  r['checks']+=1;return x.stdout.decode()
 for n in (0,3,55,56,63,64,65,1181,4096):
  data=bytes((i*73+19)&255 for i in range(n));assert run('native',['sha'],data).strip()==hashlib.sha256(data).hexdigest()
 assert run('native',['range']).strip()=='range11'
 f=json.loads((K.parent/'hd-profile310/profile-facts.json').read_text());image=bytearray(623712)
 image[:2]=b'MZ';struct.pack_into('<I',image,0x3c,0x80);struct.pack_into('<I',image,0x80,0x4550)
 struct.pack_into('<H',image,0x84,0x14c);struct.pack_into('<I',image,0x88,1004048809)
 struct.pack_into('<H',image,0x98,0x10b);struct.pack_into('<I',image,0x98+56,623712)
 image[0x3410:0x3432]=bytes(f['crtc_indices'][:34]);struct.pack_into('<26I',image,0x2c58,*f['mmio_offsets'][:26]);image[0x3654:0x3661]=bytes(f['encoder_indices'][:13])
 for code,p in zip((0x880b0a02,0x880e0c03),f['profiles']):
  ci=(code>>8)&255;mi=(code>>16)&255;ei=code&15
  image[0x3410+34*ci:0x3410+34*(ci+1)]=bytes(p['crtc'][:34])
  struct.pack_into('<26I',image,0x2c58+104*mi,*p['mmio'][:26]);struct.pack_into('<I',image,0x2c08+4*mi,p['mmio'][26])
  image[0x3654+13*ei:0x3654+13*(ei+1)]=bytes(p['encoder'][:13])
 # Low-mode raw synthetic zero rows exercise pitch overrides; NOT4034 facts.
 result=run('modeled',['facts','0','4034'],image);assert result.startswith('error=0 reads=17\n')
 groups={'CR':{},'MM':{},'EN':{}}
 for line in result.splitlines()[1:]:g,i,v=line.split();groups[g][int(i)]=int(v)
 assert groups['CR'][19]==0x68 and groups['CR'][25]==0x20 and groups['CR'][34]==0x83
 assert groups['MM'][27]==0x100030 and groups['EN'][13]==0x28
 for at in range(1,18):assert run('modeled',['facts',str(at),'4034'],image).startswith(f'error=2 reads={at}\n')
 assert run('native',['facts','0','4034'],image).startswith('error=4 reads=2\n')
 assert run('native',['facts','0','4627'],image).startswith('error=1 reads=0\n')
 for offset in (0,0x3c,0x80,0x84,0x88,0x98,0x98+56):
  bad=bytearray(image);bad[offset]^=1;assert run('native',['facts','0','4034'],bad).startswith('error=3 ')
 mutations=0
 for start,n,error in [(0x3410,34,5),(0x2c58,104,5),(0x3654,13,5),(0x2c58+104*11,104,6),(0x3654+26,13,6)]:
  for offset in range(start,start+n):
   bad=bytearray(image);bad[offset]^=1;assert run('modeled',['facts','0','4034'],bad).startswith(f'error={error} '),(offset,error);mutations+=1
 r.update(passed=True,range_assertions=11,digest_vectors=9,modeled_byte_mutations_rejected=mutations,native_wrong_kernel_reads=0,native_synthetic_setter_rejected=True,all_refusals_preserve_output=True,compiled_xbe=False)
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({n:r[n] for n in ('passed','checks','modeled_byte_mutations_rejected')}))
