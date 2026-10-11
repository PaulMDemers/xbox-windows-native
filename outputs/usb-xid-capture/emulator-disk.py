"""Stage only E: offline, then independently read cold native capture evidence."""
import hashlib,importlib,importlib.util,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1];mode,case=sys.argv[1:]
run=repo/('work/runs/xid-'+case);disk=run/'hdd.qcow2'
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof')]
m=importlib.import_module('prepare-fixture');from coldio import ColdIO
m.target=disk;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
sha=lambda b:hashlib.sha256(b).hexdigest()
relative='Applications/XWNXid'+case+'/default.xbe'
def maps():
 rows=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(disk)]))
 return [r for r in rows if r.get('depth')==0 and r.get('present') and r['start']+r['length']>15633072*512]
if mode=='stage':
 assert not (run/'stage.json').exists()
 class OnlyE(m.SliceIO):
  def write(self,data):
   start,size=m.fatx.PARTITIONS['E'];assert start<=self.pos and self.pos+len(data)<=start+size
   return super().write(data)
 io=OnlyE(disk);w=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
 data=(k/'artifacts/build003/bin/default.xbe').read_bytes();assert sha(data)==json.loads((k/'build003-review.json').read_text())['xbe_sha256']
 w.write(relative,data);w.flush();assert w.read(relative)==data;assert not maps()
 (run/'stage.json').write_text(json.dumps(dict(physical_access=False,only_E_writes=True,binary_sha256=sha(data),path='E/'+relative),indent=2)+'\n')
 print('E-only emulator staging verified')
elif mode=='audit':
 assert (run/'cleanup.json').exists() and not (k/(case+'-review.json')).exists()
 observed=json.loads((run/'observe.json').read_text());assert observed['dashboard_returned']
 fixed=json.loads((k.parent/'usb-identification207/fixture-emu001.json').read_text())['files']
 exact={}
 with ColdIO(disk) as io:
  writers={v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
  data=writers['E'].read(relative.rsplit('/',1)[0]+'/xid.log');(run/'xid.log').write_bytes(data)
  for path,digest in fixed.items():
   volume,pathpart=path.split('/',1);exact[path]=sha(writers[volume].read(pathpart))==digest
  assert all(exact.values())
  assert sha(writers['E'].read(relative))==observed['binary_sha256']
 spec=importlib.util.spec_from_file_location('native_parser',k/'analyze.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
 parsed=parser.parse(data);(run/'decoded.json').write_text(json.dumps(parsed,indent=2)+'\n')
 extents=maps();r=dict(case=case,physical_access=False,passed=parsed['native_capture_passed'] and not extents and all(exact.values()),reports=len(parsed['reports']),distinct_reports=parsed['distinct_reports'],device=parsed.get('device'),xid=parsed.get('xid'),issues=parsed['issues'],top_overlay_F_extents=extents,baseline_files_exact=exact,dashboard_returned=True,log_sha256=sha(data),binary_sha256=observed['binary_sha256'],windows_input_qualified=False)
 (k/(case+'-review.json')).write_text(json.dumps(r,indent=2)+'\n')
 assert r['passed'],'Preserve failed native run'
 (k/'emulator-review.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({n:r[n] for n in ['passed','reports','distinct_reports','device','xid']}))
else:raise ValueError(mode)
