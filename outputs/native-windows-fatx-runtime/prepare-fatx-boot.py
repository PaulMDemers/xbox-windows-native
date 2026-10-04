"""Stage an experimental Windows tree on a private FATX emulator disk.

No physical device support. Original Windows and dashboard images stay intact.
Unsupported FATX component names are explicitly reported, not silently renamed.
"""
import hashlib,json,os,pathlib,re,shutil,struct,subprocess,sys,time
root=pathlib.Path('/home/paul/xbox-windows-native')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=ws/'outputs/native-windows-fatx-runtime';runtime=root/'toolchains/offline-disk/root'
sys.path[:0]=[str(out),str(runtime/'usr/lib/python3/dist-packages'),str(ws/'outputs/native-windows-nt5-kernel'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import hivex,fatx_stage_boot as fatx
from nt5_hive_indexes import normalize
from bulk_fatx import Writer
source=ws/'work/unleashx-ftp-fixture.qcow2'
ntfs=root/'fixtures/fatx-fullboot-input/windows.ntfs'
target=out/'artifacts/windows2000-fatx-boot-001.qcow2'
temp=root/'fixtures/fatx-boot-001'
assert not target.exists() and not temp.exists() and ntfs.is_file();temp.mkdir()
env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def cat(path):return subprocess.check_output([str(runtime/'usr/bin/ntfscat'),'-f',str(ntfs),path],env=env)
def node(h,path,create=False):
 at=h.root()
 for part in path.split('\\'):
  child=h.node_get_child(at,part)
  if not child and create:child=h.node_add_child(at,part)
  assert child,path;at=child
 return at
def setval(h,n,key,kind,data):h.node_set_value(n,{'key':key,'t':kind,'value':data})
record={'scope':'Private native-FATX boot experiment; unsupported long/non-ASCII names omitted and recorded. No hardware writes.','source_dashboard_sha256':sha(source),'source_ntfs_sha256':sha(ntfs),'files':[],'omitted':[]}
try:
 hive=temp/'SYSTEM';original=cat('/WINNT/system32/config/system');hive.write_bytes(original)
 h=hivex.Hivex(str(hive),write=True)
 for child in h.node_children(h.root()):
  name=h.node_name(child)
  if not re.fullmatch('ControlSet[0-9]{3}',name):continue
  service=node(h,name+'\\Services\\XwnFatx',True)
  for key,value in [('Type',2),('Start',0),('ErrorControl',1)]:setval(h,service,key,4,struct.pack('<I',value))
  for key,value,kind in [('ImagePath','system32\\drivers\\xwnfatx.sys',2),('Group','Boot File System',1),('DisplayName','XWN FATX filesystem experiment',1)]:setval(h,service,key,kind,(value+'\0').encode('utf-16le'))
 mounted=node(h,'MountedDevices');old=None
 for v in h.node_values(mounted):
  if h.value_key(v)=='\\DosDevices\\C:':old=h.value_value(v)[1]
 assert old and len(old)==12
 new=struct.pack('<IQ',0xaa55,0x55f400*512);changed=[]
 mounted_values=[(h.value_key(v),*h.value_value(v)) for v in h.node_values(mounted)]
 for key,kind,data in mounted_values:
  if data==old:setval(h,mounted,key,kind,new);changed.append(key)
 assert '\\DosDevices\\C:' in changed
 h.commit(str(hive));del h
 fixed,conversion=normalize(hive.read_bytes());hive.write_bytes(fixed)
 record['hive']={'original_sha256':hashlib.sha256(original).hexdigest(),'result_sha256':sha(hive),'mounted_devices_updated':changed,'normalization':conversion,'xwnfatx_start':0}
 raw=temp/'disk.raw';subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 inventory=json.loads((ws/'work/fullboot-file-inventory.json').read_text())
 def allowed(path):
  return path.isascii() and all(len(c)<=42 and c not in ('.','..') for c in path.strip('/').split('/'))
 overrides={'/WINNT/system32/config/system':fixed,
  '/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd':b'@echo off\r\nC:\\xwncheck.exe\r\nnotepad C:\\xwn-check.log\r\n'}
 with raw.open('r+b') as fp:
  assert fp.read(512)==bytes(512),'Expected untouched Xbox sector zero'
  part=fatx.open_partition(fp,raw,'E');w=Writer(fp,part)
  for path in inventory['directories']:
   if path=='/':continue
   if allowed(path):w.mkdir(path)
   else:record['omitted'].append({'path':path,'reason':'FATX component representation','directory':True})
  for item in inventory['files']:
   path=item['path']
   if path.rsplit('/',1)[-1] in ('.','..'):continue
   if path.lower() in ('/pagefile.sys','/hiberfil.sys'):
    record['omitted'].append({'path':path,'reason':'Regenerated runtime paging/hibernation file'});continue
   if not allowed(path):record['omitted'].append({'path':path,'reason':'FATX component representation'});continue
   data=overrides.get(path)
   if data is None:data=cat(path);assert len(data)==item['bytes'],path
   record['files'].append(w.write(path,data))
   if len(record['files'])%250==0:
    w.flush();print('Staged',len(record['files']),flush=True)
  record['files'].append(w.write('/WINNT/system32/drivers/xwnfatx.sys',(out/'artifacts/xwnfatx.sys').read_bytes()))
  w.flush();cold=Writer(fp,part)
  for item in record['files']:
   data=cold.read(item['path']);assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
  record['cold_readback_verified']=len(record['files'])
  fp.seek(0);assert fp.read(512)==bytes(512)
 subprocess.run(['qemu-img','convert','-O','qcow2',str(raw),str(target)],check=True)
 record['check']=subprocess.check_output(['qemu-img','check',str(target)],text=True)
 record['disk_sha256']=sha(target);assert sha(source)==record['source_dashboard_sha256'];assert sha(ntfs)==record['source_ntfs_sha256'];record['inputs_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp)
 record['temporary_raw_removed']=True;(out/'fatx-boot-disk-001.json').write_text(json.dumps(record,indent=2)+'\n')
print('FATX boot fixture staged',record.get('cold_readback_verified'),len(record['omitted']))
