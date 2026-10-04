"""Read-only allocation, immutable binary and registry audit of the F: fixture."""
import argparse,pathlib,sys,subprocess,struct,json,hashlib,os
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-extended-storage'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--run');g.add_argument('--fixture',choices=['windows2000-f-001','windows2000-f-write-001','windows2000-f-reboot-001']);p.add_argument('--probe-version',choices=['1','2'],default='1');p.add_argument('--video-miniport',type=pathlib.Path,help='Explicit replacement miniport whose hash must match the audited fixture');p.add_argument('--video-trace-output',type=pathlib.Path,help='Extract an existing bounded trace to a new local file');a=p.parse_args()
if a.run:
 assert a.run.startswith(('nt5-extended-f-','nt5-physical-f-')) and a.run.replace('-','').isalnum()
 run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists();source=run/'hdd.qcow2'
else:a.run=a.fixture;source=k/'artifacts'/(a.fixture+'.qcow2')
raw=root/'fixtures'/('audit-'+a.run+'.raw');assert not raw.exists()
manifest=json.loads((k/'fixture-001.json').read_text());expected={v['path'].lower():v for v in manifest['files']}
if a.video_miniport:
 assert a.video_miniport.is_file()
 expected['/winnt/system32/drivers/xboxvnt5.sys']=dict(expected['/winnt/system32/drivers/xboxvnt5.sys'],sha256=hashlib.sha256(a.video_miniport.read_bytes()).hexdigest())
extensions={'.exe','.dll','.sys','.nls','.fon','.ttf','.cpl','.ocx'}
r={'run':a.run,'scope':'Read-only F: cold audit; no physical access','directories':0,'files':0,'immutable_files_checked':0,'errors':[],'hives':[]}
if a.video_miniport:r['expected_video_miniport_sha256']=expected['/winnt/system32/drivers/xboxvnt5.sys']['sha256']
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'));owners={};found=set()
  def claim(cluster,path):
   chain=list(w.chain(cluster))
   for c in chain:
    assert c not in owners,('crosslink',c,path,owners.get(c));owners[c]=path
   return chain
  def walk(cluster,path):
   r['directories']+=1
   if not cluster:return # FATX permits an empty directory without an allocated cluster.
   claim(cluster,path)
   for name,(_,_,e) in w.directory(cluster)['entries'].items():
    full=path.rstrip('/')+'/'+name;start,size=struct.unpack_from('<II',e,44)
    if e[1]&16:walk(start,full);continue
    found.add(full);r['files']+=1;chain=claim(start,full) if start else [];assert len(chain)*w.p.cluster_size>=size
    if full in expected and pathlib.PurePosixPath(full).suffix in extensions:
     assert hashlib.sha256(w.read(full)).hexdigest()==expected[full]['sha256'],('binary mismatch',full)
     r['immutable_files_checked']+=1
  walk(1,'/')
  if a.video_trace_output:
   trace=w.read('/winnt/system32/xwn-video-trace.bin')
   assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
   assert 0 < struct.unpack_from('<I',trace,16)[0] <= 254
   with a.video_trace_output.open('xb') as target:target.write(trace)
   r['video_trace_sha256']=hashlib.sha256(trace).hexdigest()
  if a.run.startswith('nt5-physical-f-'):
   log=w.read('/xwn-report-v2.txt' if a.probe_version=='2' else '/xwn-physical.log');data=w.read('/xwn-create-v2.bin' if a.probe_version=='2' else '/xwn-physical-write.bin')
   assert (b'XWN-V2-PASS\r\n' if a.probe_version=='2' else b'XWN-PHYSICAL-PASS\r\n') in log and b'Failures: 0\r\n' in log
   if a.probe_version=='2':assert len(log)==4096 and log.startswith(b'XWN-V2-STARTED\r\n')
   assert data==bytes(((i*37+(i>>8)+0x5a)&255)^0xa5 for i in range(65537))
   r['native_probe']={'log':log.decode('ascii'),'log_sha256':hashlib.sha256(log).hexdigest(),'payload_sha256':hashlib.sha256(data).hexdigest(),'payload_bytes':len(data),'passed':True}
  r['investigated_cluster_owners']={str(c):owners.get(c) for c in [16569,16571,16575]}
  wanted={path for path in expected if pathlib.PurePosixPath(path).suffix in extensions}
  assert wanted<=found,('missing binaries',sorted(wanted-found))
  orphans=[c for c in range(1,w.limit) if w.fat[c] and c not in owners]
  if orphans:r['errors'].append('Unclaimed allocations: '+str(orphans[:20]))
  r['unclaimed_details']=[{'cluster':c,'fat_value':hex(w.fat[c]),'first_four_bytes':w.read_cluster(c)[:4].hex()} for c in orphans[:20]]
  r['orphan_directory_records']=[]
  r['references_to_orphans']=[]
  for c in list(w.dirs)+orphans[:20]:
   for dc in w.chain(c):
    data=w.read_cluster(dc)
    for off in range(0,len(data),64):
     e=data[off:off+64];start,size=struct.unpack_from('<II',e,44)
     if start in orphans or (c in orphans and 1<=e[0]<=42 and off<512):
      record={'directory_cluster':c,'data_cluster':dc,'directory_owner':owners.get(c),'chain':list(w.chain(c)),'offset':off,'marker':e[0],'attributes':e[1],'name_bytes':e[2:44].hex(),'cluster':start,'size':size,'first_end_marker':next((o for o in range(0,len(data),64) if data[o] in (0,255)),None)}
      r['references_to_orphans' if start in orphans else 'orphan_directory_records'].append(record)
  r['allocated_clusters']=len(owners);r['unclaimed_allocations']=len(orphans)
  paths={'/winnt/system32/config/'+n for n in ['system','software','sam','security','default']}
  paths.update(p for p in found if pathlib.PurePosixPath(p).name in ('ntuser.dat','usrclass.dat'))
  for path in sorted(paths):
   data=w.read(path);assert len(data)>=4096 and data[:4]==b'regf';first,second=struct.unpack_from('<II',data,4);assert first==second
   checksum=0
   for value in struct.unpack_from('<127I',data):checksum^=value
   checksum=0xfffffffe if checksum==0xffffffff else checksum or 1
   assert checksum==struct.unpack_from('<I',data,508)[0]
   hive=raw.with_suffix('.hive');hive.write_bytes(data)
   env=dict(os.environ,LD_LIBRARY_PATH=str(root/'toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu'))
   try:tree=json.loads(subprocess.check_output(['python3',str(ws/'outputs/native-windows-fatx-paging/audit-hive.py'),str(hive)],env=env))
   finally:hive.unlink(missing_ok=True)
   r['hives'].append({'path':path,'matching_sequences':True,'checksum_valid':True,'tree':tree})
  r['passed']=not r['errors']
except Exception as e:r['errors'].append(repr(e));r['passed']=False
finally:raw.unlink(missing_ok=True);(k/(a.run+'-cold-audit.json')).write_text(json.dumps(r,indent=2)+'\n')
print({n:r[n] for n in ['run','files','immutable_files_checked','errors','passed']});sys.exit(0 if r['passed'] else 1)
