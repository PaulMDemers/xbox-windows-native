"""Link the already tested i386 object once; no console image or launch."""
import hashlib,json,os,subprocess,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn652/linked001')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'linked001.json').exists()
r=dict(passed=False,physical_access=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'linked001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 h=json.loads((K/'host001.json').read_text());assert h['status']=='passed'
 p=Path('/mnt/c/xwn652/host001/receipt-i386.o')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h['artifacts'][p.name]['sha256']
 O.mkdir(parents=True)
 for name,args in [('link',['ld','-m','elf_i386','-Ttext=0x100000','-e','xwn652_store',str(p),'-o',str(O/'receipt.elf')]),('binary',['objcopy','-O','binary',str(O/'receipt.elf'),str(O/'receipt.bin')]),('symbols',['nm','-n',str(O/'receipt.elf')])]:
  x=subprocess.run(args,capture_output=True,timeout=30)
  (O/(name+'.stdout')).write_bytes(x.stdout);(O/(name+'.stderr')).write_bytes(x.stderr)
  assert x.returncode==0 and not x.stderr,(name,x.returncode)
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.iterdir()}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'])))
